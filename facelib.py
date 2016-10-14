import feedparser
import re
#import html2text
# entry_separation = '<hr style="height: 10px; color: #000">'
from  urlparse import urlparse
from doglib import file_to_str, simplify_html
import mimetypes
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer 
import time
import shelve
import os
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

def generate_entry_id(id_entry):
    return re.sub('[^a-zA-Z0-9]+', '', id_entry)


def preprocess_rss_feed(url):
    feed_parsed = feedparser.parse(url)
    entries = {}
    for entry in feed_parsed['entries']:
        entry_dic = {"title": "",
                     "content": "",
                     "author": "",
                     "time": str(time.time())}
        if "title" in entry:
            entry_dic["title"] = entry["title"].encode('utf-8')
        if "content" in entry:
            entry_dic["content"] = entry["content"][0]["value"].encode('utf-8')
        if "author" in entry:
            entry_dic["author"] = entry["authors"]
        if "id" in entry.keys():
            entries[generate_entry_id(entry["id"])] = entry_dic
    return entries


def represent_rss_entry(entry):
    return "<p><b>"+entry["title"]+"<br>"+"</p></b>"+simplify_html(entry["content"])


# old version of like-dislike
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
    s += "\" value=\""+value+"\">"+txt+"\n"
    return s

def generate_submite_bouton(var_name, value, image_path):
    s = "<input type=\"image\" name=\""+var_name+"\" "
    s += "value=\""+value+"\" "
    s += "src=\""+image_path+"\"> \n"
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
    button_html_code += generate_submite_bouton(var_name,
                                                "Like",
                                                "/icons/like.png")
    button_html_code += generate_submite_bouton(var_name,
                                                "Dislike",
                                                "/icons/dislike.png")
    button_html_code += "</form>\n"
    #button_html_code += generate_radio(var_name, "Like", "Like")
    #button_html_code += generate_radio(var_name, "Dislike", "Dislike")
    #button_html_code += generate_radio(var_name, "Ignore", "Ignore")
    #button_html_code += "<input type=\"submit\" value=\"Submit\">\n</form>\n"
    return button_html_code

def generate_save_delete_option(var_name):
    button_html_code = "<form action=\"\" method=\"get\">\n"
    button_html_code += generate_submite_bouton(var_name,
                                                "Save",
                                                "/icons/save.png")
    button_html_code += generate_submite_bouton(var_name,
                                                "Delete",
                                                "/icons/delete.png")
    button_html_code += "</form>\n"
    return button_html_code


class HTTPServer_RequestHandler_feeds(BaseHTTPRequestHandler):
    # GET
    def generate_header(self, list_rss_feeds):
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
            if feed == self.server.current_preference_folder or feed == self.server.feed_chosen:
                header += "<th><a href=\""+feed+"\"style=\"color:rgb(0,0,0)\"><fontcolor=\"black\">"+feed+"</font></a></th>\n"
            else:
                header += "<th><a href=\""+feed+"\">"+feed+"</a></th>\n"
        header += "</tr>\n"
        header += "</thead>\n"
        header += "</table>\n"
        header += "</header>\n"
        header += "<hr>\n"
        return header


    def extract_chosen_feed_from_path(self):
        """
        Extract the desired RSS feed from the path
        :returns: Chosen feed.
        :rtype: String.
        """
        feed_chosen = self.path.split("/")[-1]
        feed_chosen = feed_chosen.split("?")[0]
        return feed_chosen

    def extract_query_components(self):
        """ 
        Extract the query components from path
        :returns: Query components.
        :rtype: Dict.
        """
        query = urlparse(self.path).query
        if query != "":
            return dict(query_components.split("=") for query_components in query.split("&"))
        else:
            return {}

    def update_preference_feed_menus_from_submission(self):
        """
        Sends rated entries to its corresponding location in preference menu
        (i.e. Liked entries to Like location, Unliked to Unlike ...)
        """
        query_components = self.extract_query_components()
        if query_components.keys():
            component = query_components.keys()[0].split(".")[0]
            preference = query_components[component]
            entry_information = self.extract_data_from_id_entry(component)
            feed_name = entry_information["feed"]
            index = entry_information["index"]
            session_dict =shelve.open(self.server.previous_session,writeback=True)
            print feed_name,self.server.current_preference_folder
            if preference in ["Like", "Dislike"]:
                entry = session_dict["preferences"][self.server.current_preference_folder][feed_name].pop(index)
                if feed_name not in session_dict["preferences"][preference]:
                    session_dict["preferences"][preference][feed_name] = {}
                session_dict["preferences"][preference][feed_name][index] = entry
                session_dict.close()
            if preference in ["Delete"]:
                session_dict["preferences"][self.server.current_preference_folder][feed_name].pop(index)
            if preference in ["Save"]:
                entry = session_dict["preferences"][self.server.current_preference_folder][feed_name][index]
                file_save = open(feed_name+"_saved_entries.html","a")
                file_save.write(represent_rss_entry(entry))
                file_save.write(self.generate_entry_separator())
                file_save.close()

        # self.smartdog.fit()

    def generate_id_entry(self, feed_name, index):
        """
        Generate ID entry for preference button
        :returns: Entry ID
        :rtype: String
        """
        return feed_name+"_"+index

    def extract_data_from_id_entry(self, entry):
        """
        Extracts information from the ID of an entry
        :param entry: Entry ID
        :returns: Information of the given entry, i.e., entry feed name and
        entry index
        :rtype: Dict.
        """
        entry_split = entry.split("_")
        return {"feed": entry_split[0], "index": entry_split[1]}

    def generate_entry_separator(self):
        return "<br>\n<hr>\n"

    def update_feed_or_preference_folder(self):
        folder = self.extract_chosen_feed_from_path()
        session_dict = shelve.open(self.server.previous_session)
        if folder in session_dict["preferences"].keys():
            self.server.current_preference_folder = folder
            self.server.feed_chosen = ""
        elif folder in self.server.feeds_url_dict.keys():
            self.server.feed_chosen = folder
        session_dict.close()

    def do_GET(self):
        self.send_response(200)
        
        #import pdb; pdb.set_trace()
        mimetype, _ = mimetypes.guess_type(self.path)
        if self.path == '/'+self.server.cssfile:
            self.send_header('Content-type', mimetype)
            self.end_headers()
            self.wfile.write(file_to_str(self.server.cssfile))
        elif mimetype is not None and "image" in mimetype:
            imfile = self.path[1:] if self.path[0] == "/" else self.path
            imfile = os.path.join(os.getcwd(), imfile)
            if os.path.isfile(imfile):
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(file_to_str(imfile))
        else:
            self.update_feed_or_preference_folder()
            self.update_preference_feed_menus_from_submission()
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(page_head_tpl)
            self.wfile.write('<body>')
            # Generate preferences menu
            session_dict = shelve.open(self.server.previous_session)
            preference_menu_keys = session_dict["preferences"].keys()
            preference_menu = self.generate_header(preference_menu_keys)
            self.wfile.write(preference_menu)
            # Generate feeds menu in the current preference menu
            current_preference = self.server.current_preference_folder
            dict_feeds = session_dict["preferences"][current_preference]
            feeds_menu_keys = dict_feeds.keys()
            feeds_menu = self.generate_header(feeds_menu_keys)
            self.wfile.write(feeds_menu)
            session_dict.close()
            # Represent each entry
            feed_chosen = self.server.feed_chosen
            if self.server.feed_chosen in feeds_menu_keys:
                for key, entry in dict_feeds[feed_chosen].iteritems():
                    id_entry = self.generate_id_entry(feed_chosen, key)
                    self.wfile.write(represent_rss_entry(entry))
                    if self.server.current_preference_folder == "Home":
                        self.wfile.write(generate_like_options(id_entry))
                    else:
                        self.wfile.write(generate_save_delete_option(id_entry))
                    self.wfile.write(self.generate_entry_separator())
            self.wfile.write('</body>\n</html>')
        return


class HTTPServerFeeds(HTTPServer):
    def __init__(self,
                 server_address,
                 HTTPServer_RequestHandler,
                 cssfile,
                 feeds_url_dict,
                 previous_session=".previous_session"):
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
        HTTPServer.__init__(self, server_address, HTTPServer_RequestHandler)
        self.cssfile = cssfile
        self.feeds_url_dict = feeds_url_dict
        self.previous_session = previous_session
        self.current_preference_folder = "Home"
        self.feed_chosen = ""
        self.update_session()

    def update_session(self):
        session_dict = shelve.open(self.previous_session, writeback=True)
        if "preferences" not in session_dict:
            session_dict["preferences"] = {}
        if "seen_entries_keys" not in session_dict:
            session_dict["seen_entries_keys"] = []
        if "Like" not in session_dict["preferences"]:
            session_dict["preferences"]["Like"] = {}
        if "Dislike" not in session_dict["preferences"]:
            session_dict["preferences"]["Dislike"] = {}
        if "Home" not in session_dict["preferences"]:
            session_dict["preferences"]["Home"] = {}
        for feed in self.feeds_url_dict:
            received_entries = preprocess_rss_feed(self.feeds_url_dict[feed])
            for key, entry in received_entries.iteritems():
                if key not in session_dict["seen_entries_keys"]:
                    if feed not in session_dict["preferences"]["Home"]:
                        session_dict["preferences"]["Home"][feed] = {}
                    session_dict["preferences"]["Home"][feed][key] = entry
                    session_dict["seen_entries_keys"].append(key)
        session_dict.close()


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
