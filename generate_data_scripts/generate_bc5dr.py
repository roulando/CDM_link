import json
import pickle

def parse_b5sd_file(file, onto = None):
    report_set = set()
    data_disease = []
    data_chem = []
    
    # Read the file line by line
    not_able_to_parse_counter = 0
    while True:
        line_head = file.readline()
        
        if not line_head:
            break

        _ = file.readline()
        empty_line = False
        while not empty_line:
            line =  file.readline()
            
            if line!='\n':
                line = line.split("\t")
                if len(line) != 4:   #get rid of relations
                    report_nr = line[0]
                    mention = line[3]
                    typ = line[4] 
                    cui = line[-1][:-1]

                    if len(line) == 6 or (len(line) == 7 and line[-1]=='\n'):
                        if cui != "-1":
                            sample = dict(
                                    cui = cui,
                                    mention = mention,
                                    typ = typ,
                                    report_nr = report_nr
                                )
                            report_set.add(report_nr)
                            
                            if sample['cui'] == "":
                                sample['cui'] = line[-2]

                            if typ == 'Disease':
                                if not sample['cui'] in onto:
                                    not_able_to_parse_counter +=1 
                                else:
                                    data_disease.append(sample)
                            elif typ == 'Chemical':
                                if not sample['cui'] in onto:
                                    not_able_to_parse_counter += 1
                                else:    
                                    data_chem.append(sample)
                            else:
                                assert False, "Somthing is wrong with the file"
                    elif len(line) == 7:
                        cuis = line[-2].split('|')
                        mentions = line[-1].split('|')
                        samples = []
                        for c,m in zip(cuis, mentions):
                            samples.append(dict(
                                        cui = c,
                                        mention = m,
                                        typ = typ,
                                        report_nr = report_nr
                                    ))

                        report_set.add(report_nr)
                        
                        for sample in samples:
                            if typ == 'Disease':
                                if not sample['cui'] in onto:
                                    not_able_to_parse_counter +=1 
                                else:
                                    data_disease.append(sample)
                            elif typ == 'Chemical':
                                if not sample['cui'] in onto:
                                    not_able_to_parse_counter += 1
                                else:    
                                    data_chem.append(sample)
                            else:
                                assert False, "Somthing is wrong with the file"
            else:
                empty_line = True
    return data_disease, data_chem, report_set


def main():

    data_dev_path = "./data/data_raw/bc5cdr/CDR.Corpus.v010516/CDR_DevelopmentSet.PubTator.txt"
    data_train_path = "./data/data_raw/bc5cdr/CDR.Corpus.v010516/CDR_TrainingSet.PubTator.txt"
    data_test_path = "./data/data_raw/bc5cdr/CDR.Corpus.v010516/CDR_TestSet.PubTator.txt"

    onto_path_part1  = "./data/data_raw/bc5cdr/ontology/Descriptor Records 2015.txt"
    onto_path_part2  = "./data/data_raw/bc5cdr/ontology/Supplementary Concept Records 2015.txt"

    onto_filename = "./data/bc5dr/onto.json"
    dataset_train_filename = "./data/bc5dr/train.pkl"
    dataset_test_filename  = "./data/bc5dr/test.pkl"
    dataset_dev_filename   = "./data/bc5dr/dev.pkl"

    #parse ontology
    onto = {}

    with open(onto_path_part1, 'r') as file:
        while True:
            line = file.readline()
            if line == '*NEWRECORD\n':
                lines = []
                while True:
                    line = file.readline()
                    if line != "\n":
                        lines.append(line)
                    else:
                        break
            else:
                break
            names = []
            for line in lines:
                
                if line[:len('MH = ')] == 'MH = ':
                    names.append(line[len('MH = '):-1])
                elif line[:len('ENTRY = ')] == 'ENTRY = ':
                    line = line[len('ENTRY = '):].split('|')
                    line = line[0] if len(line) != 1 else line[0][:-1]
                    
                    names.append(line)
                elif line[:len('N1 = ')] == 'N1 = ':
                    line = line[len('N1 = '):-1]
                    for l in line.split(", "):
                        names.append(l)
                    
                elif line[:len("PRINT ENTRY = ")] == "PRINT ENTRY = ":
                    line = line[len('PRINT ENTRY = '):].split('|')
                    line = line[0] if len(line) != 1 else line[0][:-1]
                    names.append(line)
                elif line[:len('UI = ')] == 'UI = ':
                    cui = line[len('UI = '):-1]
            last_cui = cui
            onto[cui] = names

    with open(onto_path_part2, 'r') as file:
        line = file.readline()
        stop = False
        while not stop:
            
            lines = []
            line = file.readline()
            while True:
                if line != "\n":
                    lines.append(line)
                if line == "":
                    stop = True
                    break
                line = file.readline()
                if line == '*NEWRECORD\n':
                    break
            
            names = []
            for line in lines:
                if line[:len('NM = ')] == 'NM = ':
                    names.append(line[len('NM = '):-1])
                elif line[:len('SY = ')] == 'SY = ':
                    line = line[len('SY = '):].split('|')
                    line = line[0] if len(line) != 1 else line[0][:-1]
                    names.append(line)
                elif line[:len('N1 = ')] == 'N1 = ':
                    line = line[len('N1 = '):-1]
                    for l in line.split(", "):
                        names.append(l)
                    
                elif line[:len('UI = ')] == 'UI = ':
                    cui = line[len('UI = '):-1]    
                    
            onto[cui] = names

    with open(data_test_path, 'r') as file:
        test_data_d, test_data_c, report_test_set = parse_b5sd_file(file, onto = onto)

    with open(data_train_path, 'r') as file:
        train_data_d, train_data_c, report_train_set = parse_b5sd_file(file, onto = onto)

    with open(data_dev_path, 'r') as file:
        dev_data_d, dev_data_c, report_dev_set = parse_b5sd_file(file, onto = onto)

    with open(dataset_train_filename, 'wb') as f:
        pickle.dump( [train_data_d, train_data_c], f)
    with open(dataset_test_filename, 'wb') as f:
        pickle.dump([test_data_d, test_data_c], f)
    with open(dataset_dev_filename, 'wb') as f:
        pickle.dump([dev_data_d, dev_data_c], f)

    with open(onto_filename, 'w') as f:
        for key, value in onto.items():
            f.write(json.dumps(dict(id = key, names = value)) + '\n')

if __name__ == "__main__":
    main()