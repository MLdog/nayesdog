import feedparser
import os
from naylib import update_word_count_tables
from doglib import save_object_simple, load_object_simple, load_wt_st


from doglib import feed_to_md_file, process_an_entry, file_to_str,\
rating_from_md_files_in_folder, transform_feed_dict


# ML

path = '/home/ilya/feeds/'

stopwordsfile = './stopwords.txt'

# "databases"
wt_file = './wt.py.gz'
st_file = './st.py.gz'

mdpath=os.path.join(path, 'md')
# insted of obtaining labels all at once from MD files. With web inteface labels and entries
# will be obtained at the same time in the moment user presses a button
# this will give us a new item in d_idstxts and lables at the same time
labels = rating_from_md_files_in_folder(mdpath) # load labels from mdfile

word_counts, sum_dict = load_wt_st(wt_file, st_file)
#print(load_object_simple(wt_file))

stopwords=set(file_to_str(stopwordsfile).split('\n'))

files = list(filter(lambda s: s[0] != '.', os.listdir(path)))
fullpaths = list(map(lambda f: os.path.join(path, f), files))

for fullpath in fullpaths:
    d = feedparser.parse(fullpath)
    d_idstxts = transform_feed_dict(d)
    update_word_count_tables(word_counts, sum_dict, d_idstxts, labels, stopwords)

save_object_simple(wt_file, word_counts)
save_object_simple(st_file, sum_dict)

# test ML
# pick up a feed and pretend its new
newone = list(d_idstxts.values())[0]

for w in newone:
    Py = 
    Px = 
    Pxy = word_counts[label][w]/sum_dict[label]
