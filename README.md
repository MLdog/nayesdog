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

    ``` {.bash}
    cd OUTPUTFOLDER; bash wgetsitedownloader.sh http://localhost:8081
    ```

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

* Modify word_counts dict word_counts[0] and word_counts[1] contain the same keys
* Add any to-do we discussed but didn't put here.
* Modify predict and classify_new_one_optimized in order to make one method belonging to the class NaiveBayes
* Add a list of pairs [(id_entry, prediction) ] to each feed in "Home". In order to present the feeds ordered by their rank (in face lib.py)
* As soon as we start the program make the classifier predict the user preference on each entry in "Home"
    - sort entries based on P(1|x)-P(0|x)
* Modify the do_GET method in order to present the feeds ordered by their ranks
* Put more explicit names to classify_new_one_optimized (MB we eventually remove it)
* We should check if the function is ok ... I think I wrote exactly the same function you did but we need to be sure (sergio) 
    - seems to be ok with LOG, checkout commits: b1f1933ec8628594860282ca5ad687e8e62c8b69 and 2a1be82869543a349d3bd2ab70944cc849681fdc
