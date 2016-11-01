# Nayesdog: RSS reader with naive bayes powered recommendations
# Copyright (c) 2016 Ilya Prokin and Sergio Peignier
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public Licensealong with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
# 
# SimpleShelve is a module included with NayesDog
# 
# A replacement for shelve module (uses pickle+gzip)
# supports any standard python datatype
# 
# Database is simple zip file with clean python code defining object
# 
# Usage example:
#     ``` {.python}
#     s = SimpleShelve('file.py.gz')
#     s['asdasdasdasdasdas'] = 434534534
#     print(s)
#     s.close()
#     ```
#     Output:
#         {'asdasdasdasdasdas': 434534534}
#         stored in
#         file.db

import os
import pickle
import gzip


def save_object_simple(outfilename, obj):
    #with open(outfilename, 'w') as f:
    with gzip.open(outfilename, 'wb') as f:
        pickle.dump(obj, f)


def load_object_simple(filename):
    #with open(filename, 'r') as f:
    with gzip.open(filename, 'rb') as f:
        obj = pickle.load(f)
    return obj


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
        if self.data is None:
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

    def __contains__(self, key):
        return key in self.data

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

