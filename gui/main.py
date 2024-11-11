from model import evaluateCardiovascularDiseaseIn5Years
from tooltip import *
from labelDetails import *
from formatting import *
from math import ceil

import pysmile
import pysmile_license

import tkinter as tk
from tkinter import ttk, Label, Toplevel
from tkinter import filedialog
from PIL import Image, ImageTk

import openpyxl
import sqlite3
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons
import logging

precision_digit = 4

### FUNCTION SECTION ###

### CREATE DATABASE TABLE 
con = sqlite3.connect('patient.db') ## use ':memory:' to save db in volatile memory
cur = con.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS patient(
               patient_id str PRIMARY KEY,
               chemo_neo str,
               radio_neo str,
               hormons_neo str,
               target_neo str,
               chemo_adiu str,
               radio_adiu str,
               hormons_adiu str,
               target_adiu str,
               surgery str,
               dyslipidemia str,
               hypertension str,
               t2db str,
               cvds_outcome_yes float)""")
con.commit()
con.close()
### END 

## get infographical image
def get_image_path(risk : float) -> str:
    risk = risk * 100
    if risk > 10:
        return "img/high_risk.png"
    elif risk <= 2:
        return "img/population_risk.png"
    elif risk > 2 and risk < 6:
        return "img/low_risk.png"
    else:
        return "img/medium_risk.png"

## get values from combobox; returns the predicted value + add or update record
def calculate() -> str:
    evidence = {"age35" : match(age35_combobox.get()),
                "histology" : match(histology_combobox.get()),
                "grade" : match(grade_combobox.get()),
                "vascular" : match(vascular_combobox.get()),
                "ki67" : match(ki67_combobox.get()),
                "receptors" : match(receptors_combobox.get()),
                "pt" : match(pt_combobox.get()),
                "pn" : match(pn_combobox.get()),
                "chemo_neo" : therapy_resent("chemotherapy", str(neo_adj_treatments_combobox.get())),
                "radio_neo" : therapy_resent("radiotherapy", str(neo_adj_treatments_combobox.get())),
                "target_neo" : therapy_resent("target", str(neo_adj_treatments_combobox.get())),
                "hormons_neo" : therapy_resent("hormone", str(neo_adj_treatments_combobox.get())),
                "surgery" : match(surgery_combobox.get()),
                "chemo_adiu" : therapy_resent("chemotherapy", str(adj_treatments_combobox.get())),
                "radio_adiu" : therapy_resent("radiotherapy", str(adj_treatments_combobox.get())),
                "target_adiu" : therapy_resent("target", str(adj_treatments_combobox.get())),
                "hormons_adiu" : therapy_resent("hormone", str(adj_treatments_combobox.get())),
                "dyslipidemia" : match(dyslipidemia_combobox.get()),
                "hypertension" : match(hypertension_combobox.get()),
                "t2db" : match(t2db_combobox.get())}
    #print(evidence)
    try:
        ## insert new patient
        def add():
            new_patient = [new_id_entry.get(), evidence["chemo_neo"], evidence["radio_neo"],
                           evidence["hormons_neo"], evidence["target_neo"], evidence["chemo_adiu"],
                           evidence["radio_adiu"], evidence["hormons_adiu"], evidence["target_adiu"],
                           surgery_combobox.get(), dyslipidemia_combobox.get(), hypertension_combobox.get(), 
                           t2db_combobox.get(), illness_score]
            if valid_ID(new_patient[0]):
                if is_present(str(new_patient[0])):
                    tk.messagebox.showwarning(title = "Error", message = "The given ID is already present in the DataBase")
                else:
                    try:
                        con = sqlite3.connect('patient.db') 
                        cur = con.cursor()
                        cur.execute('''INSERT or IGNORE INTO patient VALUES 
                                    (:patient_id, :chemo_neo, :radio_neo, :hormons_neo, :target_neo, 
                                    :chemo_adiu, :radio_adiu, :hormons_adiu, :target_adiu,
                                    :surgery, :dyslipidemia, :hypertension, :t2db, :cvds_outcome_yes)''', 
                                    {'patient_id': new_patient[0], 'chemo_neo': new_patient[1], 'radio_neo': new_patient[2],
                                     'hormons_neo': new_patient[3], 'target_neo': new_patient[4], 'chemo_adiu': new_patient[5],
                                     'radio_adiu': new_patient[6], 'hormons_adiu': new_patient[7], 'target_adiu': new_patient[8],
                                     'surgery': new_patient[9], 'dyslipidemia': new_patient[10], 'hypertension': new_patient[11], 
                                     't2db': new_patient[12], 'cvds_outcome_yes': new_patient[13]})
                        con.commit()
                        con.close()

                        show_db_content()
                        new_id_entry.delete(0, "end")
                        tk.messagebox.showinfo(message = "The new patient has been correctly added")
                    except sqlite3.ProgrammingError as e:
                        print(e)
                        #tk.messagebox.showwarning(title = "Error", message = "Please complete the mandatory information")
        ## update old patient
        def update() -> None:
            new_patient = [new_id_entry.get(), evidence["chemo_neo"], evidence["radio_neo"],
                           evidence["hormons_neo"], evidence["target_neo"], evidence["chemo_adiu"],
                           evidence["radio_adiu"], evidence["hormons_adiu"], evidence["target_adiu"],
                           surgery_combobox.get(), dyslipidemia_combobox.get(), hypertension_combobox.get(), 
                           t2db_combobox.get(), illness_score]
            if valid_ID(new_patient[0]):
                if not(is_present(str(new_patient[0]))):
                    tk.messagebox.showwarning(title = "Error", message = "The record you want to update does not exisit in the DataBase")
                else:
                    try:
                        con = sqlite3.connect('patient.db') 
                        cur = con.cursor()
                        cur.execute('''UPDATE patient SET 
                                    chemo_neo = :chemo_neo, radio_neo = :radio_neo, hormons_neo = :hormons_neo, 
                                    target_neo = :target_neo, chemo_adiu = :chemo_adiu, radio_adiu = :radio_adiu, 
                                    hormons_adiu = :hormons_adiu, target_adiu = :target_adiu, surgery = :surgery, 
                                    dyslipidemia = :dyslipidemia, hypertension = :hypertension, t2db =:t2db,
                                    cvds_outcome_yes = :cvds_outcome_yes
                                    WHERE patient_id = :patient_id''', 
                                    {'chemo_neo': new_patient[1], 'radio_neo': new_patient[2], 'hormons_neo': new_patient[3], 
                                     'target_neo': new_patient[4], 'chemo_adiu': new_patient[5], 'radio_adiu': new_patient[6], 
                                     'hormons_adiu': new_patient[7], 'target_adiu': new_patient[8], 'surgery': new_patient[9], 
                                     'dyslipidemia': new_patient[10], 'hypertension': new_patient[11], 't2db': new_patient[12],
                                     'cvds_outcome_yes': new_patient[13], 'patient_id' : new_patient[0]})
                        con.commit()
                        con.close()

                        show_db_content()
                        new_id_entry.delete(0, "end")
                        tk.messagebox.showinfo(message = "The selected patient has been updated")
                    except sqlite3.ProgrammingError as e:
                        print(e)
                        #tk.messagebox.showwarning(title = "Error", message = "Please complete the mandatory information")

        illness_score = round(evaluateCardiovascularDiseaseIn5Years(evidence), precision_digit)
        view_result_window = Toplevel(root)
        view_result_window.title("Result of the computation")
        view_result_window.geometry("1000x700")

        output_frame = tk.Frame(view_result_window)
        output_frame.pack(padx = 20, pady = 20)
        result_label = tk.Label(output_frame, text = "The predicted value is " + str(illness_score*100)[:4] + "%", font = ("Arial", 15, "bold"))
        result_label.grid(column = 0, row = 0, padx = 10, pady = 10)

        separator = ttk.Separator(output_frame)
        separator.grid(row = 1, column = 0, padx = 10, pady = 15, sticky = "nesw", columnspan = 2)

        img_path = get_image_path(round(illness_score, precision_digit))
     
        img = Image.open(img_path).resize((750, 300))
        img_tk = ImageTk.PhotoImage(img)
        img_label = Label(output_frame, image = img_tk)
        img_label.grid(column = 0, row = 2)
        img_label.image = img_tk ## keep reference to avoid garbage collection

        separator = ttk.Separator(output_frame)
        separator.grid(row = 3, column = 0, padx = 10, pady = 15, sticky = "nesw", columnspan = 2)
        
        insert_frame = tk.LabelFrame(output_frame, text = "Add as new patient or Update as existing patient")
        insert_frame.grid(column = 0, row = 4, padx = 20, pady = 20)
        new_id_label = tk.Label(insert_frame, text = "Patient's ID", font = "Arial")
        new_id_label.grid(column = 0, row = 0, padx = 15, pady = 10)
        new_id_entry = tk.Entry(insert_frame, background = "#404040")
        new_id_entry.grid(column = 1, row = 0, padx = 15, pady = 10)

        insert_btn = ttk.Button(insert_frame, text = "Insert New Patient", command = add)
        insert_btn.grid(row = 1, column = 0, padx = 15, pady = 10, sticky = "nesw")
        update_btn = ttk.Button(insert_frame, text = "Update Old Patient", command = update)
        update_btn.grid(row = 1, column = 1, padx = 15, pady = 10, sticky = "nesw")

    except pysmile.SMILEException as e:
        print(e)
        #tk.messagebox.showwarning(title = "Error", message = "Something went wrong...")

## clear values from combobox
def clear() -> None:
    combobox_values = [age35_combobox, histology_combobox, grade_combobox, 
                       vascular_combobox, ki67_combobox, receptors_combobox, pt_combobox, 
                       pn_combobox, neo_adj_treatments_combobox, surgery_combobox,
                       adj_treatments_combobox, dyslipidemia_combobox,
                       hypertension_combobox, t2db_combobox]
    combobox_values = [combo_value.set("") for combo_value in combobox_values]

## check valid id
def valid_ID(id : str) -> bool:
   if not id:
      tk.messagebox.showwarning(title = "Error", message = "Please insert an ID number")
      return False
   return True

## save (multiple) record to db
def save_many_to_db(result_df : pd.DataFrame) -> None:
   result_list = result_df[["id", "chemo_neo", "radio_neo", "hormons_neo", "target_neo", "chemo_adiu",
                            "radio_adiu", "hormons_adiu", "target_adiu", "surgery", "dyslipidemia", 
                            "hypertension", "t2db", "cvds_outcome_yes"]].values.tolist()
   con = sqlite3.connect('patient.db') 
   cur = con.cursor()
   # covert list of list to list of tuples
   list_tuple_result = [tuple(item) for item in result_list]
   print(list_tuple_result) 
   
   ## query insert many
   cur.executemany("INSERT OR IGNORE INTO patient VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                   list_tuple_result)
   con.commit()
   con.close()

   show_db_content()
   tk.messagebox.showinfo(message = "The data has been correctly saved")

## check if db contains the id already
def is_present(id : str) -> bool:
    con = sqlite3.connect('patient.db') 
    db_content_df = pd.read_sql_query("SELECT * FROM patient", con)
    con.close()
    id_list = db_content_df["patient_id"].astype(str).tolist()
    return id.lower() in id_list

## save results in file excel
def download_as_excel(result_df : pd.DataFrame) -> None:
    try:
        result_df.to_excel("resultComputation.xlsx")
        tk.messagebox.showinfo(message = "The file has been correctly saved")
    except Exception as e:
        tk.messagebox.showwarning(title = "Error", message = "Ops...something went wrong")

## save db's content in Excel File
def export_as_excel_db():
    con = sqlite3.connect('patient.db') 
    db_df = pd.read_sql_query("SELECT * FROM patient", con)
    con.close()
    try:
        db_df.to_excel("contentDatabase.xlsx", index = False)
        tk.messagebox.showinfo(message = "The file has been correctly downloaded")
    except Exception as e:
        tk.messagebox.showwarning(title = "Error", message = "Ops...something went wrong")

## save db's content in CSV File
def export_as_csv_db():
    con = sqlite3.connect('patient.db') 
    db_df = pd.read_sql_query("SELECT * FROM patient", con)
    con.close()
    try:
        db_df.to_csv("contentDatabase.csv", sep = ";", index = False)
        tk.messagebox.showinfo(message = "The file has been correctly downloaded")
    except Exception as e:
        tk.messagebox.showwarning(title = "Error", message = "Ops...something went wrong")

## get data from csv file - do prediction for each entry
def upload_file_csv() -> None:
    try:
        file = filedialog.askopenfilename(
            filetypes = [("CSV files", ".csv")])
        df = pd.read_csv(file, sep = ";")
        calculate_and_show(format(df))
    except pysmile.SMILEException:
        tk.messagebox.showwarning(title = "Error", message = "The uploaded file does not soddisfy the formatting rules.\nPlease go and review the formatting details")

## get data from excel file - do prediction for each entry
def upload_file_excel() -> None:
    try:
        file = filedialog.askopenfilename(
            filetypes = [("Excel file", ".xlsx")])
        df = pd.read_excel(file) 
        calculate_and_show(format(df))
    except pysmile.SMILEException:
        tk.messagebox.showwarning(title = "Error", message = "The uploaded file does not soddisfy the formatting rules.\nPlease go and review the formatting details")

## calculate and show for every entry the resulting prediction + option to save
def calculate_and_show(df : pd.DataFrame) -> None:
    #print(df)
    cvds_outcome_yes = []
    classification_risk = []     
    for index in df.index:
        evidence = dict(df.iloc[index])
        #print(evidence)
        evidence.pop("id")
        risk = round(float(evaluateCardiovascularDiseaseIn5Years(evidence)), precision_digit)
        cvds_outcome_yes.append(risk)
        if risk <= 0.02:
            classification_risk.append("general population")
        elif risk > 0.02 and risk <= 0.6:
            classification_risk.append("low risk")
        elif risk > 0.06 and risk <= 0.01:
            classification_risk.append("medium risk")
        else:
            classification_risk.append("high risk")
    print(len(cvds_outcome_yes))
    df.insert(loc = len(df.columns), column = "cvds_outcome_yes", value = cvds_outcome_yes)
    df.insert(loc = len(df.columns), column = "classification_risk", value = classification_risk)
    list_values = df[["id", "cvds_outcome_yes", "classification_risk"]].sort_values(by = "cvds_outcome_yes", ascending = False).values.tolist()
    list_values = [[item[0], item[1], item[2]] for item in list_values] # get rid of .0 from id (int(item[0]))
    #print(list_values)

    view_result_window = Toplevel(root)
    view_result_window.title("Result of the Computation")
    view_result_window.geometry("1000x600")

    out_frame = tk.Frame(view_result_window)
    out_frame.pack(padx = 10, pady = 10)

    ## treeview of computation result
    treeFrame = ttk.Frame(out_frame)
    treeFrame.grid(row = 0, column = 0, padx = 45, pady = 40, sticky = "")
    treeScroll = ttk.Scrollbar(treeFrame)
    treeScroll.pack(side = "right", fill = "y", padx = 10, pady = 10)
    treeview = ttk.Treeview(treeFrame, show = "headings", yscrollcommand = treeScroll.set, 
                            columns = ("id", "cvds_outcome_yes", "classification_risk"), height = 13, padding = 5)
    treeview.heading("id", text = "Patient's ID")
    treeview.heading("cvds_outcome_yes", text = "Predicted Value")
    treeview.heading("classification_risk", text = "Risk Classification")
    for value in list_values[0:]:
        treeview.insert('', tk.END, values = value)
    treeview.pack()
    treeScroll.config(command = treeview.yview)
    
    # save to db 
    save_to_db_btn = ttk.Button(out_frame, text = "Save Results to DataBase", command = lambda: save_many_to_db(df))
    save_to_db_btn.grid(row = 1, column = 0, padx = 5, pady = 10)

    # download as excel 
    download_as_excel_btn = ttk.Button(out_frame, text = "Download Results as Excel File", command = lambda: download_as_excel(df))
    download_as_excel_btn.grid(row = 2, column = 0, padx = 5, pady = 10)

    print(df)
    # get graphical representation
    get_graph_btn = ttk.Button(out_frame, text = "Show Graphical Representation", command = lambda: show_graph(df))
    get_graph_btn.grid(row = 3, column = 0, padx = 5, pady = 10)

## show graph
def show_graph(df : pd.DataFrame) -> None:

    palette = {"yes" : "#AAD9BB", "no": "#F9F7C9"}
    palette2 = {"conservative" : "#AAD9BB", "radical" : "#F9F7C9"}

    df = df.rename(columns = {"chemo_adiu" : "Adjuvant Chemotherapy", "radio_adiu" : "Adjuvant Radio Therapy", 
                              "hormons_adiu" : "Adjuvant Hormons Therapy", "target_adiu" : "Adjuvant Target Therapy",
                              "chemo_neo" : "Neo-Adjuvant Chemotherapy", "radio_neo" : "Neo-Adjuvant Radio Therapy", 
                              "hormons_neo" : "Neo-Adjuvant Hormons Therapy", "target_neo" : "Neo-Adjuvant Target Therapy",
                              "surgery" : "Surgery"})

    fig, ax = plt.subplots(figsize = (60, 60))
    
    sns.histplot(ax = ax, data = df, x = "classification_risk", discrete = True, shrink = .8,
                 color = "#80BCBD")

    plt.subplots_adjust(left = 0.4)
    ax_radio = plt.axes([0.05, 0.3, 0.22, 0.3])
    labels = ("Default", "Adjuvant Chemotherapy", "Adjuvant Radio Therapy", "Adjuvant Hormons Therapy", "Adjuvant Target Therapy",
              "Surgery", "Neo-Adjuvant Chemotherapy", "Neo-Adjuvant Radio Therapy", "Neo-Adjuvant Hormons Therapy", "Neo-Adjuvant Target Therapy")       
    radio_buttons = RadioButtons(ax_radio, labels, active = 0)

    def get_graph(graph):
        ax.clear()
        if (radio_buttons.value_selected == "Surgery"):
            sns.histplot(ax = ax, data = df, x = "classification_risk", discrete = True, shrink = .8, 
                         hue = df[radio_buttons.value_selected], multiple = "dodge", palette = palette2)
        elif (radio_buttons.value_selected != "Default"):
            sns.histplot(ax = ax, data = df, x = "classification_risk", discrete = True, shrink = .8, 
                         hue = df[radio_buttons.value_selected], multiple = "dodge", palette = palette)
        else:
            sns.histplot(ax = ax, data = df, x = "classification_risk", discrete = True, shrink = .8,
                         color = "#80BCBD")
        ax.set(xlabel = "Risk Classification", ylabel = "Count")
        fig.canvas.draw_idle()
    
    radio_buttons.on_clicked(get_graph)
    
    ax.set(xlabel = "Risk Classification", ylabel = "Count")
    plt.show()

## serach patient in db
def search() -> None:
    if valid_ID(id_entry.get()):
      id_number = (id_entry.get()).lower()
      con = sqlite3.connect('patient.db') ## use ':memory:' to save db in volatile memory
      cur = con.cursor()
      cur.execute("SELECT * FROM patient WHERE patient_id = :patient_id", 
                  {'patient_id': id_number})
      result = cur.fetchall()
      if not result:
        tk.messagebox.showwarning(title = "Error", message = "The selected patient is not present in the DataBase")
      else:
        view_serach_resul_window = Toplevel(root)
        view_serach_resul_window.title("Information found on the searched patient")
        view_serach_resul_window.geometry("500x400")

        table = [["Identification Number", result[0][0]],
                 ["Neo-Adjuvant Chemotherapy", result[0][1]],
                 ["Neo-Adjuvant Radiotherapy", result[0][2]],
                 ["Neo-Adjuvant Hormons Therapy", result[0][3]],
                 ["Neo-Adjuvant Target Therapy", result[0][4]],
                 ["Adjuvant Chemotherapy", result[0][5]],
                 ["Adjuvant Radio Therapy", result[0][6]],
                 ["Adjuvant Hormons Therapy", result[0][7]],
                 ["Adjuvant Target Therapy", result[0][8]],
                 ["Surgery", result[0][9]],
                 ["Dyslipedemia", result[0][10]],
                 ["Hypertension", result[0][11]],
                 ["Type 2 Diabeties", result[0][12]],
                 ["Cardiovascular Risk Prediction", result[0][13]]]
        
        header = ""
        res = ""
        for item in table:
            header += item[0] + "   \n"
            if (len(str(item[1])) != 0):
                res += str(item[1]) + "\n"
            else:
                res += "not available\n"

        search_result_frame = tk.Frame(view_serach_resul_window)
        search_result_frame.pack(padx = 15, pady = 15)

        header_label = tk.Label(search_result_frame, text = header, 
                                font = ("Arial", 15), justify = "left")
        header_label.grid(column = 0, row = 0)
        result_label = tk.Label(search_result_frame, text = res, 
                                font = ("Arial", 15), justify = "left")
        result_label.grid(column = 1, row = 0)
        
      con.close()
    id_entry.delete(0, "end")

## delete patient in db
def delete() -> None:
   if valid_ID(id_entry.get()):
      id_number = id_entry.get()
      con = sqlite3.connect('patient.db')
      cur = con.cursor()
      cur.execute("SELECT * FROM patient WHERE patient_id = :patient_id", 
                  {'patient_id': id_number})
      result = cur.fetchall()
      if not result:
         tk.messagebox.showwarning(title = "Error", message = "The selected patient is not present in the DataBase")
      else:
         cur.execute("DELETE from patient WHERE patient_id = :patient_id",
                     {'patient_id': id_number})
         con.commit()
         tk.messagebox.showinfo(message = "The selected patient has been removed correctly")
      con.close()
      show_db_content()
   id_entry.delete(0, "end")

## eliminate table content
def eliminate():
    try:
        con = sqlite3.connect('patient.db')
        cur = con.cursor()
        cur.execute("DELETE FROM patient")
        con.commit()
        con.close()
        
        show_db_content()
    except Exception as e:
        print(e)

## show database content
def show_db_content() -> None:
    con = sqlite3.connect('patient.db') 
    db_content_df = pd.read_sql_query("SELECT * FROM patient", con)
    con.close()
    #db_content_df["patient_id"] = db_content_df["patient_id"].astype(str)
    db_content_list = db_content_df.sort_values(by = "cvds_outcome_yes", ascending = False).values.tolist()

    treeFrame = ttk.Frame(show_db_frame)
    treeFrame.grid(row = 0, column = 0, padx = 25, pady = 20)
    treeScroll = ttk.Scrollbar(treeFrame)
    treeScroll.pack(side = "right", fill = "y", padx = 10, pady = 10)
    columns = ["id", "chemo_neo", "radio_neo", "hormons_neo", "target_neo", "chemo_adiu",
               "radio_adiu", "hormons_adiu", "target_adiu", "surgery",
               "dyslipidemia", "hypertension", "t2db", "cvds_outcome_yes"]
    treeview = ttk.Treeview(treeFrame, show = "headings", yscrollcommand = treeScroll.set, 
                            columns = columns)
    treeview.heading("id", text = "ID")
    treeview.heading("chemo_neo", text = "CHEMO NEO")
    treeview.heading("radio_neo", text = "RADIO NEO")
    treeview.heading("hormons_neo", text = "HORMONS NEO")
    treeview.heading("target_neo", text = "TARGET NEO")
    treeview.heading("chemo_adiu", text = "CHEMO ADIU")
    treeview.heading("radio_adiu", text = "RADIO ADIU")
    treeview.heading("hormons_adiu", text = "HORMONS ADIU")
    treeview.heading("target_adiu", text = "TARGET ADIU")
    treeview.heading("surgery", text = "SURGERY")
    treeview.heading("dyslipidemia", text = "DYSLIPIDEMIA")
    treeview.heading("hypertension", text = "HYPERTENSION")
    treeview.heading("t2db", text = "DIABETES")
    treeview.heading("cvds_outcome_yes", text = "PREDICTION")
    
    for value in db_content_list[0:]:
        treeview.insert('', tk.END, values = value)
    for col in columns:
        if col == "cvds_outcome_yes":
            treeview.column(col, width = 100)
        elif (col == "surgery" or col == "dyslipidemia" or col == "hypertension"
              or col == "hormons_adiu" or col == "hormons_neo" or col == "t2db"):
            treeview.column(col, width = 90)
        else:
            treeview.column(col, width = 75)
    treeview.pack()
    treeScroll.config(command = treeview.yview)

## show the formatting rules
def show_formatting_rules() -> None:
    view_info_window = Toplevel(root)
    view_info_window.title("Indications for the correct formatting of the input file")
    view_info_window.geometry("1200x1200")

    info_frame = tk.Frame(view_info_window)
    info_frame.pack()

    intro_label = tk.Label(info_frame, text = intro)
    intro_label.config(font = "Arial", anchor = "e", justify = "left")
    intro_label.grid(column = 0, row = 0, padx = 10, pady = 10)
    
    info_img = Image.open("img/info_table3.png")
    info_img_tk = ImageTk.PhotoImage(info_img)
    table_label = tk.Label(info_frame, image = info_img_tk)
    table_label.grid(column = 0, row = 1)
    table_label.image = info_img_tk 

    
### END FUNCTION SECTION ###

### GUI SECTION ###
root = tk.Tk()
root.title("Application")

## make the app responsive
for index in [0, 1, 2]:
    root.columnconfigure(index = index, weight = 1)            
    root.rowconfigure(index = index, weight = 1)

# setting style of application
style = ttk.Style(root)
root.tk.call("source", "theme/forest-dark.tcl")
style.theme_use("forest-dark")

# main frame
main_frame = ttk.Frame()
main_frame.pack()

# widget frame
widgets_frame = tk.LabelFrame(main_frame, text = "WELCOME", font = ("Arial", 20, "bold"))
widgets_frame.grid(row = 0, column = 0, padx = 15, pady = 15)

# paned window
paned = ttk.PanedWindow(widgets_frame)
paned.grid(row = 0, column = 1, sticky = "nsew", padx = 10, pady = 10)
pane = ttk.Frame(paned, padding = 5)
paned.add(pane, weight = 3)
notebook = ttk.Notebook(pane)
notebook.pack(fill = "both", expand = True)

# info-button
info_img = Image.open("img/info_btn.png").resize((25, 25))
info_img_tk = ImageTk.PhotoImage(info_img)
info_btn = tk.Button(main_frame, text = "show formatting rules", image = info_img_tk, command = show_formatting_rules)
info_btn.grid(column = 0, row = 1, sticky = "se", padx = 10, pady = 5)
info_btn.image = info_img_tk ## keep reference to avoid garbage collection

# tab 3

binary_answers = ["", "no", "yes"]

tab_1 = ttk.Frame(notebook)
notebook.add(tab_1, text = "Insert Data")
input_frame = tk.LabelFrame(tab_1, text = "INSERT DATA MANUALLY")
input_frame.grid(row = 0, column = 0, padx = 35, pady = 10) ## centering with padx

breast_cancer_diagnosis_group = tk.LabelFrame(input_frame, text = "BREAST CANCER DIAGNOSIS")
breast_cancer_diagnosis_group.grid(row = 0, column = 0, padx = 10, pady = 15, sticky = "ne")

age35_label = tk.Label(breast_cancer_diagnosis_group, text = "Older than 35")
age35_combobox = ttk.Combobox(breast_cancer_diagnosis_group, state = "readonly", values = binary_answers)
age35_label.grid(row = 0, column = 0)
age35_combobox.grid(row = 0, column = 1)
CreateToolTip(age35_label, text = age35_details)

histology_values = ["", "adenocarcinomas", "complex epithelial neoplasms",
                    "ductal and lobular neoplasms", "epithelial neoplasms nos", "mucinous adenocarcinoma",
                    "neoplasms nos", "papillary cystadenocarcinoma", "squamous cell neoplasms"]
histology_label = tk.Label(breast_cancer_diagnosis_group, text = "Tumor Histology")
histology_combobox = ttk.Combobox(breast_cancer_diagnosis_group, state = "readonly", values = histology_values)
histology_label.grid(row = 1, column = 0)
histology_combobox.grid(row = 1, column = 1)
CreateToolTip(histology_label, text = histology_details)

grade_values = ["", "i", "ii", "iii"]
grade_label = tk.Label(breast_cancer_diagnosis_group, text = "Tumor Grading")
grade_combobox = ttk.Combobox(breast_cancer_diagnosis_group, state = "readonly", values = grade_values)
grade_label.grid(row = 2, column = 0)
grade_combobox.grid(row = 2, column = 1)
CreateToolTip(grade_label, text = grade_details)

ki67_label = tk.Label(breast_cancer_diagnosis_group, text = "Ki67 Greater than or Equal to 14")
ki67_combobox = ttk.Combobox(breast_cancer_diagnosis_group, state = "readonly", values = binary_answers)
ki67_label.grid(row = 4, column = 0)
ki67_combobox.grid(row = 4, column = 1)
CreateToolTip(ki67_label, text = ki67_details)

receptors_values = ["", "her 2 arricchiti", "luminal", "luminal a",
                    "luminal b", "luminal her2", "triple negative"]
receptors_label = tk.Label(breast_cancer_diagnosis_group, text = "Tumor Receptor Status")
receptors_combobox = ttk.Combobox(breast_cancer_diagnosis_group, state = "readonly", values = receptors_values)
receptors_label.grid(row = 5, column = 0)
receptors_combobox.grid(row = 5, column = 1)
CreateToolTip(receptors_label, text = receptors_details)

pt_values = ["", "pt1", "pt2", "pt3", "pt4"]
pt_label = tk.Label(breast_cancer_diagnosis_group, text = "Pathological TNM T")
pt_combobox = ttk.Combobox(breast_cancer_diagnosis_group, state = "readonly", values = pt_values)
pt_label.grid(row = 6, column = 0)
pt_combobox.grid(row = 6, column = 1)
CreateToolTip(pt_label, text = pt_details)

pn_values = ["", "pn+", "pn0"]
pn_label = tk.Label(breast_cancer_diagnosis_group, text = "Pathological TNM N")
pn_combobox = ttk.Combobox(breast_cancer_diagnosis_group, state = "readonly", values = pn_values)
pn_label.grid(row = 7, column = 0)
pn_combobox.grid(row = 7, column = 1)
CreateToolTip(pn_label, text = pn_details)

vascular_label = tk.Label(breast_cancer_diagnosis_group, text = "Vascular Invasion")
vascular_combobox = ttk.Combobox(breast_cancer_diagnosis_group, state = "readonly", values = binary_answers)
vascular_label.grid(row = 3, column = 0)
vascular_combobox.grid(row = 3, column = 1)
CreateToolTip(vascular_label, text = vascular_details)

for widget in breast_cancer_diagnosis_group.winfo_children():
    widget.grid_configure(padx = 15, pady = 10, sticky = "nesw")
    if isinstance(widget, ttk.Combobox):
        widget.config(width = 44)
    if isinstance(widget, tk.Label):
        widget.config(font = "Arial", anchor = "w")
    if isinstance(widget, tk.Button):
        widget.config(font = "Arial")

treatment_risk_frame = tk.Frame(input_frame)
treatment_risk_frame.grid(row = 0, column = 1, padx = 10, sticky = "nesw")

breast_cancer_treatment_group = tk.LabelFrame(treatment_risk_frame, text = "BREAST CANCER TREATMENT")
breast_cancer_treatment_group.grid(row = 0, column = 0, padx = 10, pady = 15, sticky = "nesw")

neo_adj_values = ["", "chemotherapy alone", "chemotherapy and hormone therapy",
                  "chemotherapy, radiotherapy and hormone therapy", 
                  "hormone therapy alone", "none", "radiotherapy alone"]
neo_adj_treatments_label = tk.Label(breast_cancer_treatment_group, text = "Neo-Adjuvant Treatments")
neo_adj_treatments_combobox = ttk.Combobox(breast_cancer_treatment_group, state = "readonly", values = neo_adj_values)
neo_adj_treatments_label.grid(row = 0, column = 0)
neo_adj_treatments_combobox.grid(row = 0, column = 1)
CreateToolTip(neo_adj_treatments_label, text = neo_adj_treatments_details)

surgery_values = ["", "conservative", "radical"]
surgery_label = tk.Label(breast_cancer_treatment_group, text = "Surgery Type")
surgery_combobox = ttk.Combobox(breast_cancer_treatment_group, state = "readonly", values = surgery_values)
surgery_label.grid(row = 1, column = 0)
surgery_combobox.grid(row = 1, column = 1)
CreateToolTip(surgery_label, text = surgery_details)

adj_values = ["", "chemotherapy alone", "chemotherapy and hormone therapy",
              "chemotherapy and radiotherapy", "chemotherapy and target therapy",
              "chemotherapy, radiotherapy and hormone therapy",
              "chemotherapy, radiotherapy and target therapy",
              "chemotherapy, radiotherapy, target therapy and hormone therapy",
              "chemotherapy, target therapy and hormone therapy",
              "hormone therapy alone", "none",
              "radiotherapy alone", "radiotherapy and hormone therapy",
              "radiotherapy and target therapy", 
              "radiotherapy, target therapy and hormone therapy",
              "target therapy alone", "target therapy and hormone therapy"]
adj_treatments_label = tk.Label(breast_cancer_treatment_group, text = "Adjuvant Treatments")
adj_treatments_combobox = ttk.Combobox(breast_cancer_treatment_group, state = "readonly", values = adj_values)
adj_treatments_label.grid(row = 2, column = 0)
adj_treatments_combobox.grid(row = 2, column = 1)
CreateToolTip(adj_treatments_label, text = adj_treatments_details)


for widget in breast_cancer_treatment_group.winfo_children():
    widget.grid_configure(padx = 15, pady = 10, sticky = "nesw")
    if isinstance(widget, ttk.Combobox):
        widget.config(width = 45)
    if isinstance(widget, tk.Label):
        widget.config(font = "Arial", anchor = "w")
    if isinstance(widget, tk.Button):
        widget.config(font = "Arial")

major_cardiovascular_risk_factor_group = tk.LabelFrame(treatment_risk_frame, text = "MAJOR CARDIOVASCULAR RISK FACTOR")
major_cardiovascular_risk_factor_group.grid(row = 1, column = 0, padx = 10, pady = 15, sticky = "nesw")

t2db_values = ["", "no", "post", "pre"]
t2db_label = tk.Label(major_cardiovascular_risk_factor_group, text = "Type 2 Diabete Mellitus")
t2db_combobox = ttk.Combobox(major_cardiovascular_risk_factor_group, state = "readonly", values = t2db_values)
t2db_label.grid(row = 0, column = 0)
t2db_combobox.grid(row = 0, column = 1)
CreateToolTip(t2db_label, text = t2db_details)

hypertension_values = ["", "no", "post", "pre"]
hypertension_label = tk.Label(major_cardiovascular_risk_factor_group, text = "Hypertension")
hypertension_combobox = ttk.Combobox(major_cardiovascular_risk_factor_group, state = "readonly", values = hypertension_values)
hypertension_label.grid(row = 1, column = 0)
hypertension_combobox.grid(row = 1, column = 1)
CreateToolTip(hypertension_label, text = hypertension_details)

dyslipidemia_values = ["", "no", "post", "pre"]
dyslipidemia_label = tk.Label(major_cardiovascular_risk_factor_group, text = "Dyslipidemia")
dyslipidemia_combobox = ttk.Combobox(major_cardiovascular_risk_factor_group, state = "readonly", values = dyslipidemia_values)
dyslipidemia_label.grid(row = 2, column = 0)
dyslipidemia_combobox.grid(row = 2, column = 1)
CreateToolTip(dyslipidemia_label, text = dyslipidemia_details)

for widget in major_cardiovascular_risk_factor_group.winfo_children():
    widget.grid_configure(padx = 15, pady = 10, sticky = "nesw")
    if isinstance(widget, ttk.Combobox):
        widget.config(width = 45)
    if isinstance(widget, tk.Label):
        widget.config(font = "Arial", anchor = "w")
    if isinstance(widget, tk.Button):
        widget.config(font = "Arial")

action_frame = tk.Frame(tab_1)
action_frame.grid(row = 1, column = 0)

button_submit = ttk.Button(action_frame, text = "Get Prediction CVDS", command = calculate)
button_submit.grid(row = 0, column = 0, padx = 15, pady = 15)
CreateToolTip(button_submit, text = "Probability of getting cardiovascular disease in 5 year")

button_clear = ttk.Button(action_frame, text = "Clear", command = clear)
button_clear.grid(row = 0, column = 1, padx = 15, pady = 15)

upload_excel_btn = ttk.Button(action_frame, text = "Upload Excel File", command = upload_file_excel)
upload_excel_btn.grid(row = 0, column = 2, padx = 15, pady = 15)

upload_csv_btn = ttk.Button(action_frame, text = "Upload CSV File", command = upload_file_csv)
upload_csv_btn.grid(row = 0, column = 3, padx = 15, pady = 15)


# tab 2 - pt1: show DB content; pt2: operations on DB
tab_2 = ttk.Frame(notebook)
notebook.add(tab_2, text = "Database")

show_db_frame = tk.Frame(tab_2)
show_db_frame.grid(row = 0, column = 0, padx = 15, pady = 5)

show_db_content()


db_operations_frame = tk.LabelFrame(tab_2, text = "")
db_operations_frame.grid(row = 1, column = 0, padx = 15, pady = 5)

id_label = tk.Label(db_operations_frame, text = "Patient's ID")
id_entry = tk.Entry(db_operations_frame, background = "#404040")
id_label.grid(row = 0, column = 0)
id_entry.grid(row = 0, column = 1)
search_btn = ttk.Button(db_operations_frame, text = "Search Patient", command = search)
search_btn.grid(row = 0, column = 2, padx = 5, pady = 5, sticky = "nesw")
delete_btn = ttk.Button(db_operations_frame, text = "Delete Patient", command = delete)
delete_btn.grid(row = 0, column = 3, padx = 5, pady = 5, sticky = "nesw")
eliminate_btn = ttk.Button(db_operations_frame, text = "Clear DataBase Content", command = eliminate)
eliminate_btn.grid(row = 1, column = 0, padx = 5, pady = 5, sticky = "nesw", columnspan = 4)

separator = ttk.Separator(db_operations_frame)
separator.grid(row = 2, column = 0, padx = 10, pady = 15, sticky = "nesw", columnspan = 4)


export_excel_db_btn = ttk.Button(db_operations_frame, text = "Export DataBase as Excel File", command = export_as_excel_db)
export_excel_db_btn.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = "nesw", columnspan = 4)
export_csv_db_btn = ttk.Button(db_operations_frame, text = "Export DataBase as CSV File", command = export_as_csv_db)
export_csv_db_btn.grid(row = 4, column = 0, padx = 5, pady = 5, sticky = "nesw", columnspan = 4)

for widget in db_operations_frame.winfo_children():
    widget.grid_configure(padx = 15, pady = 5, sticky = "nesw")
    if isinstance(widget, tk.Label):
        widget.config(font = "Arial", anchor = "w")
    if isinstance(widget, tk.Button):
        widget.config(font = "Arial")



root.mainloop()
### END GUI SECTION ###
