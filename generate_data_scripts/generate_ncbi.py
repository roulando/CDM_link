import pandas as pd
import json

def load_and_parse_dataset(filename, onto, alt_ids, skip_first_line = False):
    dataset = []
    not_able_to_find_counter = 0
    unique_ids = set()
    line = ""
    with open(filename, 'r') as file:
        # Read the file line by line
        i = 0
        if skip_first_line:
            _ = file.readline()
        
        while True:
            line = file.readline()
            if not line:
                break
            #skip the text
            _ = file.readline()
            
            while True:
                line = file.readline()
                
                if line == "\n" or not line:
                    break
                
                split = line.split("\t")
                id = split[-1][:-1]
                if '|' in id:
                    id = id.split("|")
                if '+' in id:
                    id = id.split("+")
                mention = split[3]
                report_nr = split[0]
                if isinstance(id, list):
                    for index, bla in enumerate(id):
                        if ' ' == bla[0]:
                            id[index] = id[index][1:]
                        if "OMIM:" in bla:
                            id[index] = id[index][5:]
                        elif "MESH:" in id:
                            id[index] = id[index][5:]
                else:
                    if ' ' == id[0]:
                        id = id[1:]
                    if "OMIM:" in id:
                        id = id[5:]
                    elif "MESH:" in id:
                        id = id[5:]

                if isinstance(id, list):
                    for i_d in id:
                        unique_ids.add(i_d)
                else:
                    unique_ids.add(id)
                
                def check_id(str):
                    if not str in onto: 
                        if str in alt_ids:
                            str = alt_ids[str]
                        else:
                            str = None
                    return str

                if isinstance(id,list):
                    temp = []
                    for str in id:
                        str = check_id(str)
                        if str:
                            temp.append(str)
                    id = temp
                    
                    if len(id) == 0:
                        not_able_to_find_counter+=1
                        continue
                else:
                    id = check_id(id)
                    if not id:
                        not_able_to_find_counter+=1
                        continue
                
                dataset.append(dict(mention = mention, id = id,  report_nr = report_nr))
                
    print(f"Samples that could not be matched with the ontology: {not_able_to_find_counter}")
    return dataset

def main():

    #paths to raw data
    path_CTD_diseases = "./data/data_raw/ncbi/CTD_diseases.csv"
    path_testset = "./data/data_raw/ncbi/NCBItestset_corpus.txt"
    path_devset = "./data/data_raw/ncbi/NCBIdevelopset_corpus.txt"
    path_trainset = "./data/data_raw/ncbi/NCBItrainset_corpus.txt"

    #filenames of the parsed data
    onto_filename = "./data/ncbi/onto.json"
    dataset_train_filename = "./data/ncbi/train.json"
    dataset_test_filename  = "./data/ncbi/test.json"
    dataset_dev_filename   = "./data/ncbi/dev.json"

    
    print("Parsing the ontology")
    onto_link = pd.read_csv(path_CTD_diseases, skiprows=[i for i in range(27)]+[28])
    onto = {}
    alternative_link_ids = {} 

    for _,row in onto_link.iterrows():
        name = row['# DiseaseName']
        synonyms = []
        
        id = row['DiseaseID']
        if 'MESH:' in id:
            id = id[5:]
        elif 'OMIM:' in id:
            id = id[5:]
        else:
            assert False, "That is a new prefix... look why"
        if not pd.isna(row['Synonyms']):
            
            for s in row['Synonyms'].split('|'):
                if not s == "":
                    if s[0] == ' ':
                        s = s[1:]
                    if s[-1] == ' ':
                        s = s[:-1]
                synonyms.append(s)
        
        if not id in onto:
            onto[id] = [name] + synonyms
            if not pd.isna(row['AltDiseaseIDs']):
                alt_ids = row['AltDiseaseIDs']
                
                alt_ids = row['AltDiseaseIDs'].split("|") if "|" in alt_ids else [alt_ids]

                def cut(str):
                    if 'MESH:' in str:
                        str = str[5:]
                    elif 'OMIM:' in str:
                        str = str[5:]
                    return str
                for str in alt_ids:
                    if "DO:DOID:" in str:
                        continue
                    str = cut(str)

                    if not str in alt_ids:
                        alternative_link_ids[str] = id 
                    else:
                        assert False, "double id.. there is something wrong with the data"
        else:
            assert False, "double id.. there is something wrong with the data"

    #parse_data
    print("Parsing Testset")    
    testset = load_and_parse_dataset(path_testset, onto, alternative_link_ids, skip_first_line = False)
    print("Parsing Devset")    
    devset = load_and_parse_dataset(path_devset, onto, alternative_link_ids, skip_first_line = True)
    print("Parsing Trainset")    
    trainset = load_and_parse_dataset(path_trainset, onto, alternative_link_ids, skip_first_line = True)


    with open(dataset_train_filename, 'w') as f:
        for data in trainset:
            f.write(json.dumps(data) + '\n')

    with open(dataset_test_filename, 'w') as f:
        for data in testset:
            f.write(json.dumps(data) + '\n')

    with open(dataset_dev_filename, 'w') as f:
        for data in devset:
            f.write(json.dumps(data) + '\n')

    with open(onto_filename, 'w') as f:
        for key, value in onto.items():
            f.write(json.dumps(dict(id = key, names = value)) + '\n')


if __name__ == "__main__":
    main()