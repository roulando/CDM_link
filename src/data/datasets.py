from utils import add_to_dict_values_list

class TestData(dict):
    def generate_cache(self, function_to_encode):
        mention_cache = []        
        for m in self.keys():
            mention_cache.append((m, function_to_encode(m)))
        return mention_cache
    
    def get_unique_ids(self):
        unique_ids = set()
        for ids in self.values():
            for id in ids:
                if isinstance(id,list):
                    for i in id:
                        unique_ids.add(i)
                else:
                    unique_ids.add(id)
        return unique_ids
    
class BC5CDRdataset(TestData):
    def __init__(self, data, type = 'c', padding = lambda x:x):
        data_un = data[0] if type == 'd' else data[1]
        
        mention_to_ids = {}

        for sample in data_un:
            mention = padding(sample['mention'].lower())
            id = sample['cui']
            add_to_dict_values_list(mention_to_ids, mention, id)
        
        super().__init__(mention_to_ids)

class SHAREdataset(TestData):
    def __init__(self, data, onto_keys ,padding = lambda x:x):
        
        mention_to_ids = {}

        for sample in data:
            id = sample['cui']
                
            if not onto_keys is None and not id in onto_keys:
                continue
            
            mention = sample['mention']
            if isinstance(mention, list):
                temp = ""
                for s in mention:
                    temp += s + " "
                mention = temp[:-1]
            mention = padding(mention.lower())

            add_to_dict_values_list(mention_to_ids, mention, id)
        
        super().__init__(mention_to_ids)

class NCBIdataset(TestData):
    def __init__(self, data ,padding = lambda x:x):
        unique_ids = set()
        mention_to_ids = {}
        
        for sample in data:
            id = sample['id']
            if isinstance(id, list):
                for i in id:
                    unique_ids.add(i)
            else:
                unique_ids.add(id)
            
            mention = padding(sample['mention'].lower())
            
            add_to_dict_values_list(mention_to_ids, mention, id)
        
        super().__init__(mention_to_ids)
    
    
class TrainLookup(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def apply_transform(self,transform):
        for k in self.keys():
            self.__setitem__(k,[transform(n) for n in self.__getitem__(k)])

    def filter_out_dulpicates(self,keep_for_empty = True):
        #generate stats
        synoyme_lookup = {}
        
        found_duplicate = False  #for speed up
        for id, mentions in self.items():
            for m in mentions:
                if m in synoyme_lookup:
                    if id in synoyme_lookup[m]:
                        synoyme_lookup[m][id] +=1
                        found_duplicate = True 
                    else:
                        synoyme_lookup[m][id] = 1
                else:
                    synoyme_lookup[m] = {id:1}

        found_duplicate = True
        
        removed_stuff = {}
        added_doubles = []
        if found_duplicate:
            for mention, stats in synoyme_lookup.items():
                max_stat = 0
                current_counter = 0
                #find max and check if alone
                for id,s in stats.items():
                    if s > max_stat:
                        max_stat = s
                        current_counter = 0
                    elif s == max_stat:
                        current_counter += 1

                if current_counter != 0:
                    for k in stats.keys():
                        self[k].remove(mention)
                        if k in removed_stuff:
                            removed_stuff[k].append(mention)
                        else:
                            removed_stuff[k] = [mention]
            if keep_for_empty:
                for key in self.keys():
                    if len(self[key]) == 0:
                        self[key] = removed_stuff[key]
                        del removed_stuff[key]
                        added_doubles.append(key)
        return removed_stuff, added_doubles

class BC5CDRtrainlookup(TrainLookup):
    def __init__(self,data, type = 'c', padding = lambda x:x):
        data_un = data[0] if type == 'd' else data[1]
        lookup_dict = {}

        for sample in data_un:
            key = sample['cui']

            mention = padding(sample['mention'].lower())
            if key in lookup_dict:   
                #if not mention in lookup_dict[key]:
                lookup_dict[key].append(mention)
            else:
                lookup_dict[key] = [mention]
        super().__init__(lookup_dict)


class SHAREtrainlookup(TrainLookup):
    def __init__(self,data, onto_keys ,padding = lambda x:x):
        lookup_dict = {}

        for sample in data:
            key = sample['cui']
            if not onto_keys is None and not key in onto_keys:
                continue
                
            mention = sample['mention']
            if isinstance(mention, list):
                temp = ""
                for s in mention:
                    temp += s + " "
                mention = temp[:-1]
            mention =  padding(mention.lower())

            if key in lookup_dict:   
                lookup_dict[key].append(mention)
            else:
                lookup_dict[key] = [mention]
        super().__init__(lookup_dict)

class NCBItrainlookup(TrainLookup):
    def __init__(self, data, onto, padding = lambda x:x):
        
        lookup_dict = {}
        self.for_doubles = {}
        
        for sample in data:
            key = sample['id']
            
            mention = padding(sample['mention'].lower())

            if isinstance(key, list):
                for k in key:
                    if not onto or k in onto:
                        add_to_dict_values_list(self.for_doubles, k, mention)
            else:
                if not onto or key in onto:
                    add_to_dict_values_list(lookup_dict, key, mention)
        
        super().__init__(lookup_dict)
