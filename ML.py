import feedparser
import os
from naylib import update_word_count_tables, classify_new_one
from doglib import save_object_simple, load_wt_st


from doglib import feed_to_md_file, process_an_entry, file_to_str,\
rating_from_md_files_in_folder, transform_feed_dict


def dargmax(d, vmax0=-1):
    vmax = vmax0
    for k,v in d.items():
        if v > vmax:
            vmax = v
    return k

def classnamer(k):
    return {0:"dislike", 1:"like"}.get(k, "dont know if you like")


# ML

path = '/home/ilya/feeds/'

stopwordsfile = './stopwords.txt'

# "databases"
db_file = './db.py.gz'

mdpath = os.path.join(path, 'md')
# insted of obtaining labels all at once from MD files. With web inteface labels and entries
# will be obtained at the same time in the moment user presses a button
# this will give us a new item in d_idstxts and lables at the same time
labels = rating_from_md_files_in_folder(mdpath) # load labels from mdfile

word_counts, sum_dict = (lambda x: (x['wt'], x['st']))(load_wt_st(db_file))
#print(load_object_simple(wt_file))

stopwords = set(file_to_str(stopwordsfile).split('\n'))

files = list(filter(lambda s: s[0] != '.', os.listdir(path)))
fullpaths = list(map(lambda f: os.path.join(path, f), files))

for fullpath in fullpaths:
    d = feedparser.parse(fullpath)
    d_idstxts = transform_feed_dict(d)
    update_word_count_tables(word_counts, sum_dict, d_idstxts, labels, stopwords)

save_object_simple(db_file, {'wt': word_counts, 'st': sum_dict})

# test ML
# pick up a feed and pretend its new
newone = list(d_idstxts.values())[0]

# P(y|x) = P(y)P(x1,..,xn|y) / P(x1,..,xn) =
# = P(y) {P(x1|y)*...*P(xn|y)} / {P(x1)*...*P(xn)}

Ps = classify_new_one(word_counts, sum_dict, newone)
Pyx = Ps['yx']
k = dargmax(Pyx)

print("You will probably {} it with probability = {}".format(classnamer(k), Pyx[k]))
print(Ps)
