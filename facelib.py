import feedparser
import re
#import html2text
# entry_separation = '<hr style="height: 10px; color: #000">'
from  urlparse import urlparse
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
    for entry in feed_parsed['entries']:
        yield entry['content'][0]['value'].encode('utf-8')

# html2text.html2text(html)

#   open('shit.html', 'w')
#    with open('shit.html', 'a') as f:
#        for ss in s:
#            f.write(ss)


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

#!/usr/bin/python3
# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    # GET
    def do_GET(self):
        # Send response status code
        self.send_response(200)
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()  
        query = urlparse(self.path).query
        if query != "":
            query_components = dict(qc.split("=") for qc in query.split("&"))
        else:
            query_components = ""
        #send message to client
        url = "http://feeds.nature.com/NatureLatestResearch"
        self.wfile.write(page_head_tpl)
        self.wfile.write('<body>')
        s = rss_feed_to_html(url)
        for e in s:
            self.wfile.write(e)
            self.wfile.write(generate_like_options("caca"))
            #self.wfile.write("<form action=\"\" method=\"get\">\n<button name=\"foo\"value=\"upvote\">Upvote</button>\n</form>")
            #self.wfile.write("<form action=\"\" method=\"get\">\n<button name=\"foo2\"value=\"downvote\">Downvote</button>\n</form>")
            self.wfile.write(str(query_components))
        self.wfile.write('</body>\n</html>')
        return
#?hifeiz=ezfqz&jdosvod=efzzefez                                                                                                                         
def run():
    print('starting server...')
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http
    # server, you need root access
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

run()
