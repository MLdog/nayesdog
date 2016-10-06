import feedparser
import os
#from collections import OrderedDict

from doglib import feed_to_md_file, process_an_entry

# ML

path = '/home/ilya/feeds/'
files = list(filter(lambda s: s[0] != '.', os.listdir(path)))
fname = files[0]
fullpath = os.path.join(path, fname)

#d = feedparser.parse('http://feeds.arstechnica.com/arstechnica/index?format=xml')

d = feedparser.parse(fullpath)

print(d['feed']['title'])

# load simplified entries
entries = list(map(process_an_entry, d['entries']))

# throw away timestamps and ids
for e in entries:
    e.pop('timestamp')
    e.pop('id')

# title and text are combined
txts = list(map(
                lambda e: sum(e.values(), [])
                ,
                entries
               )
           )
#labels = # load from some where


