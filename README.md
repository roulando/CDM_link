# Parameter-Free Biomedical Entity Linking: A Zero-Shot Compression-Based Approach

This repo holds the code necessary for data preprocessing and entity linking to reproduce the results of the
compression-based distance method presented in the paper: 
**"Parameter-Free Biomedical Entity Linking: A Zero-Shot Compression-Based Approach"**

## Data preprocessing
### ShARe dataset
For the ShARe dataset the underlying knowledge-base/ontology is SnomedCT based on UMLS 2012AB.
The relevant UMLS tables MRCONSO and MRREL have to be downloaded and a SQLite file has to be generated prior to preprocessing steps.<br>
* Input the config parameters for the MySQL database into the data\config\config.ini file. 
* Run generate_share.py which generates the ontology file (document.json) as well as the training and test jsons

### BC5CDR dataset
Get the data from: https://github.com/JHnlp/BioCreative-V-CDR-Corpus
Get the ontology from: https://github.com/JHnlp/BC5CIDTask

use the script generate_data_scripts/generate_bc5dr.py to generate dataset from the raw data files (Adjust file paths):
    ontology:
        - Descriptor Records 2015.txt
        - Supplementary Concept Records 2015.txt
    dataset: 
        - CDR_DevelopmentSet.PubTator.txt
        - CDR_TestSet.PubTator.txt
        - CDR_TrainingSet.PubTator.txt

### NCBI dataset
Get the data from here: https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/

use the script generate_data_scripts/generate_ncbi.py to generate dataset from the raw data files (Adjust file paths):
    - CTD_diseases.csv
    - NCBItestset_corpus.txt
    - NCBItrainset_corpus.txt
    - NCBIdevelopset_corpus.txt

## Environment
Setup Conda Environment: create an environment with
```
conda create -n cdm_link python=3.9
```


install requirements.txt with 
```
pip install -r requirements.txt
```

## Inference
NCBI: run: 
```
python3 src/main_NCBI.py
```

SHARE: run: 
```
python3 src/main_SHARE.py
```

BC5CDR: run: 
```
python3 src/main_BC5CDR.py
```
