# NayesDog
RSS reader with Naive Bayes powered recommendations

---
- doglib.py is preprocessing lib.
- naylib.py is ML lib.
- facelib.py is web interface lib.

---

## Dependencies:
[feedparser](https://pypi.python.org/pypi/feedparser)

## Installation:
To install latest release:

``` {.sh}
pip install nayesdog
```

To install development version:

``` {.sh}
pip install git+https://github.com/MLdog/nayesdog
```

## Usage:
+ To run `nayesdog` you only need to run `nayesdog` in a terminal
* Default config is stored in `~/.nayesdog`
	+ `config.py`: configuration file.  Modify this file to include new RSS feeds or remove the existing ones.
	+ `tables.py.gz`: Trained model, containing the word counts that are used by the Naive Bayes Classifier. You can copy your model, use it somewhere else and share it.
	+ `.previous_session`: A hidden file that stores the state of your session. If you have problems, try to erase this file.
+ By running `nayesdog` with `--config` option you can have different nayesdogs trained for different purposes and different RSS feeds.

## Python library:
You can import the `nayesdog` library into python projects with `import nayesdog`

## To-do
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
