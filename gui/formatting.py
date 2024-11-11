import pandas as pd
import tkinter as tk
from tkinter import ttk

# complete node list
node_list = ["age35", "cardiotoxicity", "chemo_adiu", "chemo_neo", "cohort", "cvds",
             "death_in_5y", "dyslipidemia", "grade", "histology", "hormons_adiu", "hormons_neo",
             "hypertension", "ischemic_heart_disease", "ki67", "pn", "pt", "radio_adiu",
             "radio_neo", "receptors", "surgery", "t2db", "target_adiu", "target_neo", "vascular"]

# test (all possible node taken into consideration)
settable_list = ["id", "age35", "cardiotoxicity", "chemo_adiu", "chemo_neo", "cohort",
             "death_in_5y", "dyslipidemia", "grade", "histology", "hormons_adiu", "hormons_neo",
             "hypertension", "ischemic_heart_disease", "ki67", "pn", "pt", "radio_adiu",
             "radio_neo", "receptors", "surgery", "t2db", "target_adiu", "target_neo", "vascular"]

# types of options
list_options_node = ["dyslipidemia", "grade", "histology", "ki67", "pt"]
yes_no_options_node = ["age35", "chemo_adiu", "chemo_neo", "hormons_adiu", "hormons_neo",
                       "radio_adiu", "radio_neo", "target_adiu", "target_neo", "vascular"]
pre_post_no_options_node = ["dyslipidemia", "t2db", "hypertension"]
list_options_node = ["grade", "histology", "ki67", "pt", "receptors", "surgery", "pn"]

# mandatory columns - database purpose
mandatory_columns = ["id", "chemo_neo", "radio_neo", "hormons_neo", "target_neo", "chemo_adiu",
                     "radio_adiu", "hormons_adiu", "target_adiu", "surgery", "dyslipidemia", 
                     "hypertension", "t2db"]

# filter the wanted columns from the whole uploaded file
def format(df : pd.DataFrame) -> pd.DataFrame:
    df_columns = list(df.columns)
    to_set = []

    ## all nodes
    for value in settable_list:
        if value in df_columns:
            to_set.append(value)
    #print(to_set)
    
    df = df[to_set].astype(str)

    for node in mandatory_columns:
        if not(node in to_set):
            df[node] = ""

    for node in df.columns:
        df[node] = df[node].map(str.lower)
    
    #print(df)
    return df

# manage white spaces in combobox options
def match(value : str) -> str:
    if len(value) == 0:
        return ""
    # histology
    if value == "adenocarcinomas":
        return "adenomas_and_adenocarcinomas"
    if value == "complex epithelial neoplasms":
        return "complex_epithelial_neoplasms"
    if value == "ductal and lobular neoplasms":
        return "ductal_and_lobular_neoplasms"
    if value == "epithelial neoplasms nos":
        return "epithelial_neoplasms__nos"
    if value == "mucinous adenocarcinoma":
        return "mucinous_adenocarcinoma"
    if value == "neoplasms nos":
        return "neoplasms__nos"
    if value == "papillary cystadenocarcinoma":
        return "papillary_cystadenocarcinoma"
    if value == "squamous cell neoplasms":
        return "squamous_cell_neoplasms"
    # receptors
    if value == "her 2 arricchiti":
        return "her_2_arricchiti"
    if value == "luminal":
        return "luminal"
    if value == "luminal a":
        return "luminal_a"
    if value == "luminal b":
        return "luminal_b"
    if value == "luminal her2":
        return "luminal_her2"
    if value == "triple negative":
        return "triple_negative"
    # provisory
    if value == "pn+":
        return "pn_"
    # default
    return value

# looks if a particular terapy has been used 
def therapy_resent(therapy : str, treatments : str) -> str:
    if len(treatments) == 0:
        return ""
    else:
        if therapy in treatments:
            return "yes"
        else: 
            return "no"

## formatting rules ##

intro = "Accepted Types: .xlsx (Excel) and .csv (Comma-Separated Value)\n\nThe application accepts as input the upper mentioned types of files; il will filter the columns based on the settable list of nodes and discard the rest.\nPlease note that it is important to follow the exact same way everything is written, otherwise the column won't be read.\n\nIn the following table are summarized the values that can be set to a given node."



