import pandas as pd
import configparser
import sqlite3
from tqdm import tqdm


class SnomedCTHelper:

    def __init__(self, config_path="../data/config/config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.connection = sqlite3.connect(self.config["Database"]["host"])

    def get_all_concepts_in_entity_linking_format(self):
        df_concepts = pd.read_sql(f"select * from MRCONSO group by CUI, SUI", con=self.connection)
        concepts_formatted_dict = {
            "cui": [],
            "title": [],
            "synonyms": [],
        }
        for name, df_group in tqdm(df_concepts.groupby("CUI"), total=len(df_concepts.groupby("CUI"))):
            concepts_formatted_dict["cui"].append(df_group.iloc[0]["CUI"])
            concepts_formatted_dict["title"].append(df_group.iloc[0]["STR"])
            concepts_formatted_dict["synonyms"].append(df_group["STR"].values.tolist()[1:])
        return pd.DataFrame(concepts_formatted_dict)
