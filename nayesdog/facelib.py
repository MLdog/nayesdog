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
from urlparse import urlparse
import mimetypes
from doglib import (
        tranform_feed_entry_to_bag_of_words,
        file_to_str,
        simplify_html,
        preprocess_feed
        )
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import naylib
import time
from simpleshelve import SimpleShelve as shelve
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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
  function myFunctionHome() {
    document.getElementById("myDropdownHome").classList.toggle("show");
  }
  function myFunctionLike() {
    document.getElementById("myDropdownLike").classList.toggle("show");
  }
  function filterFunctionHome() {
    var input, filter, ul, li, a, i;
    input = document.getElementById("myInputHome");
    filter = input.value.toUpperCase();
    div = document.getElementById("myDropdownHome");
    a = div.getElementsByTagName("a");
    for (i = 0; i < a.length; i++) {
        if (a[i].innerHTML.toUpperCase().indexOf(filter) > -1) {
            a[i].style.display = "";
        } else {
            a[i].style.display = "none";
        }
    }
  }
  function filterFunctionLike() {
    var input, filter, ul, li, a, i;
    input = document.getElementById("myInputLike");
    filter = input.value.toUpperCase();
    div = document.getElementById("myDropdownLike");
    a = div.getElementsByTagName("a");
    for (i = 0; i < a.length; i++) {
        if (a[i].innerHTML.toUpperCase().indexOf(filter) > -1) {
            a[i].style.display = "";
        } else {
            a[i].style.display = "none";
        }
    }
  }
  window.onclick = function(e) {
    if (!e.target.matches('.Home')) {
  
      var dropdowns = document.getElementsByClassName("dropdownHome-content");
      for (var d = 0; d < dropdowns.length; d++) {
        var openDropdown = dropdowns[d];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
    if (!e.target.matches('.Like')) {
  
      var dropdowns = document.getElementsByClassName("dropdownLike-content");
      for (var d = 0; d < dropdowns.length; d++) {
        var openDropdown = dropdowns[d];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
  }
  </script>
</head>
"""


def generate_an_option(action_name,
                       var_name,
                       anchor_to_closest_element):
    """
    Generate Save and delete bar option
    :param action_name: Save/Delete/Otherwise
    :param var_name: Submit button variable name
    :param anchor_to_closest_element: Anchor to the closest entry
    :type action_name: String
    :type var_name: String
    :type anchor_to_closest_element: String
    :returns: HTML code for save and delete bar 
    :rtype: String
    """
    link_text = "/?"+var_name+"="+action_name+anchor_to_closest_element
    link = generate_link(link_text, action_name)
    link = to_span(action_name.lower()+"_option", link)
    return link


def generate_submit_button(var_name, value, image_path):
    """
    Generate HTML submit button with image
    :param var_name: Variable name
    :param value: Variable value
    :param image_path: Path of image
    :type var_name: String
    :type value: String
    :type image_path: String
    :returns: HTML code associated to the generation of submit button
    :rtype: String
    """
    s = "<input type=\"image\" name=\""+var_name+"\" "
    s += "value=\""+value+"\" "
    s += "src=\""+image_path+"\"> \n"
    return s

def to_form(element,action="\"\"", method="\"get\""):
    """
    Takes HTML piece of code and adds form context
    :param element: HTML pice of code to be inserted in context
    :param action: Form action
    :param method: Method to be used for sending back the information (get, post ..)
    :type element: String
    :type action: String
    :type method: String
    :returns: HTML code with form context
    :rtype: String 
    """
    s = "<form action="+action+" method="+method+">\n"
    s += element
    s += "</form>\n"
    return s

def to_div(div,element,id_html=None):
    """
    Takes HTML piece of code and adds div context
    :param div: Div class name
    :param element: HTML pice of code to be inserted in context
    :param id_html: ID for HTML div
    :type div: String
    :type element: String
    :type id_html: String or None
    :returns: HTML code with div context
    :rtype: String 
    """
    if id_html is not None:
        s = "<div class=\""+div+"\" id=\""+id_html+"\"> \n"
    else:
        s = "<div class=\""+div+"\">\n"
    s += element
    s += "</div>\n"
    return s

def to_span(span, element):
    """
    Takes HTML piece of code and adds span context
    :param span: Span class name
    :param element: HTML pice of code to be inserted in context
    :type div: String
    :type element: String
    :returns: HTML code with span context
    :rtype: String 
    """
    s = "<span class=\""+span+"\">\n"
    s += element
    s += "</span>\n"
    return s

def generate_link(href, name, function=None):
    """
    Generate HTML link
    :param href: Reference 
    :param name: Reference text
    :param function: On click function
    :type href: String
    :type name: String
    :type function: String or None 
    :returns: HTML link code
    :rtype: String
    """
    s = "<a href=\""+href+"\""
    if function is not None:
        s += " onclick=\""+function+"\""    
    s += ">\n"
    s += name+"\n"
    s += "</a>\n"
    return s

def generate_html_table_column(element):
    """
    Generate HTML column with text send as parameter
    :param element: HTML code to be inserted in column
    :type element: String
    :returns: HTML code inserted in html table column
    :rtype: String
    """
    s = "<th>\n"
    s += element
    s += "</th>\n"
    return s

def generate_html_table_row(element):
    """
    Generate HTML row with text send as parameter
    :param element: HTML code to be inserted in row
    :type element: String
    :returns: HTML code inserted in html table row
    :rtype: String
    """
    s = "<tr>\n"
    s += element
    s += "</tr>\n"
    return s

def generate_html_table(element):
    """
    Generate HTML table with text send as parameter
    :param element: HTML code to be inserted in table
    :type element: String
    :returns: HTML code inserted in html table
    :rtype: String
    """
    s = "<table>\n"
    s += element
    s += "</table>\n"
    return s

def generate_html_header(element):
    """
    Generate HTML header with text send as parameter
    :param element: HTML code to be inserted in header
    :type element: String
    :returns: HTML code inserted in html header
    :rtype: String
    """
    s = "<header>\n"
    s += element
    s += "</header>\n"
    return s

def generate_horizontal_rule():
    """
    Generate html horizontal rule
    """
    return "<hr>\n"

def to_body(element):
    """
    Generate HTML body with text send as parameter
    :param element: HTML code to be inserted in body
    :type element: String
    :returns: HTML code inserted in html body
    :rtype: String
    """
    s = '<body>\n'
    s += element
    s += '</body>\n'
    return s

def generate_html_button(function,button_class,text):
    """
    Generate HTML button
    :param function: On click function
    :param button_class: Button class
    :param text: Button text
    :type function: String 
    :type button_class: String
    :type text: String
    :returns: HTML button code
    :rtype: String
    """
    s = "<button " 
    s += "onclick=\""+function+"\" "
    s += "class=\""+button_class+"\"> "
    s += text
    s += "</button>"
    return s

def generate_input_text(input_type,placeholder,input_id,function):
    """
    Generate HTML input text
    :param input_type: Input type
    :param placeholder: Input text placeholder 
    :param input_id: Input text id
    :param function: On keyup function
    :type input_type: String
    :type placeholder: String
    :type input_id: String
    :type function: String
    :returns: HTML input text code
    :rtype: String
    """
    s = "<input "
    s += "type=\""+input_type+"\" "
    s += "placeholder=\""+placeholder+"\" "
    s += "id=\""+input_id+"\" "
    s += "onkeyup=\""+function+"\">"
    return s

def represent_rss_entry(entry, key_entry):
    """
    Generate HTML code for representing RSS entry
    :param entry: Entry Dictionnary with title, link, authors, content, prediction as keys
    :param key_entry: Key used as identifier for entry
    :type entry: Dict
    :type key_entry: String
    :returns: HTML entry representation
    :rtype: String
    """
    s = ""
    if "title" in entry:
        if "link" in entry:
            s += to_span("title",generate_link(entry["link"],entry["title"]))
        else:
            s += to_span("title",entry["title"])
    if "authors" in entry:
        s += to_span("authors",", ".join(entry["authors"]))
    if "content" in entry:
        s += to_span("content",entry["content"])
    if "prediction" in entry:
        prediction = entry["prediction"]
        s += "Score = "+str(prediction)+"<br>\n"
    s = to_div("entry",s,key_entry)
    return s

def to_anchor(element):
    """
    Add html anchor tag to element
    :param element: String be tagged
    :type element: String
    :returns: Tagged element
    :rtype: String
    """
    return "#"+element

def generate_html_break_line():
    """
    Generate HTML code for break line
    :returns: HTML code for beack line
    :rtype: String
    """
    return "<br>"

def to_header(header_level,element):
    """
    Generate HTML title header with text send as parameter
    :param header_level: Header level
    :param element: HTML code to be inserted in title header
    :type header_level: Int 
    :type element: String
    :returns: HTML code inserted in html title header
    :rtype: String
    """
    s = "<h"+str(header_level)+">" 
    s += element
    s += "</h"+str(header_level)+">" 
    return s

class HTTPServer_RequestHandler_feeds(BaseHTTPRequestHandler):

    def __init__(self, *args):
        BaseHTTPRequestHandler.__init__(self, *args)

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
            menu_element = generate_link(feed, self.server.correct_feed_name_to_text(feed))
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

    def generate_feeds_menu(self,
                            list_rss_feeds,
                            drop_button_name,
                            drop_button_text,
                            div_name,
                            button_function,
                            dropdown_ID,
                            filter_function,
                            input_name):
        """
        Generate Feeds side menu
        :param list_rss_feeds: List of RSS feeds titles
        :type list_rss_feeds: List
        :returns: HTML code for feeds menu
        :rtype: String
        """
        dropdown = generate_input_text("text","Search..",input_name,filter_function)
        feed_name = drop_button_name
        for feed in list_rss_feeds:
            menu_element = generate_link("/" + feed_name+"/"+feed, self.server.correct_feed_name_to_text(feed))
            dropdown += menu_element
        dropdown = to_div(div_name+"-content",dropdown,dropdown_ID)
        button = generate_html_button(button_function,drop_button_name,drop_button_text)
        menu = button + dropdown
        menu = to_div(div_name,menu)
        return menu

    def generate_save_delete_option(self,
                                    var_name,
                                    anchor_to_closest_element):
        """
        Generate Save and delete bar option
        :param var_name: Submit button variable name
        :param anchor_to_closest_element: Anchor to the closest entry
        :param method: Method to send information (get, post ..)
        :type var_name: String
        :type anchor_to_closest_element: String
        :type method: String
        :returns: HTML code for save and delete bar 
        :rtype: String
        """
        s = generate_an_option("Save", var_name, anchor_to_closest_element) +\
            generate_an_option("Delete", var_name, anchor_to_closest_element)
        return s

    def generate_like_options(self, 
                              var_name, 
                              anchor_to_closest_element):
        """
        Generate HTML code to create  radio and submit button for 
        Like/Dislike/Ignore options.
        :param self: self
        :param var_name: Variable name.
        :type var_name: String.
        :returns: HTML code to generate radio and submit button
        :rtype: String.
        """
        s = ''.join(
                [
                    generate_an_option(an,
                        var_name,
                        anchor_to_closest_element)
                    for an in ["Like", "Dislike"]
                ])
        return s

    def extract_chosen_preference_and_feed_from_path(self):
        """
        Extract the desired RSS feed from the path
        :returns: Chosen feed.
        :rtype: String.
        """
        splitted_path = self.path.split("/")
        if len(splitted_path) >= 2:
            preference = splitted_path[-2]
            feed_chosen = self.path.split("/")[-1]
            feed_chosen = feed_chosen.split("?")[0]
        else:
            preference = self.path.split("/")[-1]
            feed_chosen = ""
        return preference,feed_chosen

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
            session_dict = shelve(self.server.previous_session)
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
                    session_dict.close()
                if preference in ["Delete"]:
                    session_dict["preferences"][self.server.current_preference_folder][feed_name].pop(index)
                    session_dict.close()
                if preference == "Save":
                    entry = session_dict["preferences"][self.server.current_preference_folder][feed_name][index]
                    file_save = open(feed_name+"_saved_entries.html", "a")
                    file_save.write(represent_rss_entry(entry, component))
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
        """
        Generates HTML separator between entries
        :returns: Separator between entries HTML code
        :rtype: String
        """
        return to_span("entries_separator", "<br>\n<hr>\n")

    def update_feed_or_preference_folder(self):
        """
        Updates the values for server.feed_chosen or server.current_preference_folder
        according to the values of the path
        """
        preference,feed = self.extract_chosen_preference_and_feed_from_path()
        session_dict = shelve(self.server.previous_session)
        if preference in session_dict["preferences"].keys():
            self.server.current_preference_folder = preference
            self.server.feed_chosen = ""
        if feed in self.server.feeds_url_dict.keys():
            self.server.feed_chosen = feed
        session_dict.close()

    def get_closest_element_anchor(self, keys, key_id, feed_chosen):
        """
        Retieve a HTML anchor to the closest entry 
        :param keys: List of entries identifiers
        :param key_id: Current entry identifier
        :param feed_chosen: Current chosen feed
        :type keys: List
        :type key_id: String
        :type feed_chosen: String
        :returns: HTML anchor to the closest entry
        :rtype: String
        """
        if key_id == len(keys) - 1:
            return to_anchor(feed_chosen+"_"+keys[key_id - 1])
        return to_anchor(feed_chosen+"_"+keys[key_id + 1])

    def do_GET(self):
        """
        Reaction to get method. If the requested element is the style, sends the css style.
        If it is an image sends the image. Otherwise, it reconstructs the webpage according
        to the changes and sent it to the client. 
        """
        self.send_response(200)
        mimetype, _ = mimetypes.guess_type(self.path)
        if ".css" in self.path:#== '/'+self.server.cssfile
            self.send_header('Content-type', mimetype)
            self.end_headers()
            self.wfile.write(file_to_str(self.server.cssfile))
        elif mimetype is not None and "image" in mimetype:
            imfile = self.path.split("/")[-1]
            imfile = os.path.join(self.server.icons_folder, imfile)
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
            self.wfile.write('<body>\n')
            # Generate preferences menu
            session_dict = shelve(self.server.previous_session)
            preference_menu_keys = session_dict["preferences"].keys()
            preference_menu = ""
            for preference in preference_menu_keys:
                dict_feeds = session_dict["preferences"][preference]
                feeds_menu_keys = dict_feeds.keys()
                menu_element = self.generate_feeds_menu(feeds_menu_keys,
                                                        drop_button_name=preference,
                                                        drop_button_text=preference,
                                                        div_name="dropdown"+preference,
                                                        button_function="myFunction"+preference+"()",
                                                        dropdown_ID="myDropdown"+preference,
                                                        filter_function="filterFunction"+preference+"()",
                                                        input_name="myInput"+preference)
                
                """
                if preference == self.server.current_preference_folder:
                    menu_element = to_span("selected_link", menu_element)
                else:
                    menu_element = to_span("unselected_link", menu_element)
                
                menu_element = to_div(preference+"menu",menu_element)
                """
                preference_menu += menu_element

            toggle_images_link = generate_link("#", "Toggle images", "javascript:imtoggle()")
            toggle_images_link = to_span("toggle_images", toggle_images_link)
            preference_menu += toggle_images_link
            train_link = generate_link("/Train", "Train and bring news")
            train_link = to_span("train", train_link)
            preference_menu += train_link
            self.wfile.write(preference_menu)
            # Generate feeds menu in the current preference menu
            current_preference = self.server.current_preference_folder
            dict_feeds = session_dict["preferences"][current_preference]
            feeds_menu_keys = dict_feeds.keys()
            self.wfile.write(to_header(1,current_preference))
            feed_chosen = self.server.feed_chosen
            self.wfile.write(to_header(2,self.server.correct_feed_name_to_text(feed_chosen)))
            self.wfile.write(self.generate_entry_separator())
            session_dict.close()
            
            if "Train" in self.path:
                self.server.update_session()
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

                    opts = self.generate_save_delete_option(id_entry, anchor) # always show save and delete
                    if self.server.current_preference_folder == self.server.home:
                        # in this case add Like/Dislike
                        opts = "{1} &nbsp; {0}".format(
                                opts,
                                self.generate_like_options(id_entry, anchor)
                        )
                    self.wfile.write(opts)
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
                 maximal_number_of_entries,
                 icons_folder):
        """
        Generates an instance for HTTPServerFeeds that inheritates from
        HTTPServer class.
        :param server_address: Server adress, paramater required by HTTPServer.
        :param HTTPServer_RequestHandler: HTTPServer_RequestHandler required by
        HTTPServer.
        :param cssfile: CSS file.
        :param feeds_url_dict: Dictionnary with feed urls and names.
        :param previous_session: File name for shelve object that stores the session
        :param word_counts_database_file: File name for object storing the word counts
        :param stopwords_file: File name for list of stopwords
        :param maximal_number_of_entries: Maximal number of entries allowed
        :param icons_folder: Icons folder
        :type server_address: Tuple.
        :type HTTPServer_RequestHandler: HTTPServer_RequestHandler class.
        :type cssfile: String.
        :type feeds_url_dict: Dict.
        :type previous_session: String
        :type word_counts_database_file: String
        :type stopwords_file: String 
        :type maximal_number_of_entries: Int
        :type icons_folder: String
        """
        HTTPServer.__init__(self, server_address, HTTPServer_RequestHandler)
        self.home = "Home"
        self.like = "Like"
        self.cssfile = cssfile
        self.feeds_url_dict = self.correct_names_feed_url_dict(feeds_url_dict)
        self.previous_session = previous_session
        self.current_preference_folder = self.home
        self.feed_chosen = ""
        self.icons_folder = icons_folder
        self.nayesdog = naylib.NaiveBayes(word_counts_database_file,
                                          stopwords_file,
                                          maximal_number_of_entries)
        self.update_session()

    def correct_names_feed_url_dict(self, feeds_url_dict):
        feeds_url_dict_correct = {}
        for key,url in feeds_url_dict.iteritems():
            feed_name = self.correct_feed_name(key)
            feeds_url_dict_correct[feed_name] = url
        return feeds_url_dict_correct

    def update_session(self):
        """
        Update session feeds, entries and entries scores
        """
        session_dict = shelve(self.previous_session)
        self.initialize_shelve_structure(session_dict)
        self.initialize_each_seen_entry_as_useless(session_dict["seen_entries_keys"])
        for feed in self.feeds_url_dict:
            feed_url = self.feeds_url_dict[feed]
            if feed_url in session_dict["feed_url_names"]:
                old_feed_name = session_dict["feed_url_names"][feed_url]
                if feed != old_feed_name:
                    self.change_feed_name_session_dict(session_dict, old_feed_name, feed)
            session_dict["feed_url_names"][feed_url] = feed
            received_entries = preprocess_feed(feed_url)
            for key, entry in received_entries.iteritems():
                if feed not in session_dict["preferences"][self.home]:
                    session_dict["preferences"][self.home][feed] = {}
                if key not in session_dict["seen_entries_keys"]:
                    session_dict["preferences"][self.home][feed][key] = entry
                session_dict["seen_entries_keys"][key] = 1
            self.predict_entries_in_dict(session_dict["preferences"][self.home][feed])
        self.filter_url_feeds(session_dict)
        self.filter_previous_session_file_after_config_update(session_dict)
        self.prune_useless_stored_entries_keys(session_dict["seen_entries_keys"])
        session_dict.close()

    def filter_url_feeds(self, session_dict):
        feeds_url_config = [url for url in self.feeds_url_dict.values()]
        for url in session_dict["feed_url_names"].keys():
            if url not in feeds_url_config:
                session_dict["feed_url_names"].pop(url)

    def initialize_shelve_structure(self, session_dict):
        if "preferences" not in session_dict:
            session_dict["preferences"] = {}
        if "seen_entries_keys" not in session_dict:
            session_dict["seen_entries_keys"] = {}
        if "feed_url_names" not in session_dict:
            session_dict["feed_url_names"] = {}
        if self.like not in session_dict["preferences"]:
            session_dict["preferences"][self.like] = {}
        if self.home not in session_dict["preferences"]:
            session_dict["preferences"][self.home] = {}

    def change_feed_name_session_dict(self, session_dict, old_name, new_name):
        if old_name in session_dict["preferences"][self.home]:
            session_dict["preferences"][self.home][new_name] = session_dict["preferences"][self.home].pop(old_name)
        if old_name in session_dict["preferences"][self.like]:
            session_dict["preferences"][self.like][new_name] = session_dict["preferences"][self.like].pop(old_name)

    def initialize_each_seen_entry_as_useless(self, seen_entries_keys):
        """
        Initialize each entry in list as useless
        :param seen_entries_keys: List of entries that are in memory
        :type seen_entries_keys: list
        """
        for key in seen_entries_keys:
            seen_entries_keys[key] = 0

    def prune_useless_stored_entries_keys(self,seen_entries_keys):
        """
        Prune old erased entries from list of entries
        :param seen_entries_keys: List of entries that are in memory
        :type seen_entries_keys: list        
        """
        for key in seen_entries_keys.keys():
            if not seen_entries_keys[key]:
                seen_entries_keys.pop(key)

    def rank_entries_by_preference(self,dict_entries):
        """
        Get entries id ranked by preference.
        :param dict_entries: Dict of entries
        :type dict_entries: Dict
        :returns: List of entries ids ranked by preference
        :rtype: List
        """
        get_prediction_from_entry = lambda k: dict_entries[k]["prediction"]
        ranks = sorted(dict_entries, key=get_prediction_from_entry, reverse=True)
        return ranks

    def predict_entries_in_dict(self,dict_entries):
        """
        Predicts entries preference with Naive Bayesian algorithm
        :param dict_entries: Dict of entries
        :type dict_entries: Dict
        """
        for key,entry in dict_entries.iteritems():
            x = tranform_feed_entry_to_bag_of_words(entry)
            dict_entries[key]["prediction"] = self.nayesdog.predict(x)

    def filter_previous_session_file_after_config_update(self,session_dict):
        """
        Update session Dictionnary to take into account modifications in config file
        :param session_dict: Dict of session
        :type session_dict: Dict
        """
        for k in session_dict['preferences'].keys():
            for kfeed in session_dict['preferences'][k].keys():
                if kfeed not in self.feeds_url_dict.keys():
                    session_dict['preferences'][k].pop(kfeed)

    def correct_feed_name(self,name):
        correct_name = name.split()
        correct_name = "%20".join(correct_name)
        return correct_name

    def correct_feed_name_to_text(self,name):
        correct_name = name.split("%20")
        correct_name = " ".join(correct_name)
        return correct_name

def run(server_address=None,
        cssfile=None,
        feeds_url_dict=None,
        previous_session_database_file=None,
        word_counts_database_file=None,
        stopwords_file=None,
        maximal_number_of_entries_in_memory=None,
        icons_folder=None,
        HTTPServer_RequestHandler_feeds=HTTPServer_RequestHandler_feeds):
    httpd = HTTPServerFeeds(server_address,
                            HTTPServer_RequestHandler_feeds,
                            cssfile,
                            feeds_url_dict,
                            previous_session_database_file,
                            word_counts_database_file,
                            stopwords_file,
                            maximal_number_of_entries_in_memory,
                            icons_folder)
    print('running server...')
    httpd.serve_forever()
