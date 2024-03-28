import numpy as np

from multiprocessing import Pool, Queue, Manager
from tqdm import tqdm

from src.process.utils import generate_index_lists
from src.process.dist_functions import CDM_gzip
from src.utils import add_to_dict_values_list

_onto = None
_test_data = None
_queue = None 
_dist_function = None 
_results_list = None


def insert_results(results, new_score, index):
    if new_score > results[-1][0]:
        return
    elif new_score < results[0][0]: 
        results.insert(0, (new_score,index))
        results.pop()
        return
    else:
        for i in range(1, len(results)):
            if new_score < results[i][0]:
                results.insert(i, (new_score,index))
                results.pop()
                return

def process_test_data(sample_ids):
    global _results_list

    dummy_list = _results_list[0].copy()
    for i_s in sample_ids:
        results = dummy_list.copy()
        mention, mention_c_x = _test_data[i_s]
        for index_onto, (names, name_c_x) in enumerate(_onto):
            min_score = 1.
            for n, c_n in zip(names, name_c_x):
                dist = _dist_function(mention, n, c_x1 = mention_c_x, c_x2 = c_n)
                min_score = dist if dist < min_score else min_score

            insert_results(results, min_score, index_onto)
        
        _results_list[i_s] = results
        if _queue:
            _queue.put(1)

class MultiProcess():
    def __init__(self,onto, dist_function = CDM_gzip()):
        global _dist_function
        _dist_function = dist_function
        self.onto = onto

    def map_results_to_ids(self,results, test_data):
        top_set = [0] * len(results[0])
        
        onto_keys_i = {} 
        
        for index_o, key in enumerate(self.onto.keys()):  
            onto_keys_i[key] = index_o
        
        n_total_samples = 0
        id_labels = list(test_data.values())  
        for index, r_top_scores in enumerate(results):
            for id in id_labels[index]:
                n_total_samples +=1
                r_top_labels = [r_t_s[1] for r_t_s in r_top_scores]
                
                def check_where_label(index_o, r_top):
                    return np.where(np.asarray(r_top)==index_o)[0][0]
                correct_label_pos = None
                if isinstance(id, list): #some datasets have multiple labels per sample
                    for i_d in id:
                        if i_d in onto_keys_i:
                            index_o = onto_keys_i[i_d]
                            if index_o in r_top_labels:
                                id_pos_r_top = check_where_label(index_o, r_top_labels)
                                correct_label_pos = id_pos_r_top if not correct_label_pos or id_pos_r_top<correct_label_pos else correct_label_pos
                elif id in onto_keys_i:
                    index_o = onto_keys_i[id]
                    if index_o in r_top_labels:
                        correct_label_pos = check_where_label(index_o, r_top_labels)
                
                if not correct_label_pos is None: 
                    for k in range(correct_label_pos, len(top_set)):
                        top_set[k] +=1
        
        return top_set,n_total_samples

    def process(self, test_data , n_process=30, print_bar = True, top_k = 1):
        global _test_data
        global _onto
        global _queue
        global _results_list

        _test_data = test_data.generate_cache(_dist_function.encode_single)
        _onto = self.onto.generate_cache(_dist_function.encode_single)

        index_lists = generate_index_lists(len(_test_data), n_process)

        if print_bar:
            _queue = Queue()
            pbar = tqdm(total=len(_test_data)) 
        else:
            _queue = None
        
        #create variable for results
        manager = Manager()
        _results_list = manager.list()

        for _ in range(len(_test_data)):
            _results_list.append([(1., -1) for _ in range(top_k)])

        with Pool(n_process) as p:
            p.map_async(process_test_data, index_lists)

            if print_bar:
                for _ in range(len(_test_data)):
                    _queue.get()
                    pbar.update()
            p.close()
            p.join()
            if print_bar:
                pbar.close()

        _results_list = list(_results_list)
        
        return _results_list
    
