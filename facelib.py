import feedparser
import re
#import html2text
# entry_separation = '<hr style="height: 10px; color: #000">'
from  urlparse import urlparse
from doglib import file_to_str
import mimetypes
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer 

page_head_tpl = """
<!DOCTYPE html><html><head>
  <meta charset="utf-8">
  <meta name="generator" content="hands">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
  <title>News</title>
  <style type="text/css">code{white-space: pre;}</style>
  <link rel="stylesheet" href="/css.css">
  <!--[if lt IE 9]>
    <script src="//cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.3/html5shiv-printshiv.min.js"></script>
  <![endif]-->
</head>
"""

def rss_feed_to_html(url):
    feed_parsed = feedparser.parse(url)
    entries = []
    for entry in feed_parsed['entries']:
        entries.append(entry['content'][0]['value'].encode('utf-8'))
    return entries

def generate_radio(var_name, value, txt):
    """
    Generate HTML code to create a radio
    :param var_name: Variable name.
    :param value: Variable value.
    :param txt: Radio text.
    :type var_name: String.
    :type value: String.
    :type txt: String.
    :returns: HTML code to create a radio
    :rtype: String.
    """
    s = "<input type=\"radio\" name=\""+var_name
    s += "\" value=\""+value+"\">"+txt+"<br>\n"
    return s


def generate_like_options(var_name):
    """
    Generate HTML code to create  radio and submit button for Like/Dislike/Ignore options.
    :param var_name: Variable name. 
    :type var_name: String.
    :returns: HTML code to generate radio and submit button
    :rtype: String.
    """
    button_html_code = "<form action=\"\" method=\"get\">\n"
    button_html_code += generate_radio(var_name, "like", "Like")
    button_html_code += generate_radio(var_name, "dislike", "Dislike")
    button_html_code += generate_radio(var_name, "ignore", "Ignore")
    button_html_code += "<input type=\"submit\" value=\"Submit\">\n</form>\n"
    return button_html_code


def generate_header(list_rss_feeds):
    """
    Generate HTML code to create the header of the webpage interface.
    The header contains a menu with all the different RSS feeds received.
    :param list_rss_feeds: List of RSS feeds titles
    :type list_rss_feeds: List
    :returns: HTML code to generate a header for the webpage interface 
    :rtype: String 
    """
    nb_feeds = len(list_rss_feeds)
    header = "<header>\n"
    header += "<table align=\"center\">\n"
    for i in xrange(nb_feeds):
        header += "<col width="+str(100/nb_feeds)+"%>\n"
    header += "<thead>\n"
    header += "<tr class=\"header\">\n"
    for feed in list_rss_feeds:
        header += "<th><a href=\""+feed+"\">"+feed+"</a></th>\n"
    header += "</tr>\n"
    header += "</thead>\n"
    header += "</table>\n"
    header += "</header>\n"
    header += "<hr>\n"
    return header


class HTTPServer_RequestHandler_feeds(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)
        # Send headers
        query = urlparse(self.path).query
        self.feed_chosen = self.path.split("/")[-1]
        if self.path == '/'+self.server.cssfile:
            mimetype, _ = mimetypes.guess_type(self.path)
            self.send_header('Content-type', mimetype)
            self.end_headers()
            self.wfile.write(file_to_str(self.server.cssfile))
        else:
            self.feed_chosen = self.path.split("/")[-1]
            self.send_header('Content-type','text/html')
            self.end_headers()
            if query != "":
                query_components = dict(qc.split("=") for qc in query.split("&"))
            else:
                query_components = ""
            #send message to client
            self.wfile.write(page_head_tpl)
            self.wfile.write('<body>')
            self.wfile.write(generate_header(self.server.dict_of_entries.keys()))
            if self.feed_chosen in self.server.dict_of_entries.keys():
                for e in self.server.dict_of_entries[self.feed_chosen]:
                    self.wfile.write(e)
                    self.wfile.write(generate_like_options("a"))
                    self.wfile.write(str(query_components))
            self.wfile.write('</body>\n</html>')
        return


class HTTPServerFeeds(HTTPServer):
    def __init__(self,
                 server_address,
                 HTTPServer_RequestHandler,
                 cssfile,
                 feeds_url_dict):
        """
        Generates an instance for HTTPServerFeeds that inheritates from
        HTTPServer class.
        :param server_address: Server adress, paramater required by HTTPServer.
        :param HTTPServer_RequestHandler: HTTPServer_RequestHandler required by
        HTTPServer.
        :param cssfile: CSS file.
        :param feeds_url_dict: Dictionnary with feed urls and names.
        :type server_address: Tuple.
        :type HTTPServer_RequestHandler: HTTPServer_RequestHandler class.
        :type cssfile: String.
        :type feeds_url_dict: Dict.
        """
        HTTPServer.__init__(self,server_address,HTTPServer_RequestHandler)
        self.cssfile = cssfile
        self.feeds_url_dict = feeds_url_dict
        self.generate_list_of_entries_per_feed()

    def generate_list_of_entries_per_feed(self):
        """
        Generates a list of entries per feed in HTML format ready to output for
        each feed. Each feed cna be accessed through its keys. Creates a new
        attribute dict_of_entries, which is a dictionnary with feeds names as
        keys and lists of entries as values.
        """
        self.dict_of_entries = {}
        for feed in self.feeds_url_dict:
            self.dict_of_entries[feed] = rss_feed_to_html(self.feeds_url_dict[feed])



def run():
    print('starting server...')
    server_address = ('127.0.0.1', 8081)
    cssfile = 'css.css'
    feeds_url_dict = {'nature':'http://feeds.nature.com/NatureLatestResearch',
                      'arstecnica':'http://feeds.arstechnica.com/arstechnica/science'}
    httpd = HTTPServerFeeds(server_address,
                            HTTPServer_RequestHandler_feeds,
                            cssfile,
                            feeds_url_dict)
    print('running server...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
