import feedparser
import re
#import html2text
# entry_separation = '<hr style="height: 10px; color: #000">'
from naylib import NaiveBayes
from urlparse import urlparse
import mimetypes
from doglib import (
        tranform_feed_entry_to_bag_of_words,
        file_to_str,
        simplify_html
        )
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import naylib
import time
import shelve
import os
from config import (
        server_address,
        cssfile,
        feeds_url_dict,
        previous_session_database_file,
        word_counts_database_file,
        maximal_number_of_entries_in_memory,
        stopwords_file
        )
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
  <script>
  function imtoggle() {
      var images = document.getElementsByTagName('img');
      if (images[0].style.display != "none") {
          var style = "none";
      } else {
          var style = "inline";
      }
      for (i = 0; i < images.length;i++ ) {
          images[i].style.display = style;
      }
  }
  </script>
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
                     "authors": "",
                     "link": "",
                     "time": str(time.time())}
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

# old version of like-dislike
def generate_radio(var_name, value, txtzo):
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


def generate_submit_button(var_name, value, image_path):
    s = "<input type=\"image\" name=\""+var_name+"\" "
    s += "value=\""+value+"\" "
    s += "src=\""+image_path+"\"> \n"
    return s


def to_form(element,action="\"\"", method="\"get\""):
    s = "<form action="+action+" method="+method+">\n"
    s += element
    s += "</form>\n"
    return s

def to_div(div,element,id_html=None):
    if id_html is not None:
        s = "<div class=\""+div+"\" id=\""+id_html+"\"> \n"
    else:
        s = "<div class=\""+div+"\">\n"
    s += element
    s += "</div>\n"
    return s

def to_span(span, element):
    s = "<span class=\""+span+"\">\n"
    s += element
    s += "</span>\n"
    return s

def generate_link(href, name):
    s = "<a href=\""+href+"\">\n"
    s += name+"\n"
    s += "</a>\n"
    return s

def generate_html_table_column(element):
    s = "<th>\n"
    s += element
    s += "</th>\n"
    return s

def generate_html_table_row(element):
    s = "<tr>\n"
    s += element
    s += "</tr>\n"
    return s

def generate_html_table(element):
    s = "<table>\n"
    s += element
    s += "</table>\n"
    return s

def generate_html_header(element):
    s = "<header>\n"
    s += element
    s += "</header>\n"
    return s

def generate_horizontal_rule():
    return "<hr>\n"

def to_body(element):
    s = '<body>\n'
    s += element
    s += '</body>\n'
    return s

def represent_rss_entry(entry, key_entry):
    s = ""
    if "title" in entry:
        if "link" in entry:
            s += to_span("title",generate_link(entry["link"],entry["title"]))
        else:
            s += to_span("title",entry["title"])
    if "authors" in entry:
        authors = ", ".join(entry["authors"])
        s += to_span("authors",", ".join(entry["authors"]))
    if "content" in entry:
        s += to_span("content",entry["content"])
    if "prediction" in entry:
        prediction = entry["prediction"]
        s += "P(Dislike) = "+str(prediction[0])+"<br>\n"
        s += "P(Like) = "+str(prediction[1])+"<br>\n"
    s = to_div("entry",s,key_entry)
    return s

def to_anchor(element):
    return "\"#"+element+"\""


class HTTPServer_RequestHandler_feeds(BaseHTTPRequestHandler):

    def __init__(self, *args):
        BaseHTTPRequestHandler.__init__(self, *args)
        self.ML = NaiveBayes()

    def generate_header(self, list_rss_feeds):
        """
        Generate HTML code to create the header of the webpage interface.
        The header contains a menu with all the different RSS feeds received.
        :param list_rss_feeds: List of RSS feeds titles
        :type list_rss_feeds: List
        :returns: HTML code to generate a header for the webpage interface 
        :rtype: String 
        """
        html_table_row = ""
        for feed in list_rss_feeds:
            menu_element = generate_link(feed, feed)
            if feed == self.server.current_preference_folder or feed == self.server.feed_chosen:
                menu_element = to_span("selected_link", menu_element)
            else:
                menu_element = to_span("unselected_link", menu_element)
            html_table_column = generate_html_table_column(menu_element)
            html_table_column = to_span("menu_column_table", html_table_column)
            html_table_row += html_table_column
        html_table_row = to_span("menu_row_table", html_table_row)
        menu = generate_html_table_row(html_table_row)
        menu = generate_html_table(menu)
        menu = to_div("menu_bar", menu)
        menu += to_span("menu_bar_separator", generate_horizontal_rule())
        return menu

    def generate_save_delete_option(self,
                                    var_name,
                                    anchor_to_closest_element,
                                    method):
        s = generate_submit_button(var_name,
                                    "Save",
                                    "/icons/save.png")
        s += generate_submit_button(var_name,
                                     "Delete",
                                     "/icons/delete.png")
        s = to_form(s,action=anchor_to_closest_element,method=method)
        s = to_div("submit_bar",s)
        return s

    def generate_like_options(self, 
                              var_name, 
                              anchor_to_closest_element, 
                              method):
        """
        Generate HTML code to create  radio and submit button for 
        Like/Dislike/Ignore options.
        :param self: self
        :param var_name: Variable name.
        :type var_name: String.
        :returns: HTML code to generate radio and submit button
        :rtype: String.
        """
        s = to_span("submit_button",
                    generate_submit_button(var_name,
                                            "Like",
                                            "/icons/like.png"))
        s += to_span("submit_button",
                     generate_submit_button(var_name,
                                             "Dislike",
                                             "/icons/dislike.png"))

        s = to_form(s, action=anchor_to_closest_element, method=method)
        s = to_div("submit_bar", s)
        return s

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
            session_dict = shelve.open(self.server.previous_session, writeback=True)
            if index in session_dict["preferences"][self.server.current_preference_folder][feed_name].keys():
                if preference == "Like":
                    entry = session_dict["preferences"][self.server.current_preference_folder][feed_name].pop(index)
                    if feed_name not in session_dict["preferences"][preference]:
                        session_dict["preferences"][preference][feed_name] = {}
                    session_dict["preferences"][preference][feed_name][index] = entry
                    x = tranform_feed_entry_to_bag_of_words(entry)
                    self.server.nayesdog.fit(x, 1)
                    session_dict.close()
                if preference == "Dislike":
                    entry = session_dict["preferences"][self.server.current_preference_folder][feed_name].pop(index)
                    x = tranform_feed_entry_to_bag_of_words(entry)
                    self.server.nayesdog.fit(x, 0)
                if preference in ["Delete"]:
                    session_dict["preferences"][self.server.current_preference_folder][feed_name].pop(index)
                if preference == "Save":
                    entry = session_dict["preferences"][self.server.current_preference_folder][feed_name][index]
                    file_save = open(feed_name+"_saved_entries.html", "a")
                    file_save.write(represent_rss_entry(entry))
                    file_save.write(self.generate_entry_separator())
                    file_save.close()
            else:
                print "{} not in keys()".format(index)

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
        return to_span("entries_separator", "<br>\n<hr>\n")

    def update_feed_or_preference_folder(self):
        folder = self.extract_chosen_feed_from_path()
        session_dict = shelve.open(self.server.previous_session)
        if folder in session_dict["preferences"].keys():
            self.server.current_preference_folder = folder
            self.server.feed_chosen = ""
        elif folder in self.server.feeds_url_dict.keys():
            self.server.feed_chosen = folder
        session_dict.close()

    def get_closest_element_anchor(self, keys, key_id, feed_chosen):
        if key_id == len(keys) - 1:
            return to_anchor(feed_chosen+"_"+keys[key_id - 1])
        return to_anchor(feed_chosen+"_"+keys[key_id + 1])

    """
    # The information is in self.rfile.read(length)
    # Then we will probably need to call the same functions as in do_GET
    def do_POST(self):
        request_path = self.path
        print("\n----- Request post Start ----->\n")
        print(request_path)
        request_headers = self.headers
        content_length = request_headers.getheaders('content-length')
        length =int(content_length[0]) if content_length else 0
        print(request_headers)
        print(self.rfile.read(length))
    """

    def do_GET(self):
        self.send_response(200)
        # import pdb; pdb.set_trace()
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
            self.wfile.write('''<body>
                <div class="ontop">
                    <a href="#" onclick="javascript:imtoggle()">Toggle images</a><br>
                    <a href="/Learn">Learn</a>
                </div>
            ''')
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
                dic_current_feed = dict_feeds[feed_chosen]
                sorted_keys = self.server.rank_entries_by_preference(dic_current_feed)
                for idx_key, key in enumerate(sorted_keys):
                    entry = dic_current_feed[key]
                    anchor = self.get_closest_element_anchor(sorted_keys,
                                                             idx_key,
                                                             feed_chosen)
                    id_entry = self.generate_id_entry(feed_chosen, key)
                    rss_entry = represent_rss_entry(entry, id_entry)
                    self.wfile.write(rss_entry)
                    if self.server.current_preference_folder == "Home":
                        self.wfile.write(self.generate_like_options(id_entry,
                                                                    anchor,
                                                                    "get"))
                    else:
                        self.wfile.write(self.generate_save_delete_option(
                                                                 id_entry,
                                                                 anchor,
                                                                 "get"))
                    self.wfile.write(self.generate_entry_separator())
            self.wfile.write('</body>\n</html>')
        return


class HTTPServerFeeds(HTTPServer):
    def __init__(self,
                 server_address,
                 HTTPServer_RequestHandler,
                 cssfile,
                 feeds_url_dict,
                 previous_session,
                 word_counts_database_file,
                 stopwords_file,
                 maximal_number_of_entries):
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
        :type feeds_url_dict: Dict."""
        HTTPServer.__init__(self, server_address, HTTPServer_RequestHandler)
        self.cssfile = cssfile
        self.feeds_url_dict = feeds_url_dict
        self.previous_session = previous_session
        self.current_preference_folder = "Home"
        self.feed_chosen = ""
        self.nayesdog = naylib.NaiveBayes(word_counts_database_file,
                                          stopwords_file,
                                          maximal_number_of_entries)
        self.update_session()

    def update_session(self):
        session_dict = shelve.open(self.previous_session, writeback=True)
        if "preferences" not in session_dict:
            session_dict["preferences"] = {}
        if "seen_entries_keys" not in session_dict:
            session_dict["seen_entries_keys"] = {}
        if "Like" not in session_dict["preferences"]:
            session_dict["preferences"]["Like"] = {}
        # if "Dislike" not in session_dict["preferences"]:
        #    session_dict["preferences"]["Dislike"] = {}
        if "Home" not in session_dict["preferences"]:
            session_dict["preferences"]["Home"] = {}
        self.initialize_each_seen_entry_as_useless(session_dict["seen_entries_keys"])
        for feed in self.feeds_url_dict:
            received_entries = preprocess_rss_feed(self.feeds_url_dict[feed])
            for key, entry in received_entries.iteritems():
                if key not in session_dict["seen_entries_keys"]:
                    if feed not in session_dict["preferences"]["Home"]:
                        session_dict["preferences"]["Home"][feed] = {}
                    session_dict["preferences"]["Home"][feed][key] = entry
                    x = tranform_feed_entry_to_bag_of_words(entry)
                    entry["prediction"] = self.nayesdog.predict(x)
                session_dict["seen_entries_keys"][key] = 1
        self.prune_useless_stored_entries_keys(session_dict["seen_entries_keys"])
        session_dict.close()

    def initialize_each_seen_entry_as_useless(self, seen_entries_keys):
        for key in seen_entries_keys:
            seen_entries_keys[key] = 0

    def prune_useless_stored_entries_keys(self,seen_entries_keys):
        for key in seen_entries_keys.keys():
            if not seen_entries_keys[key]:
                seen_entries_keys.pop(key)

    def rank_entries_by_preference(self,dict_entries):
        get_prediction_from_entry = lambda k: dict_entries[k]["prediction"][1]
        ranks = sorted(dict_entries, key=lambda k: get_prediction_from_entry, reverse=True)
        return ranks
        
def run():
    httpd = HTTPServerFeeds(server_address,
                            HTTPServer_RequestHandler_feeds,
                            cssfile,
                            feeds_url_dict,
                            previous_session_database_file,
                            word_counts_database_file,
                            stopwords_file,
                            maximal_number_of_entries_in_memory)
    print('running server...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
