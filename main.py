import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import chardet
import pyarrow as pa
import seaborn as sns
import os
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import csv


class GraphTheory:
    def __init__(self):
        pass

    def visualize_square_feet_vs_price(self):
        sns.scatterplot(x='SquareFeet', y='Price', data=self.df)


class PredictionAlgorithm:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = None
        self.columns = []

    def load_data(self, df):
        # Load data into the class
        file = pd.read_excel('housing_price_dataset.xlsx')
        for col in file:
            try:
                file[col] = pd.to_numeric(file[col])
                self.columns.append(col)
            except ValueError:
                file = file.drop(col, axis=1)

    def evaluate_models(self):
        file = self.file
        scaler = MinMaxScaler()
        file[self.columns] = scaler.fit_transform(file[self.columns])
        X = file[self.columns]
        y = file['Price']
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=1000, activation='relu', random_state=42)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        print(predictions)


class EnchanceSecurity:
    def __int__(self):
        pass


class DatabaseHandler:
    def __init__(self):
        # Adjust the connection details here
        self.engine = create_engine('postgresql://neojoker26:password123@localhost/dissydb')

    def create_table(self, table_name, column_names):
        try:
            table = Table(table_name, *[Column(col_name, String()) for col_name in column_names])
            table.create(self.engine)
            print("Table created successfully.")
        except Exception as e:
            print("Error creating table:", e)

    def insert_data(self, table_name, df):
        try:
            conn = self.engine.connect()
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print("Data inserted into table successfully.")
        except Exception as e:
            print("Error inserting data into table:", e)


class WindowMaker:
    def __init__(self):
        # Configure pandas display options
        pd.set_option('display.max_column', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_seq_items', None)
        pd.set_option('display.max_colwidth', 500)
        pd.set_option('expand_frame_repr', True)
        pd.set_option('display.precision', 10)
        pd.set_option('display.colheader_justify', 'left')

        self.window = tk.Tk()
        self.window.title("Search for Database")
        self.window.geometry("800x600")
        self.window.minsize(800, 600)

        # Create variables for file path and data
        self.file_path = ""
        self.data = None

        # Create variable for sheets
        self.sheet_names = None
        self.sheet_data = {}

        # Create the main window widgets
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack()

        self.open_button = tk.Button(self.button_frame, text="Open File", command=self.open_file)
        self.open_button.pack(side=tk.LEFT, padx=5)

        self.send_to_db_button = tk.Button(self.button_frame, text="Send Through Database")
        self.send_to_db_button.pack(side=tk.LEFT, padx=5)

        self.label_filename = tk.Label(self.window, text="", wraplength=300)
        self.label_filename.pack()

        # Create vertical scrollbar
        self.y_scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL)
        self.y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create horizontal scrollbar
        self.x_scrollbar = ttk.Scrollbar(self.window, orient=tk.HORIZONTAL)
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create a text box to display the file content
        self.text_box = tk.Text(self.window, wrap=tk.NONE, yscrollcommand=self.y_scrollbar.set,
                                xscrollcommand=self.x_scrollbar.set)
        self.text_box.pack(fill=tk.BOTH, expand=True)
        self.y_scrollbar.config(command=self.text_box.yview)
        self.x_scrollbar.config(command=self.text_box.xview)

        # Create a listbox to display the detected sheets
        self.sheet_listbox = tk.Listbox(self.window, selectmode=tk.SINGLE, yscrollcommand=self.y_scrollbar.set)
        self.sheet_listbox.pack(fill=tk.BOTH, expand=True)

        # Bind double-click event on the listbox to select the sheet
        self.sheet_listbox.bind('<Double-Button-1>', self.select_sheet)

        # Send file to database class
        self.handle_db = DatabaseHandler()

    def main(self):
        self.window.mainloop()

    def open_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[
            ("CSV Files", "*.csv"),
            ("Excel Files", "*.xlsx *.xls"),
            ("All Files", "*.*")
        ])
        if self.file_path and self.file_path.endswith(".csv"):
            self.parse_csv()
        elif self.file_path.endswith((".xlsx", ".xls")):
            self.parse_excel(self.file_path)

    def parse_csv(self):
        try:
            self.text_box.delete('1.0', tk.END)
            with open(self.file_path, 'rb') as f:
                rawdata = f.read()
            encoding = chardet.detect(rawdata)['encoding']
            df = pd.read_csv(self.file_path, encoding=encoding)
            self.text_box.insert(tk.END, df.to_string(index=False))
            self.data = df
            self.handle_db.create_table("csv_data", df.columns.tolist())
            self.handle_db.insert_data("csv_data", df)
        except Exception as e:
            print("Error:", e)

    def parse_excel(self, file_path):
        try:
            self.text_box.delete('1.0', tk.END)
            df = pd.read_excel(file_path)
            self.text_box.insert(tk.END, df.to_string(index=False))
            self.sheet_listbox.delete(0, tk.END)
            for sheet_name in pd.ExcelFile(file_path).sheet_names:
                self.sheet_listbox.insert(tk.END, sheet_name)
            self.data = df
            self.handle_db.create_table("excel_data", df.columns.tolist())
            self.handle_db.insert_data("excel_data", df)
        except Exception as e:
            print("Error parsing Excel file:", e)

    def select_sheet(self, event):
        selected_index = self.sheet_listbox.curselection()
        if selected_index:
            selected_sheet = self.sheet_listbox.get(selected_index)
            excel_file = pd.ExcelFile(self.file_path)
            try:
                df = excel_file.parse(selected_sheet)
                self.text_box.delete('1.0', tk.END)
                self.text_box.insert(tk.END, df.to_string(index=False))
            except Exception as e:
                print(f"Error parsing sheet '{selected_sheet}':", e)


if __name__ == "__main__":
    window = WindowMaker()
    window.main()
