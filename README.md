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
