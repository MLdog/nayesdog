import re
import time
import os
import gzip # to save/laod
from collections import OrderedDict
from naylib import create_empty_word_count_table



# two dumb simple save/load in transparent format
def save_object_simple(outfilename, obj):
    s = repr(obj)
    #with open(outfilename, 'w') as f:
    with gzip.open(outfilename, 'wb') as f:
        f.write(s.encode())


# OrderedDict has to be defined, otherwise EVAL won't load it from file
def load_object_simple(filename):
    #with open(filename, 'r') as f:
    with gzip.open(filename, 'rb') as f:
        s = f.read()
    return eval(s)


def load_wt_st(db_file):
    if os.path.isfile(db_file):
        return load_object_simple(db_file)
    else:
        return {
                'wt': create_empty_word_count_table(),
                'st': {0:0, 1:0}
               }


def file_to_str(filepath):
    with open(filepath, 'r') as f:
        s = f.read()
    return s


def simplify_html(s):
    s = re.sub('style="[^"]+"', '', s)
    s = re.sub('height="[^"]+"', '', s)
    s = re.sub('width="[^"]+"', '', s)
    # remove unnecessary tags
    for tag in ['div', 'span']:
        s = re.sub('<{tag}[^>]*>'.format(tag=tag), '', s)
        s = re.sub('</{tag}[^>]*>'.format(tag=tag), '', s)
    # those are not present in XML, right?
    #for tag in ['script', 'noscript']:
    #    s = re.compile('<{tag}[^>]*>[^<]+</{tag}>'.format(tag=tag), flags=re.MULTILINE).sub('', s)
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
                s.replace('\n', '').strip()
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
    mds = filter(lambda s: s != '', map(to_readable_md, d['entries']))
    mds = list(filter(lambda s: s != '', map(to_readable_md, d['entries'])))
    md = '\n\n-------------\n\n'.join(mds)
    md = '# ' + d['feed']['title'] + '\n\n' + re.sub('([#]+)', r'\1#', md)
    #print(md)
    with open(fpath, 'w') as f:
        f.write(md)


# DELETE THIS FUNCTION
def ids_to_file(path, files, outfullpath):
    # make file with ids

    fullpaths = map(lambda f: os.path.join(path, f), infiles)
    s = ''
    for fullpath in fullpaths:
        d = feedparser.parse(fullpath)
        ids = [e['id'] for e in d['entries']]
        s += ' \n'.join(ids)
        s += '\n'

    with open(outfullpath, 'w') as f:
        f.write(s)


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
                        notags(s).replace('\n', ' ').replace('\xa0', ' ')
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

