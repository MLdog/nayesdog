import os
from collections import OrderedDict
from math import log, exp as mexp
from simpleshelve import save_object_simple, load_object_simple
from doglib import file_to_str, transform_feed_dict

from config import word_counts_database_file, stopwords_file
#from simpleshelve import SimpleShelve


EPS = 1e-12
constPx = 1e-3 # prob to have a word in an item
MAXNBENTRIES = 300

def exp(x):
    return mexp(x) if x<200 else mexp(200)



# def classify_new_one(word_counts, sum_dict, words):
#     Ps = dict(
#         y=dict(),
#         yx=dict(),
#         Pixy=dict()
#     )
#     Ps['x'] = constPx
#     sum_dict = {k:float(v) for k,v in sum_dict.items()} # to let division work in python2.7
#     total = sum(sum_dict.values())
# 
#     # estimate Px. It migh be better to just fix it to >0 <1
#     # tn = 1.0
#     # for w in words:
# 
#     #     wc = 0.0 # word conut across labels
#     #     for label in word_counts.keys():
#     #         if w in word_counts[label]:
#     #             wc += word_counts[label][w]
# 
#     #     if wc != 0: # otherwise no real info so do not update
#     #         Ps['x'] *= wc # assuming independence
#     #         tn *= total
#     # Ps['x'] /= tn
# 
#     for label in word_counts.keys():
# 
#         Ps['Pixy'][label] = 1.0
#         sm = 1.0
#         for w in words:
#             if w in word_counts[label]:
#                 Ps['Pixy'][label] *= word_counts[label][w]
#                 sm *= sum_dict[label]
#         
#         Ps['Pixy'][label] /= sm
# 
#         Ps['y'][label] = sum_dict[label] / total
# 
#         Ps['yx'][label] = Ps['y'][label] * Ps['Pixy'][label] / Ps['x']
# 
#     return Ps
# 
# 
# def classify_new_one_log(word_counts, sum_dict, words):
#     # First Ps are logP, they they are P
#     Ps = dict(
#         y=dict(),
#         yx=dict(),
#         Pixy=dict()
#     )
#     Ps['x'] = log( constPx )
# 
#     sum_dict = {k:float(v) for k,v in sum_dict.items()} # to let division work in python2.7
#     total = sum(sum_dict.values())
# 
#     # estimate Px. It migh be better to just fix it to >0 <1
#     #for w in words:
# 
#     #    wc = 0.0 # word conut across labels
#     #    for label in word_counts.keys():
#     #        if w in word_counts[label]:
#     #            wc += word_counts[label][w]
# 
#     #    Ps['x'] += log( EPS + wc ) - log ( EPS + total ) # assuming independence 
# 
#     for label in word_counts.keys():
# 
#         Ps['Pixy'][label] = 0.0
#         for w in words:
#             if w in word_counts[label]:
#                 Ps['Pixy'][label] += log( EPS + word_counts[label][w] ) - log( EPS + sum_dict[label] )
# 
#         Ps['y'][label] = log( EPS + sum_dict[label] ) - log ( EPS + total )
# 
#         Ps['yx'][label] = Ps['y'][label] + Ps['Pixy'][label] - Ps['x']
# 
#     # convert logP to P
#     Ps['x'] = exp( Ps['x'] )
#     for key in ['y', 'yx', 'Pixy']:
#         Ps[key] = {k:exp(v) for k,v in Ps[key].items()}
# 
#     return Ps


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
        
        Ps['y'][label] = sum_dict[label] / total
        
        # sanity check:
        # if all words were never seen before then Pixy is set to 0
        if Pixy_numerator == Pixy_denominator == 1.0:
            Ps['Pixy'][label] = 0.0
            Ps['yx'][label] = 0.0
        else:
            Ps['Pixy'][label] = Pixy_numerator / Pixy_denominator
            Ps['yx'][label] = sum_dict[label]*Pixy_numerator / ( Ps['x'] * total * Pixy_denominator )

    return Ps

class NaiveBayes:

    def __init__(self,
                 db_file=word_counts_database_file,
                 stopwordsfile=stopwords_file,
                 maximal_number_of_entries=MAXNBENTRIES):
        self.db_file = db_file
        if os.path.isfile(self.db_file):
            self.table = load_object_simple(self.db_file)
        else:
            self.table = self.create_empty_tables()
        self.stopwords = set(file_to_str(stopwordsfile).split('\n'))
        self.maximal_number_of_entries = maximal_number_of_entries

    def create_empty_tables(self):
        tables = {'word_counts': {0: OrderedDict(),
                                  1: OrderedDict()},
                  'sum_dict': {0: 0,
                               1: 0},
                  'bag_words_in_memory': [],
                  'insertion_index':0}
        return tables
    
    def save_tables(self):
        save_object_simple(self.db_file, self.table)

    def fit_from_feed(self, d, labels):
        d_idstxts = transform_feed_dict(d)
        for k in d_idstxts.keys():
            if k in labels.keys():
                for word in d_idstxts[k]:
                    if word not in self.stopwords:
                        if word in self.table['word_counts'][labels[k]].keys():
                            self.table['word_counts'][labels[k]][word] += 1
                            self.table['sum_dict'][labels[k]] += 1
                        else:
                            self.table['word_counts'][labels[k]][word] = 0

    def fit(self, X, Y):
        if isinstance(X[0],list):
            for i,x in enumerate(X):
                y = Y[i]
                self.insert_new_entry(x,y)
        else:
            self.insert_new_entry(X,Y)

    def remove_oldest_entry(self):
        insertion_index = self.table['insertion_index']
        if insertion_index < len(self.table["bag_words_in_memory"]):
            x,y = self.table['bag_words_in_memory'][insertion_index]
            for word in x:
                if word not in self.stopwords:
                    self.table['word_counts'][y][word] -= 1
                    self.table['sum_dict'][y] -= 1
                    if not self.table['word_counts'][y][word]:
                        self.table['word_counts'][y].pop(word)

    def insert_new_entry(self, x, y):
        for word in x:
            if word not in self.stopwords:
                if word in self.table['word_counts'][y].keys():
                    self.table['word_counts'][y][word] += 1
                    self.table['sum_dict'][y] += 1
                else:
                    self.table['word_counts'][y][word] = 1
                    self.table['sum_dict'][y] += 1
        insertion_index = self.table['insertion_index']
        self.remove_oldest_entry()
        if insertion_index < len(self.table["bag_words_in_memory"]):
            self.table['bag_words_in_memory'][insertion_index] = (x[:], y)
        else:
            self.table['bag_words_in_memory'].append((x[:],y))
        insertion_index += 1
        if insertion_index >= self.maximal_number_of_entries:
            insertion_index = 0
        self.table['insertion_index'] = insertion_index
        self.save_tables()

    def predict(self, X, Y=None):
    
        if isinstance(X[0],list):
            Y_predicted = []
            for x in X:
                y_predicted = self.compute_probabilities_one_entry(x)
                Y_predicted.append(y_predicted)
            return Y_predicted
        return self.compute_probabilities_one_entry(X)
        """
        return classify_new_one_optimized(
                self.table['word_counts'],
                self.table['sum_dict'],
                X
        )
        """

    def compute_probabilities_one_entry(self,x):
        """
        Compute the probabilities that the given entry belongs to each one of
        the existing classes. P_x denote here the probability to observe the
        set of words x. P_y_x denotes the probability that the entry belongs to
        class y given the set of words x it contains. 
        :param x: Bag of words
        :type x: List of Strings
        :returns: Probabilities of membership of the current entry to each one
        of the possible classes
        :rtype: Dict.
        """
        word_counts = self.table["word_counts"]
        sum_dict = self.table["sum_dict"]
        P_x = constPx
        P_y_x = {}
        total_nb_words = sum(sum_dict.values())
        for y in word_counts.keys():
            prod_P_xi_y_numerator = 1.0
            prod_P_xi_y_denominator = 1.0
            for word in x:
                if word in word_counts[y]:
                    prod_P_xi_y_numerator *= word_counts[y][word]
                    prod_P_xi_y_denominator *= sum_dict[y]
            if prod_P_xi_y_denominator == prod_P_xi_y_numerator == 1.0:
                P_y_x[y] = 0.0
            else:
                P_y_x_numerator = sum_dict[y] * prod_P_xi_y_numerator  
                P_y_x_denominator = prod_P_xi_y_denominator * total_nb_words * P_x
                P_y_x[y] = P_y_x_numerator * 1./P_y_x_denominator   
        return P_y_x

