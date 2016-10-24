# NayesDog
RSS reader with naive bayes powered recommendations

---

- doglib.py is preprocessing lib.
- naylib.py is ML lib.
- facelib.py is web interface lib.
- feeds2mds.py is script that converts local rss files to markdown documents.
- prep_feeds.sh is script that downloads RSS from *urls* file and renames them with their readable title, and then converts all feeds to markdown.
- urls is file with URLs of feeds.
- wgetsitedownloader.sh is a scrpt to download webisite recursively with wget. To make offline version of html feeds:

---
+ create a directory from which you want to run NayesDog
+ Run NayesDog from this directory
+ Modify the user_config.py file to include new RSS feeds or remove the existing ones
+ The file tables.py.gz contains your trained model


## To-do

* Test and spot bugs
* setup
* replace shelves (?)
* being able to enter feed names that contain spaces!
* summarization: https://github.com/neopunisher/Open-Text-Summarizer