server_address = ('127.0.0.1', 8081)
cssfile = 'css.css'
"""
feeds_url_dict = {
    'Nrsrch': 'http://feeds.nature.com/NatureLatestResearch',
    'Ncrrnt': 'http://feeds.nature.com/nature/rss/current',
    'Nnw': 'http://feeds.nature.com/NatureNewsComment',
    'Stwis': 'http://science.sciencemag.org/rss/twis.xml',
    'Snw': 'https://www.sciencemag.org/rss/news_current.xml',
    'AT': 'http://feeds.arstechnica.com/arstechnica/index?format=xml',
    'ATsc': 'http://feeds.arstechnica.com/arstechnica/science',
    'ATftrs': 'http://feeds.arstechnica.com/arstechnica/features',
    'MIT': 'https://www.technologyreview.com/topnews.rss',
    'IEEE': 'http://spectrum.ieee.org/rss/fulltext',
    'Reddit': 'https://www.reddit.com/r/worldnews/.rss',
}
"""
feeds_url_dict = {
    'NatureResearch': 'http://feeds.nature.com/NatureLatestResearch',
    'Arstechnica': 'http://feeds.arstechnica.com/arstechnica/science',
    'Science': 'http://www.sciencemag.org/rss/current.xml',
}
word_counts_database_file = './tables.py.gz'
stopwords_file = './stopwords.txt'
previous_session_database_file = '.previous_session'
maximal_number_of_entries_in_memory = 300
