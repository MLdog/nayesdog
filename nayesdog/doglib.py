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

#remove this function
def dargmax(d, vmax0=-1):
    vmax = vmax0
    kmax = 0
    for k,v in d.items():
        if v > vmax:
            vmax = v
            kmax = k
    return kmax

#remove this function
def classnamer(k):
    return {0:"dislike", 1:"like"}.get(k, "dont know if you like")

#remove this funciton
def print_sorted(d, indent=0, s="  "):
    for k in sorted(d.keys()):
        print("{}{}".format(s*indent, k))
        if type(d[k]) == dict:
            print_sorted(d[k], indent=indent+1)
        else:
            print("{}{}".format(s*(indent+1), d[k]))

#remove this function
def file_to_str(filepath):
    with open(filepath, 'r') as f:
        s = f.read()
    return s


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


def to_readable_md(e):
    """
    Converts RSS entry into readable String in markdown format
    :param e: RSS entry
    :type e: dict
    :returns: String in markdown format
    :rtype: String
    """
    try:
        s = ''
        s += '# ' + e['title'].strip() + '\n\n'
        if 'authors' in e.keys():
            s += '## ' + ', '.join(list(map(lambda x: x['name'], e['authors']))) + '\n\n'
        if 'content' in e.keys():
            s += notags(e['content'][0]['value']).replace('\n', ' ').strip() + '\n\n'
        s += e['id']
        s = re.sub(' +', ' ', s)
        return s
    except:
        return ''


def feed_to_md_file(d, fpath):
    """
    Converts each entry of RSS feed parsed into readable Strings in markdown
    format and writes them in a file.
    :param d: RSS feed parsed 
    :param fpath: File path
    :type d: dict
    :type fpath: string
    """
    #mds = [s for s in map(to_readable_md, d['entries']) if s != '']
    mds = list(filter(lambda s: s != '', map(to_readable_md, d['entries'])))
    md = '\n\n-------------\n\n'.join(mds)
    md = '# ' + d['feed']['title'] + '\n\n' + re.sub('([#]+)', r'\1#', md)
    with open(fpath, 'w') as f:
        f.write(md)


def rating_from_md_file(mdfile):
    """
    Reads user-entered rating from mdfile.
    To rate news item, edit mdfile directly: add rating after id separated by
    one space character.
    E.g.:
    Before edit:
        https://arstechnica.com/?p=972521
    After edit:
        https://arstechnica.com/?p=972521 0
    :param mdfile: Full path to markdown file
    :type mdfile: string
    :returns: Dict with ids of feeds as keys and ratings as values
    :rtype: dict
    """
    mds = file_to_str(mdfile).split('\n\n-------------\n\n')
    id_rating = map(
        lambda md:
            (lambda x:
                (x[0], None) if len(x)==1 else (x[0], int(x[1]))
            )(md.split('\n')[-1].split(' '))
        ,
        mds
       )
    return dict(id_rating)


def rating_from_md_files_in_folder(mdfolder):
    """Extract ratings from .md files in mdfolder. Applies rating_from_md_file
    to each file in mdfolder.
    :param mdfolder: Path to folder
    :type mdfolder: string
    :returns: Dict with ids of feeds as keys and ratings as values (combined
    for all files)
    :rtype: dict
    """
    mdfiles = list(filter(lambda s: s[0] != '.' and s[-3:] == '.md', os.listdir(mdfolder)))
    fullpaths = map(lambda x: os.path.join(mdfolder, x), mdfiles)
    items_combined = sum(map(lambda x: list(rating_from_md_file(x).items()), fullpaths), [])
    return dict(filter(lambda x: x[1] != None, items_combined))


def process_an_entry(e):
    """
    Process an RSS entry and outputs a dictionary with the time stamp, the  title, the content
    (both transformed into bag of lowercase words) and the authors (if it
    exists)
    :param e: RSS entry
    :type e: dict
    :returns: Important elements in RSS entry
    :rtype: dict
    """
    l =  [time.time()]
    # transform title and content to bag of lowercase words
    l += list(
            map(
                lambda s:
                    nopunctuation(
                        notags(s).replace('\n', ' ').replace(u'\xa0', ' ')
                    ).strip().lower().split(' ')
                ,
                [
                    e['title'],
                    e['content'][0]['value'] if 'content' in e.keys() else ''
                ]
            )
         )
    l += [e['id']]
    # give names to items
    l = dict(
            zip(
                ['timestamp', 'title', 'content', 'id']
                ,
                l
            )
        )
    # add authors if any
    if 'authors' in e.keys():
        l['authors'] = list(map(lambda x: x['name'], e['authors']))
    return l

#should remove this function
def process_sergios_entry(e, index):
    """
    Process an RSS entry and list of words for training
    """
    # transform title and content to bag of lowercase words

    l = sum(list(
            map(
                lambda s:
                    nopunctuation(
                        notags(s).replace('\n', ' ').replace(u'\xa0', ' ')
                    ).strip().lower().split(' ')
                ,
                [
                    e['title'],
                    e['content']
                ]
            )
         ), [])
    # add authors if any
    if 'authors' in e.keys():
        l += e['authors']
    return {index:l}

#should remove this function
def transform_feed_dict(d):
    # load simplified entries
    entries = list(map(process_an_entry, d['entries']))

    # get ids
    ids = [e['id'] for e in entries]

    # throw away timestamps and ids
    for e in entries:
        e.pop('timestamp')
        e.pop('id')

    # title and text combined
    txts = map(
                lambda e: 
                    list(filter(
                        lambda s: s != '', # if content is absent
                        sum(e.values(), [])
                    ))
                ,
                entries
              )

#    txts = list(txts)

    return dict(zip(ids, txts))

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
    

