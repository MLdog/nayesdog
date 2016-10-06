import re
import time

# preprocess

def notags(s):
    return re.sub('<[^>]+>', '', s)


def nopunctuation(s):
    return re.sub(' +',' ',
            re.sub('[^\w\s]','',
                s.replace('\n', '').strip()
            )
           )


def to_readable_md(e):
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
    mds = list(filter(lambda s: s != '', map(to_readable_md, d['entries'])))
    md = '\n\n-------------\n\n'.join(mds)
    md = '# ' + d['feed']['title'] + '\n\n' + md.replace('#', '##')
    #print(md)
    with open(fpath, 'w') as f:
        f.write(md)


def process_an_entry(e):
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
