"""
Nayesdog: RSS reader with naive bayes powered recommendations
Copyright (c) 2016 Ilya Prokin and Sergio Peignier
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public Licensealong with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re
import time
import os
import feedparser
from urllib2 import urlopen
from functools import partial
import bs4


def fetch_page(url):
    response = urlopen(url)
    charset = response.headers.getparam('charset')
    page = response.read()
    if charset is not None:
        page = page.decode(charset)
    return page


def get_inside_tag(page, tag='title'):
    try:
        return page.split('<{}>'.format(tag))[1].split('</{}>'.format(tag))[0]
    except:
        return ''


def get_body(page, func):
    sp = bs4.BeautifulSoup(page)
    return str(eval(func))


def compose(*functions):
    return lambda x: reduce(lambda v, f: f(v), reversed(functions), x)


get_title = compose(lambda x: x.strip(), get_inside_tag)
#get_body = partial(get_inside_tag, tag="body")


def file_to_str(filepath):
    with open(filepath, 'r') as f:
        s = f.read()
    return s


def generate_entry_id(id_entry):
    """
    Keeps only letters and number in RSS entry id
    :param id_entry: RSS entry id
    :type id_entry: String
    :returns: Modified RSS entry id
    :rtype: String
    """
    return re.sub('[^a-zA-Z0-9]+', '', id_entry)


def simplify_html(s):
    """
    Simplify HTML code
    :param s: Piece of HTML code 
    :type s: String
    :returns: Piece of HTML code simplified
    :stype: String
    """
    s = re.sub('style="[^"]+"', '', s)
    s = re.sub('height="[^"]+"', '', s)
    s = re.sub('width="[^"]+"', '', s)
    # remove unnecessary tags
    for tag in ['div', 'span']:
        s = re.sub('<{tag}[^>]*>'.format(tag=tag), '', s)
        s = re.sub('</{tag}[^>]*>'.format(tag=tag), '', s)
    return s


def notags(s):
    """
    Remove tags from HTML piece of code
    :param s: Piece of HTML code from which we should remove tags
    :type s: String
    :returns: Piece of HTML code with all tags removed
    :rtype: String
    """
    return re.sub('<[^>]+>', '', s)


def nopunctuation(s):
    """
    Removes punctuation from string
    :param s: String from which we should remove puntuation
    :type s: String
    :returns: String whithout punctuation 
    :rtype: String
    """
    return re.sub(' +',' ',
            re.sub('[^\w\s]','',
                s.replace('\n', ' ').strip()
            )
           )


def preprocess_html(url, pattern, func, prefix=None):
    page = fetch_page(url)
    urls_of_items = list(set(re.findall(pattern, page)))
    if prefix is not None:
        urls_of_items = list(map(lambda url: prefix+url, urls_of_items))

    entries = dict(map(
        lambda url:
            (
                generate_entry_id(url).encode('utf-8')
                ,
                (lambda x: 
                    {
                        'title'   : get_title(x).encode("utf-8"),
                        'content' : simplify_html(get_body(x, func))\
                                .encode("utf-8"),
                        'authors' : ''.encode("utf-8"),
                        'link'    : ''.encode("utf-8"),
                        'time'    : str(time.time())
                    }
                )(
                    fetch_page(url)
                )
            )
            ,
            urls_of_items
        ))

    return entries


def preprocess_rss_feed(url):
    """
    Preprocess RSS feed and only keeps the most important elements for each entry, i.e.,
    the title, content, author, link and id
    :param url: RSS feed url
    :type: String
    :returns: Dictionnary of most important entry elements
    :rtype: Dict
    """
    feed_parsed = feedparser.parse(url)
    entries = {}
    for entry in feed_parsed['entries']:
        entry_dic = {
            "title": "",
            "content": "",
            "authors": "",
            "link": "",
            "time": str(time.time())
        }
        if "title" in entry:
            entry_dic["title"] = simplify_html(entry["title"]).encode('utf-8')
        if "content" in entry:
            entry_dic["content"] = simplify_html(entry["content"][0]["value"]).encode('utf-8')
        elif "summary" in entry:
            entry_dic["content"] = simplify_html(entry["summary"]).encode('utf-8')
        else:
            print entry.keys()
        if "author" in entry:
            entry_dic["authors"] = [author["name"].encode('utf-8') for author in entry["authors"]]
        if "link" in entry:
            entry_dic["link"] = entry["link"].encode('utf-8')
        if "id" in entry.keys():
            entries[generate_entry_id(entry["id"]).encode('utf-8')] = entry_dic
    return entries


def preprocess_feed(args):
    if isinstance(args, str):
        return preprocess_rss_feed(args)
    else:
        if args[0] == 'HTML':
            return preprocess_html(args[1], args[2], args[3])
        elif args[0] == 'HTMLpref':
            return preprocess_html(args[1], args[2], args[3], prefix=args[4])
        else:
            raise ValueError


def html_to_bag_of_words(html_code):
    """
    Converts piece of html code into bag of words
    :param html_code: Piece of html code
    :type html_code: String
    :returns: Bag of words
    :rtype: List of strings
    """
    bag_words = notags(html_code)
    bag_words = bag_words.decode('utf-8').replace(u'\xa0', ' ')
    bag_words = nopunctuation(bag_words)
    bag_words = bag_words.lower()
    return bag_words.split()


def tranform_feed_entry_to_bag_of_words(entry):
    """
    Transform an entry into a bag of words
    :param entry: RSS entry, this element should contain 5 keys: "title",
    "content", "author", "time" and "link"
    :type entry: Dict
    :returns: Bag of words associated to entry
    :rtype: List of strings 
    """
    title_bag_words =  html_to_bag_of_words(entry["title"])
    content_bag_words = html_to_bag_of_words(entry["content"])
    authors_bag_words = ["_".join(author.split()) for author in entry["authors"]]
    return title_bag_words + content_bag_words + authors_bag_words
    

