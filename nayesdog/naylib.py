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
import os
from collections import OrderedDict
from math import log, exp as mexp
from simpleshelve import save_object_simple, load_object_simple
from doglib import file_to_str

#from config import make_me_config
#exec(make_me_config())
#from config import word_counts_database_file, stopwords_file


EPS = 1e-12
constPx = 1e-3 # prob to have a word in an item
NUMCLASSES = 2

def exp(x):
    return mexp(x) if x<200 else mexp(200)


class NaiveBayes:

    def __init__(self,
                 word_counts_database_file,
                 stopwords_file,
                 maximal_number_of_entries,
                 num_classes=NUMCLASSES):
        self.stopwords = set(file_to_str(stopwords_file).split('\n'))
        self.maximal_number_of_entries = maximal_number_of_entries
        self.num_classes = num_classes
        self.word_counts_database_file = word_counts_database_file
        if os.path.isfile(self.word_counts_database_file):
            self.table = load_object_simple(self.word_counts_database_file)
        else:
            self.table = self.create_empty_tables()

    def create_empty_tables(self):
        tables = {'word_counts': OrderedDict(),
                  'sum_for_classes': [0.0]*self.num_classes,
                  'bag_words_in_memory': [],
                  'insertion_index':0}
        return tables
    
    def save_tables(self):
        save_object_simple(self.word_counts_database_file, self.table)

    def sort_word_tables(self):
        # sort word_counts table based on log(P(y|x)-log(P(y))
        self.table['word_counts'] = OrderedDict(
            sorted(
                self.table['word_counts'].items(),
                key=lambda x: self.compute_probabilities_one_entry(
                    x[0],
                    mode='log(P(y|x)-log(P(y))'
                )
            )
        )

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
            x, y = self.table['bag_words_in_memory'][insertion_index]
            for word in x:
                self.table['word_counts'][word][y] -= 1
                self.table['sum_for_classes'][y] -= 1
                if not self.table['word_counts'][word][y]:
                    self.table['word_counts'].pop(word)

    def insert_new_entry(self, x, y):
        for word in x:
            if word not in self.stopwords:
                if word in self.table['word_counts'].keys():
                    self.table['word_counts'][word][y] += 1.0
                    self.table['sum_for_classes'][y] += 1.0
                else:
                    self.table['word_counts'][word] = [1.0]*self.num_classes
                    self.table['sum_for_classes'] = list(map(lambda x: x+1.0, self.table['sum_for_classes']))
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
        self.sort_word_tables()
        self.save_tables()

    def predict(self, X):
    
        if isinstance(X[0],list):
            Y_predicted = []
            for x in X:
                y_predicted = self.compute_probabilities_one_entry(x)
                Y_predicted.append(y_predicted)
            return Y_predicted
        return self.compute_probabilities_one_entry(X)

    def compute_probabilities_one_entry(self, x,
            mode=['P(y|x)',
                  'log(P(y|x)-log(P(y))',
                  'log(P(y=a|x)-log(P(y=b|x)',
                  'log(P(y|x))'
                 ][2], # string or list of strings
            ab=(1,0) # used only when mode=="log_P_a_x-log_P_b_x"
            ):
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
        allowed=['P(y|x)',
                 'log(P(y|x)-log(P(y))',
                 'log(P(y=a|x)-log(P(y=b|x)',
                 'log(P(y|x))'
                ]
        word_counts = self.table["word_counts"]
        sum_for_classes = self.table["sum_for_classes"]
        outputs = {k:{} for k in allowed}
        total_nb_words = sum(sum_for_classes)

        total_per_word = dict()
        for word,counts in word_counts.items():
            total_per_word[word] = sum(counts)

        #import ipdb; ipdb.set_trace()

        words = set(word_counts.keys())

        for y in range(self.num_classes):

            log_prod_P_xi_y = 0.0
            log_P_x = 0.0
            at_least_one_known_word = False

            for word in x:
                if word in words:
                    if sum_for_classes[y] != 0:
                        at_least_one_known_word = True
                        log_prod_P_xi_y += log( EPS + word_counts[word][y] / sum_for_classes[y] )
                        if total_per_word[word] != 0:
                            log_P_x += log( EPS + total_per_word[word] / total_nb_words )

            if not at_least_one_known_word:
                outputs['log(P(y|x))'][y] = log( EPS )
                outputs['P(y|x)'][y] = 0.0
                outputs['log(P(y|x)-log(P(y))'][y] = log_prod_P_xi_y - log_P_x
            else:
                outputs['log(P(y|x))'][y] = log( EPS + sum_for_classes[y] / total_nb_words ) + log_prod_P_xi_y - log_P_x
                outputs['P(y|x)'][y] = exp( outputs['log(P(y|x))'][y] )
                outputs['log(P(y|x)-log(P(y))'][y] = log_prod_P_xi_y - log_P_x

        outputs['log(P(y=a|x)-log(P(y=b|x)'] = outputs['log(P(y|x))'][ab[0]] - outputs['log(P(y|x))'][ab[1]]
        if isinstance(mode, list):
            return [outputs[m] for m in mode]
        else:
            if mode == 'all':
                return outputs
            else:
                return outputs[mode]
