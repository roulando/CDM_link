from utils import add_to_dict_values_list
from tqdm import tqdm
import sqlite3

class Ontology(dict):
    def delete_duplicate(self, keep_for_empty = True):
        synonyms = {}
        for key, names in self.items():
            for n in names:
                add_to_dict_values_list(synonyms, n, key)
        
        for key in self.keys():
            cleared_synonyms = []

            for n in self[key]:
                if len(synonyms[n]) == 1:
                    cleared_synonyms.append(n)
            
            if len(cleared_synonyms) != 0 or not keep_for_empty:
                self[key]= cleared_synonyms
            
    def generate_cache(self,function_to_encode):
        onto_cache = []
        for names in self.values():
            c_xs = []
            for n in names:
                c_xs.append(function_to_encode(n))
            onto_cache.append((names,c_xs))
        return onto_cache
    
    def merge_lookup(self,data, add_unkown = False):
        for key, names in data.items():
            if key in self:
                onto_names = self[key]
                for n in names:
                    if n not in onto_names:
                        onto_names.append(n)
            elif add_unkown:
                self[key] = names

class OntologieBC5CDR(Ontology):
    def __init__(self, data, padding = lambda x: x):
        ontology = {}
        
        for sample in tqdm(data):
            cui = sample['id']
            
            sample_names = []
            for n in sample['names']:
                n = padding(n.lower())
                if not n in sample_names:
                    sample_names.append(n)
            ontology[cui] = sample_names

        super().__init__(ontology)

class OntologieSHARE(Ontology):
    def __init__(self, data, padding = lambda x: x):
        ontology = {}
        if not isinstance(data, list) or len(data)!=0:
            for sample in tqdm(data):
                cui = sample['cui']
                
                sample_names = []
                for n in [sample['title']] + sample['synonyms']: #todo fix that shit!!!
                    n = padding(n.lower())
                    if not n in sample_names:
                        sample_names.append(n)
                ontology[cui] = sample_names

        super().__init__(ontology)

class OntologieNCBI(Ontology):
    def __init__(self, data, padding = lambda x: x):
        ontology = {}
        if not isinstance(data, list) or len(data)!=0:
            for sample in tqdm(data):
                cui = sample['id']
                #assert not cui in cuis, "There is something wrong with the data"
                
                sample_names = []
                for n in sample['names']:
                    n = padding(n.lower())
                    if not n in sample_names:
                        sample_names.append(n)
                ontology[cui] = sample_names

        super().__init__(ontology)