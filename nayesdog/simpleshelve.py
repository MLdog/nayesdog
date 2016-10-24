"""
Nayesdog: RSS reader with naive bayes powered recommendations
Copyright (c) 2016 Ilya Prokin and Sergio Peignier
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public Licensealong with this program.  If not, see <http://www.gnu.org/licenses/>.
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

