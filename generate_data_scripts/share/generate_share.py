import os
import pandas as pd
import configparser
from snomedCT_helper import SnomedCTHelper
from tqdm import tqdm

config_file_path = "../../../data/config/config.ini"
config = configparser.ConfigParser()
config.read(config_file_path)

hlp = SnomedCTHelper(config_path=config_file_path)
df_kb_entries = hlp.get_all_concepts_in_entity_linking_format()

with open(os.path.join(config["entity_linking.share"]["output_dir"], "document.json"), "w", encoding="utf-8") as file:
    df_kb_entries.to_json(file, orient="records", lines=True, force_ascii=False)
print("Done KB creation")

# ******************************************************************************************************************

WINDOW_SIZE_TOKENS = int(config["entity_linking.share"]["window_size_tokens"])

reports_dict = {
    "filename": [],
    "content": [],
    "annotation": [],
}

for _, _, files in os.walk(config["entity_linking.share"]["data_path_reports"]):
    for file in tqdm(files, total=len(files)):
        try:
            with open(os.path.join(config["entity_linking.share"]["data_path_labels"], f"{file.split('.')[0]}.pipe.txt")) as f:
                reports_dict["annotation"].append(f.read())
        except:
            print("No annotation file found: ", os.path.join(config["entity_linking.share"]["data_path_labels"], f"{file.split('.')[0]}.pipe.txt"))
            continue
        with open(os.path.join(config["entity_linking.share"]["data_path_reports"], file)) as f:
            reports_dict["content"].append(f.read())
        reports_dict["filename"].append(file)

df_reports = pd.DataFrame(reports_dict)

content_augmented_dict = {
    "filename": [],
    "mention": [],
    "cui": [],
    "content": [],
    "pos": []
}
for idx, row in tqdm(df_reports.iterrows(), total=df_reports.shape[0]):
    structured_annotations = [x for x in row["annotation"].split("\n") if x]
    for ann_item in structured_annotations:
        file_name, span, cui, *_ = ann_item.split("|")
        disjoint_spans = span.split(",")
        if len(disjoint_spans) > 1:
            # span is separated into multiple parts/words
            disjoint_span_start = int(disjoint_spans[0].split("-")[0])
            disjoint_span_end = int(disjoint_spans[-1].split("-")[1])
            content_augmented_dict["filename"].append(file_name)
            content_augmented_dict["cui"].append(cui)
            content_augmented_dict["content"].append(row["content"][(disjoint_span_start-WINDOW_SIZE_TOKENS):(disjoint_span_end+WINDOW_SIZE_TOKENS)])
            mention_str = []
            mention_pos = []
            for t_span in disjoint_spans:
                t_span_start, t_span_end = map(int, t_span.split("-"))
                mention_str.append(row["content"][t_span_start:t_span_end])
                pos_in_content_start = (t_span_start-disjoint_span_start)+WINDOW_SIZE_TOKENS
                pos_in_content_end = pos_in_content_start + (t_span_end-t_span_start)
                mention_pos.append((pos_in_content_start, pos_in_content_end))
            content_augmented_dict["mention"].append(mention_str)
            content_augmented_dict["pos"].append(mention_pos)
        else:
            # no disjoint span
            span_start, span_end = map(int, span.split("-"))
            content_augmented_dict["filename"].append(file_name)
            content_augmented_dict["cui"].append(cui)
            content_augmented_dict["content"].append(row["content"][(span_start-WINDOW_SIZE_TOKENS):(span_end+WINDOW_SIZE_TOKENS)])
            content_augmented_dict["mention"].append(row["content"][span_start:span_end])
            pos_in_content_start = WINDOW_SIZE_TOKENS
            pos_in_content_end = WINDOW_SIZE_TOKENS + (span_end - span_start)
            content_augmented_dict["pos"].append((pos_in_content_start, pos_in_content_end))

df_content_augmented = pd.DataFrame(content_augmented_dict)

with open(os.path.join(config["entity_linking.share"]["output_dir"], "train.json"), "w", encoding="utf-8") as file:
    df_content_augmented.to_json(file, orient="records", lines=True, force_ascii=False)
print("Done dataset creation")

