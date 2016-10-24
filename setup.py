from distutils.core import setup
setup(
    name = 'nayesdog',
    packages = ['nayesdog'],
    version = '0.1.1.0',
    description = 'RSS reader with Naive Bayes powered recommendations',
    author = 'Ilya Prokin, Sergio Peignier',
    author_email = 'isprokin@gmail.com, sergio.peignier.zapata@gmail.com',
    url = 'http://github.com/MLdog/nayesdog',
    download_url ='http://github.com/MLdog/nayesdog/tarball/0.1',
    keywords = ['RSS reader', 'Naive Bayes', 'recommendations'],
    classifiers = [],
    package_data = {'nayesdog':['icons/*','css.css','stopwords.txt']},
    scripts=['nayesdog/NayesDog'],
)
#    entry_points={
#        'console_scripts':[
#            'nayesdog = nayesdog.nayesdog:main_func'
#        ]
#    }