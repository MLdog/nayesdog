import feedparser
import os
from collections import OrderedDict

from doglib import feed_to_md_file, process_an_entry, file_to_str, rating_from_md_files_in_folder

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
# get ids
ids = [e['id'] for e in entries]

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


labels = rating_from_md_files_in_folder(os.path.join(path, 'md')) # load from some where


d_idstxts = dict(zip(ids, txts))

stopwords = set(file_to_str('./stopwords.txt').split('\n'))

def create_empty_word_count_table():
    return {
        0:OrderedDict(),
        1:OrderedDict()
    }

# init tables
word_counts = create_empty_word_count_table()
sum_dict = {0:0, 1:0}

for k in d_idstxts.keys():
    if k in labels.keys():
        for word in d_idstxts[k]:
            if word not in stopwords:
                if word in word_counts[labels[k]].keys():
                    word_counts[labels[k]][word] += 1
                    sum_dict[labels[k]] += 1
                else:
                    word_counts[labels[k]][word] = 0


