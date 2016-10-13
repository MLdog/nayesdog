# NayesDog
RSS reader with naive bayes powered recommendations

---

- doglib.py is preprocessing lib.
- naylib.py is ML lib.
- facelib.py is web interface lib.
- feeds2mds.py is script that converts local rss files to markdown documents.
- prep_feeds.sh is script that downloads RSS from *urls* file and renames them with their readable title, and then converts all feeds to markdown.
- urls is file with URLs of feeds.

---

To have local files with feeds:

edit prep_feeds.sh:

``` {.bash}
feeddest=~/feeds
mddest="$feeddest/md"
```

run:
bash prep_feeds.sh

check folders:
~/feeds/ and ~/feeds/md/

## To-do

* Why log and nolog versions of classify_new_one give different results?
* Modify word_counts dict word_counts[0] and word_counts[1] contain the same keys
* wrap transform_feed_dict and update_word_count_tables as one sklearn-like FIT function
* Add any to-do we discussed but didn't put here.
* We can also havo common syncthing folder for extra stuff

