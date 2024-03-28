import pickle
import os 
import rootutils

from argparse import ArgumentParser

rootutils.set_root(
    path=".", 
    project_root_env_var=True, 
    dotenv=True, 
    pythonpath=True, 
    cwd=True, 
) 

import src.process.dist_functions as dist_functions

from src.data.datasets import SHAREdataset, SHAREtrainlookup
from src.data.ontology import OntologieSHARE
from src.utils import read_json, decode_results_to_pandas_table, create_log_folder_current_time,create_results_str
from src.process.process import MultiProcess

def main(args):
    log_folder = './logs' if args.log_dir is None else args.log_dir
    log_prefix = 'SHARE'
    
    log_prefix+= ":"+args.dist_fun

    onto = OntologieSHARE(read_json(args.onto_path))
    onto.delete_duplicate()

    test_set = SHAREdataset(read_json(args.test_path), onto_keys=onto)
    
    if not args.train_path is None:
        log_prefix+= ":add_train_set"
        train_lookup = SHAREtrainlookup(read_json(args.train_path),onto_keys=onto)
        train_lookup.filter_out_dulpicates(keep_for_empty=False)
        onto.merge_lookup(train_lookup, add_unkown=False)
        
    processor = MultiProcess(onto, dist_function = getattr(dist_functions, args.dist_fun)()) 

    log_dir = create_log_folder_current_time(prefix=log_prefix, log_dir=log_folder)
    
    results_list = processor.process(test_set, top_k=args.top_k, n_process=args.n_processes)
    with open(os.path.join(log_dir, "raw_results.pkl"), 'wb') as f:
        pickle.dump(results_list, f) 
    
    decode_results_to_pandas_table(results_list, onto,test_set).to_csv(os.path.join(log_dir, "results_details.csv"))

    top_set, n_total_samples = processor.map_results_to_ids(results_list, test_set)

    with open(os.path.join(log_dir, "run_stats.txt"), 'w') as f:
        text = create_results_str(top_set, n_total_samples)
        print(text)
        f.write(text)

if __name__ == "__main__":
    parser = ArgumentParser()
    
    parser.add_argument("--onto_path", type=str, default="./data/share/onto.json")
    parser.add_argument("--train_path", type=str, default="./data/share/train.json")
    parser.add_argument("--test_path", type=str, default="./data/share/test.json")
    parser.add_argument("--log_dir", type=str, default=None)

    parser.add_argument("--dist_fun", type=str, default="CDM_gzip", help="Choose distance function with class name from src.process.dist_functions")
    parser.add_argument("--top_k", type=int, default=5)
    parser.add_argument("--n_processes", type=int, default=31)
    args = parser.parse_args()
    
    main(args)