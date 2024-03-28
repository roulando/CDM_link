import os

import pandas as pd

from nltk import ngrams
from abc import ABC, abstractmethod
from tqdm import tqdm

class Padding(ABC):

    @abstractmethod
    def __call__(self, str):
        pass

def read_medmentions_set_reports_nr(set_nr_pach):
    nr_set = set()

    with open(set_nr_pach, 'r', encoding='utf-8') as f:
        while True:
            line = f.readline()

            if len(line )>0:
                nr_set.add(int(line[:-1]))
            else:
                break
    return nr_set

def read_seperate_medmentions_data(pandas_table,train_nr_set, test_nr_set):
    train_data = []
    test_data = []

    for i,row in tqdm(pandas_table.iterrows(), total=len(pandas_table)):
        id = row['CUI']
        report_nr = row['report_nr']
        
        if pd.isna(row['mention']):
            continue
        else:
            mention = row['mention'].lower()
        sample = dict(id = id, mention = mention)
        
        if report_nr in train_nr_set:
            train_data.append(sample)
        elif report_nr in test_nr_set:
            test_data.append(sample)
    return train_data, test_data    

