# NayesDog
RSS/Web news reader with Naive Bayes powered recommendations

---
- doglib.py is preprocessing lib.
- naylib.py is ML lib.
- facelib.py is web interface lib.

---

## Dependencies:
[feedparser](https://pypi.python.org/pypi/feedparser) for RSS
[beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4) for web scraping

## Installation:
To install latest release (pip of python2.7, pip2 on my system):

``` {.sh}
pip2 install nayesdog
```

To install development version:

``` {.sh}
pip2 install git+https://github.com/MLdog/nayesdog
```

## Usage:
+ To run `nayesdog` you only need to run `nayesdog` in a terminal
* Default config files are stored in `~/.nayesdog`
	+ `config.py`: configuration file.  Modify this file to include new RSS feeds or web scrap news, or remove the existing ones.
	+ `tables.py.gz`: Trained model, containing the word counts that are used by the Naive Bayes Classifier. You can copy your model, use it somewhere else and share it.
	+ `.previous_session`: A hidden file that stores the state of your session. If you have problems, try to erase this file.
+ By running `nayesdog` with `--config` option you can have different nayesdogs trained for different purposes and different RSS feeds.

Example configuration can be found at <https://github.com/iprokin/dotfiles/tree/master/.nayesdog>.

## Python library:
You can import the `nayesdog` library into python2.7 projects with `import nayesdog`

# To-do
* Each time nayesdog is run, preprocess_html loads all urls even they were previously loaded. This unnecessary work and resulting delays should be avoided.
* Add UI toggle for showing titles only / full content / summarized content
* Save the last feed open and the last folder open
* Upload last version Pypi
* Parse HTML (One more dependency)
* Summarization: https://github.com/neopunisher/Open-Text-Summarizer
* Topic modeling and word search according to topic distance and likability
* Visual search of documents ordered by topics
* Test and spot bugs
* replace shelves for cross-compatibility (?)
* being able to enter feed names that contain spaces!
* Move "toggle images" function to config.py instead of having button?
* Should we remove deleted article also from WordCount dict?
