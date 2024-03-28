import json
import io
import os

import pandas as pd

from datetime import datetime

def add_to_dict_values_list(dict, key ,data):
    if key in dict:
        dict[key].append(data)
    else:
        dict[key] = [data]

def read_json(path):
    samples = []

    with io.open(path, mode="r", encoding="utf-8") as file:
        for line in file:
            samples.append(json.loads(line.strip()))

    return samples


def decode_results_to_pandas_table(results_list, onto, test_set):
    results_table = []

    mention_l = list(test_set.keys())
    onto_id = list(onto.keys())
    for i_test, r in enumerate(results_list):
        r = r[0] #take top 1
        results_table.append((mention_l[i_test], onto_id[r[1]], r[0]))
    
    return pd.DataFrame(results_table,
        columns=['mention', 'onto id', "score"]
    )

def create_log_folder_current_time(log_dir = "./log", prefix = "CDM"):
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    current_log_dir = os.path.join(log_dir, prefix+"::"+datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S"))
    if not os.path.exists(current_log_dir):
        os.mkdir(current_log_dir)
    return current_log_dir

def create_results_str(top_set,n_total_samples ):
    text= f"Matched {top_set[0]} out of {n_total_samples}\n\n"
    
    for k,t in enumerate(top_set):
        text += f"top {k+1} acc of:  {t/n_total_samples}\n"
    return text