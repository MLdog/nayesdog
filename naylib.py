from collections import OrderedDict
from math import log, exp as mexp
EPS = 1e-6

def exp(x):
    return mexp(x) if x<100 else mexp(100)

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
        x=1.0,
        yx=dict(),
        Pixy=dict()
    )
    sum_dict = {k:float(v) for k,v in sum_dict.items()} # to let division work in python2.7
    total = sum(sum_dict.values())

    # estimate Px. It migh be better to just fix it to >0 <1
    tn = 1.0
    for w in words:

        wc = 0.0 # word conut across labels
        for label in word_counts.keys():
            if w in word_counts[label]:
                wc += word_counts[label][w]

        if wc != 0: # otherwise no real info so do not update
            Ps['x'] *= wc # assuming independence
            tn *= total
    Ps['x'] /= tn

    for label in word_counts.keys():

        Ps['Pixy'][label] = 1.0
        sm = 1.0
        for w in words:
            if w in word_counts[label]:
                Ps['Pixy'][label] *= word_counts[label][w]
                sm *= sum_dict[label]
        
        Ps['Pixy'][label] /= sm

        Ps['y'][label] = sum_dict[label] / total

        if Ps['x'] != 0.0:
            Ps['yx'][label] = Ps['y'][label] * Ps['Pixy'][label] / Ps['x']
        else:
            Ps['yx'][label] = None

    return Ps

def classify_new_one_log(word_counts, sum_dict, words):
    # First Ps are logP, they they are P
    Ps = dict(
        y=dict(),
        x=0.0,
        yx=dict(),
        Pixy=dict()
    )
    sum_dict = {k:float(v) for k,v in sum_dict.items()} # to let division work in python2.7
    total = sum(sum_dict.values())

    # estimate Px. It migh be better to just fix it to >0 <1
    for w in words:

        wc = 0.0 # word conut across labels
        for label in word_counts.keys():
            if w in word_counts[label]:
                wc += word_counts[label][w]

        Ps['x'] += log( EPS + wc / total ) # assuming independence 

    for label in word_counts.keys():

        Ps['Pixy'][label] = 0.0
        for w in words:
            if w in word_counts[label]:
                Ps['Pixy'][label] += log( EPS + word_counts[label][w] / sum_dict[label] )

        Ps['y'][label] = log( EPS + sum_dict[label] / total )

        Ps['yx'][label] = Ps['y'][label] + Ps['Pixy'][label] - Ps['x']

    # convert logP to P
    Ps['x'] = exp(Ps['x'])
    for key in ['y', 'yx', 'Pixy']:
        Ps[key] = {k:exp(v) for k,v in Ps[key].items()}

    return Ps

