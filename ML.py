import feedparser
import os
from naylib import NaiveBayes
import time

from doglib import feed_to_md_file, process_an_entry, file_to_str,\
rating_from_md_files_in_folder, transform_feed_dict,\
print_sorted, classnamer, dargmax

# ML

path = '/home/ilya/feeds/'
mdpath = os.path.join(path, 'md')
# insted of obtaining labels all at once from MD files. With web inteface labels and entries
# will be obtained at the same time in the moment user presses a button
# this will give us a new item in d_idstxts and lables at the same time
labels = rating_from_md_files_in_folder(mdpath) # load labels from mdfile

files = list(filter(lambda s: s[0] != '.', os.listdir(path)))
fullpaths = list(map(lambda f: os.path.join(path, f), files))

r = NaiveBayes()

for fullpath in fullpaths:
    d = feedparser.parse(fullpath)
    r.fit_from_feed(d, labels)

r.save_tables()


# test ML
# pick up a feed and pretend its new
#newone = list(transform_feed_dict(feedparser.parse('/home/ilya/feeds/Ars_Technica')).values())[0]
newone = list(transform_feed_dict(d).values())[0]

print(newone)
print(len(newone))

# P(y|x) = P(y)P(x1,..,xn|y) / P(x1,..,xn) =
# = P(y) {P(x1|y)*...*P(xn|y)} / {P(x1)*...*P(xn)}

Ps = r.predict(newone)

Pyx = Ps['yx']
k = dargmax(Pyx)
print("You will probably {} it with probability = {}".format(classnamer(k), Pyx[k]))
            
print_sorted(Ps)
