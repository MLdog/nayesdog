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
## Installation:

pip install nayesdog

## Execution:

+ Create a directory from which you want to run NayesDog  (e.g., `mkdir News` and `cd News`)
+ Run NayesDog from this directory typing `NayesDog`
+ Modify the user_config.py file to include new RSS feeds or remove the existing ones. The feed names should only contain letters and numbers
+ The file tables.py.gz contains your trained model

## Browsers:
 
+ Works well with Google chrome and safari
+ [Problems with Firefox](https://bugzilla.mozilla.org/show_bug.cgi?id=583211) (It will work soon ;))

## To-do

* Test and spot bugs
* compatibility with firefox
* replace shelves (?)
* being able to enter feed names that contain spaces!
* summarization: https://github.com/neopunisher/Open-Text-Summarizer