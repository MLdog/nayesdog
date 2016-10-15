import os
from collections import OrderedDict
from math import log, exp as mexp
from simpleshelve import save_object_simple, load_object_simple
from doglib import file_to_str, transform_feed_dict
#from simpleshelve import SimpleShelve


EPS = 1e-10
constPx = 1e-3


def exp(x):
    return mexp(x) if x<200 else mexp(200)


def create_empty_word_count_table():
    return {
        0:OrderedDict(),
        1:OrderedDict()
    }


def update_word_count_tables(
        word_counts,
        sum_dict,
        d_idstxts,
        labels,
        stopwords):

    for k in d_idstxts.keys():
        if k in labels.keys():
            for word in d_idstxts[k]:
                if word not in stopwords:
                    if word in word_counts[labels[k]].keys():
                        word_counts[labels[k]][word] += 1
                        sum_dict[labels[k]] += 1
                    else:
                        word_counts[labels[k]][word] = 0


def classify_new_one(word_counts, sum_dict, words):
    Ps = dict(
        y=dict(),
        yx=dict(),
        Pixy=dict()
    )
    Ps['x'] = constPx
    sum_dict = {k:float(v) for k,v in sum_dict.items()} # to let division work in python2.7
    total = sum(sum_dict.values())

    # estimate Px. It migh be better to just fix it to >0 <1
    # tn = 1.0
    # for w in words:

    #     wc = 0.0 # word conut across labels
    #     for label in word_counts.keys():
    #         if w in word_counts[label]:
    #             wc += word_counts[label][w]

    #     if wc != 0: # otherwise no real info so do not update
    #         Ps['x'] *= wc # assuming independence
    #         tn *= total
    # Ps['x'] /= tn

    for label in word_counts.keys():

        Ps['Pixy'][label] = 1.0
        sm = 1.0
        for w in words:
            if w in word_counts[label]:
                Ps['Pixy'][label] *= word_counts[label][w]
                sm *= sum_dict[label]
        
        Ps['Pixy'][label] /= sm

        Ps['y'][label] = sum_dict[label] / total

        Ps['yx'][label] = Ps['y'][label] * Ps['Pixy'][label] / Ps['x']

    return Ps


def classify_new_one_log(word_counts, sum_dict, words):
    # First Ps are logP, they they are P
    Ps = dict(
        y=dict(),
        yx=dict(),
        Pixy=dict()
    )
    Ps['x'] = log( constPx )

    sum_dict = {k:float(v) for k,v in sum_dict.items()} # to let division work in python2.7
    total = sum(sum_dict.values())

    # estimate Px. It migh be better to just fix it to >0 <1
    #for w in words:

    #    wc = 0.0 # word conut across labels
    #    for label in word_counts.keys():
    #        if w in word_counts[label]:
    #            wc += word_counts[label][w]

    #    Ps['x'] += log( EPS + wc ) - log ( EPS + total ) # assuming independence 

    for label in word_counts.keys():

        Ps['Pixy'][label] = 0.0
        for w in words:
            if w in word_counts[label]:
                Ps['Pixy'][label] += log( EPS + word_counts[label][w] ) - log( EPS + sum_dict[label] )

        Ps['y'][label] = log( EPS + sum_dict[label] ) - log ( EPS + total )

        Ps['yx'][label] = Ps['y'][label] + Ps['Pixy'][label] - Ps['x']

    # convert logP to P
    Ps['x'] = exp( Ps['x'] )
    for key in ['y', 'yx', 'Pixy']:
        Ps[key] = {k:exp(v) for k,v in Ps[key].items()}

    return Ps


def classify_new_one_optimized(word_counts, sum_dict, words):
    Ps = dict(
        y=dict(),
        yx=dict(),
        Pixy=dict()
    )
    Ps['x'] = constPx
    sum_dict = {k:float(v) for k,v in sum_dict.items()} # to let division work in python2.7
    total = sum(sum_dict.values())

    for label in word_counts.keys():

        Pixy_numerator = 1.0
        Pixy_denominator = 1.0
        for w in words:
            if w in word_counts[label]:
                Pixy_numerator *= word_counts[label][w]
                Pixy_denominator *= sum_dict[label]
        
        Ps['Pixy'][label] = Pixy_numerator / Pixy_denominator

        Ps['y'][label] = sum_dict[label] / total

        Ps['yx'][label] = ( sum_dict[label]*Pixy_numerator ) / ( Ps['x'] * total * Pixy_denominator )

    return Ps


class NaiveBayes:

    db_file = './tables.py.gz'
    stopwordsfile = './stopwords.txt'

    def __init__(self, db_file=None):
        if db_file is not None:
            self.db_file = db_file
        if os.path.isfile(self.db_file):
            self.table = load_object_simple(self.db_file)
        else:
            self.table = {
                'wt': create_empty_word_count_table(),
                'st': {0:0, 1:0}
            }
        self.stopwords = set(file_to_str(self.stopwordsfile).split('\n'))

    def save_tables(self):
        save_object_simple(self.db_file, self.table)

    def fit(self, d, labels):
        d_idstxts = transform_feed_dict(d)
        update_word_count_tables(
                self.table['wt'],
                self.table['st'],
                d_idstxts,
                labels,
                self.stopwords
        )

    def predict(self, newitem):
        return classify_new_one_optimized(self.table['wt'], self.table['st'], newitem)


