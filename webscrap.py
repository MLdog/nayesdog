import re
from urllib.request import urlopen
from functools import partial
#from lxml import html
#import bs4


def fetch_page(url):
    with urlopen(url) as response:
        page = response.read().decode(response.headers.get_content_charset())
    return page

def get_inside_tag(page, tag='title'):
    try:
        return page.split('<{}>'.format(tag))[1].split('</{}>'.format(tag))[0]
    except:
        return ''

def compose(*functions):
    return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

#def compose(*funcs):
#    def f(x):
#        res = x
#        for arg in funcs[::-1]:
#            res = arg(res)
#        return res
#    return f
    

get_title = compose(lambda x: x.strip(), get_inside_tag)
get_body = partial(get_inside_tag, tag="body")


#tree = html.fromstring(page)
#'title'   : str(tree.xpath('//head/title/text()')[0].strip())
#'content' : str()

#def parse_page(page):
#    sp = bs4.BeautifulSoup(page)
#    parsed_dict = {
#        'title'   : sp.title.contents[0].strip(),
#        'content' : str(sp.body)
#    }
#    return parsed_dict



url = 'http://www.nature.com/news/index.html'
pattern = 'https?://[^/]+nature.com/news/[^"]+'

page = fetch_page(url)
urls_of_items = re.findall(pattern, page)

#l = list(map(
#        lambda url: parse_page(fetch_page(url))
#        ,
#        urls_of_items
#    ))

l = list(map(lambda url:
        (lambda x: {
            'title'  : get_title(x),
            'content': get_body(x)
        })(fetch_page(url))
        ,
        urls_of_items
    ))

print(l)
