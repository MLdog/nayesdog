import re
import time

# preprocess

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
    mds = list(filter(lambda s: s != '', map(to_readable_md, d['entries'])))
    md = '\n\n-------------\n\n'.join(mds)
    md = '# ' + d['feed']['title'] + '\n\n' + md.replace('#', '##')
    #print(md)
    with open(fpath, 'w') as f:
        f.write(md)


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
                        notags(s).replace('\n', '')
                    ).strip().lower().split(' ')
                ,
                [
                    e['title'],
                    e['content'][0]['value']
                ]
            )
         )
    l += e['id']
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
