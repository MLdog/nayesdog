"""
SimpleShelve

A hacky replacement for shelve module (uses eval function)
supports OrderedDicts and any standard python datatype

Copyright Ilya Prokin 2016

Database is simple zip file with clean python code defining object

Usage example:
    ``` {.python}
    s = SimpleShelve('file.py.gz')
    s['asdasdasdasdasdas'] = 434534534
    print(s)
    s.close()
    ```
    Output:
        {'asdasdasdasdasdas': 434534534}
        stored in
        file.db
"""

import os
import gzip
from collections import OrderedDict # has to be here even that it is not used in code


# two dumb simple save/load in transparent format
def save_object_simple(outfilename, obj):
    s = repr(obj)
    #with open(outfilename, 'w') as f:
    with gzip.open(outfilename, 'wb') as f:
        f.write(s.encode())


# OrderedDict has to be defined, otherwise EVAL won't load it from file
def load_object_simple(filename):
    #with open(filename, 'r') as f:
    with gzip.open(filename, 'rb') as f:
        s = f.read()
    return eval(s)


class SimpleShelve:

    def __init__(self, db_file, write_on_destroy=False):
        self.filepath = db_file
        self.write_on_destroy = write_on_destroy
        if os.path.isfile(self.filepath):
            self.data = load_object_simple(self.filepath)
        else:
            self.data = dict()

    def sync(self):
        save_object_simple(self.filepath, self.data)

    def close(self, sync=True):
        if self.dict is None:
            return
        try:
            if sync:
                self.sync()
            try:
                self.data.close()
            except AttributeError:
                pass
        finally:
            self.data = None
            self.filepath = None

    def __del__(self):
        self.close(sync=self.write_on_destroy)

    def __getitem__(self, key):
        try:
            value = self.data[key]
        except KeyError:
            pass
        return value

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        try:
            del self.data[key]
        except KeyError:
            pass

    def __repr__(self):
        return "{}\nstored in\n{}".format(self.data, self.filepath)

