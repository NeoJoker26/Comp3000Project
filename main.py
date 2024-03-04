import tkinter as tk
from tkinter import ttk, filedialog
import pandas as pd
import chardet
import pyarrow as pa
import seaborn as sns
import os
import numpy as np
from matplotlib import pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapped_column, Mapped, relationship, DeclarativeBase
import csv
from typing import Optional, List
import psycopg2


class GraphTheory:
    def __init__(self, data=None):
        self.data = data

    def visualize_square_feet_vs_weight(self):
        if self.data is not None:
            sns.scatterplot(x='Size', y='Weight', data=self.data)
            plt.xlabel('Size')
            plt.ylabel('Weight')
            plt.title('Size vs Weight')
            plt.show()
        else:
            print("DataFrame is empty. Please load data first.")

    def visualize_histogram(self, column):
        if self.data is not None:
            sns.histplot(data=self.data, x=column)
            plt.xlabel(column)
            plt.ylabel('Frequency')
            plt.title(f'Histogram of {column}')
            plt.show()
        else:
            print("DataFrame is empty. Please load data first.")

    def visualize_line_plot(self, x_column, y_column):
        if self.data is not None:
            sns.lineplot(x=x_column, y=y_column, data=self.data)
            plt.xlabel(x_column)
            plt.ylabel(y_column)
            plt.title(f'Line Plot of {y_column} against {x_column}')
            plt.show()
        else:
            print("DataFrame is empty. Please load data first.")


class PredictionAlgorithm:
    def __init__(self):
        self.file = None
        self.columns = []

    def load_data(self, file):
        # Load data into the class
        self.file = file
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
        y = file['Size']
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=1000, activation='relu', random_state=42)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        print(predictions)

        plt.figure(figsize=(10, 6))
        plt.scatter(X_test, predictions, color='blue', label='Predictions')
        plt.scatter(X_test, y_test, color='red', label='Actual')
        plt.xlabel('Input Features')
        plt.ylabel('Size')
        plt.title('Actual vs Predicted Values')
        plt.legend()
        plt.show()


class EnhanceSecurity:
    def __int__(self):
        pass


class Base(DeclarativeBase):
    pass


class Banana(Base):
    __tablename__ = "banana_quality"
    banana_id: Mapped[int] = mapped_column(primary_key=True)
    size: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float)
    sweetness: Mapped[float] = mapped_column(Float)
    softness: Mapped[float] = mapped_column(Float)
    harvest_time: Mapped[float] = mapped_column(Float)
    ripeness: Mapped[float] = mapped_column(Float)
    acidity: Mapped[float] = mapped_column(Float)
    quality: Mapped[str] = mapped_column(String(5))

    def __repr__(self):
        return (
            f"Banana(id={self.banana_id!r}, size={self.size!r}, weight={self.weight!r}, "
            f"sweetness={self.sweetness!r}, softness={self.softness!r}, "
            f"harvest_time={self.harvest_time!r}, ripeness={self.ripeness!r}, "
            f"acidity={self.acidity!r}, quality={self.quality!r})"
        )


class DatabaseHandler:
    engine = create_engine("postgresql://neojoker26:password123@localhost:5432/dissy", echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    with engine.connect() as connection:
        result = connection.execute()
    metadata_obj = MetaData()

    def __init__(self):
        # Create all tables in the metadata at the start
        Base.metadata.create_all(self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_banana(self, size, weight, sweetness, softness, harvest_time, ripeness, acidity, quality):
        with self.get_db() as db:
            banana = Banana(
                size=size,
                weight=weight,
                sweetness=sweetness,
                softness=softness,
                harvest_time=harvest_time,
                ripeness=ripeness,
                acidity=acidity,
                quality=quality
            )
            db.add(banana)
            db.commit()

    def read_banana(self, banana_id):
        with self.get_db() as db:
            banana = db.query(Banana).get(banana_id)
            return banana

    def update_banana(self, banana_id, **kwargs):
        with self.get_db() as db:
            banana = db.query(Banana).get(banana_id)
            for key, value in kwargs.items():
                setattr(banana, key, value)
            db.commit()

    def delete_banana(self, banana_id):
        with self.get_db() as db:
            banana = db.query(Banana).get(banana_id)
            db.delete(banana)
            db.commit()


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

        self.send_to_db_button = tk.Button(self.button_frame, text="Send Through Database",
                                           command=self.send_to_database, state=tk.DISABLED)
        self.send_to_db_button.pack(side=tk.LEFT, padx=5)

        self.send_to_ml_button = tk.Button(self.button_frame, text="Send Through Machine Learning",
                                           command=self.send_to_ml, state=tk.DISABLED)
        self.send_to_ml_button.pack(side=tk.LEFT, padx=5)

        self.visualize_button = tk.Button(self.button_frame, text="Visualise",
                                          command=self.visualize_data, state=tk.DISABLED)
        self.visualize_button.pack(side=tk.LEFT, padx=5)

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

        # Send file to other classes
        self.handle_db = Banana()
        self.neural_network = PredictionAlgorithm()
        self.visualise = GraphTheory()

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

            self.send_to_db_button['state'] = tk.NORMAL
            self.send_to_ml_button['state'] = tk.NORMAL
            self.visualize_button['state'] = tk.NORMAL
        except Exception as e:
            print("Error:", e)

    def parse_excel(self, file_path):
        try:
            self.text_box.delete('1.0', tk.END)
            self.sheet_listbox.delete(0, tk.END)
            excel_file = pd.ExcelFile(file_path)
            self.sheet_names = excel_file.sheet_names
            for sheet_name in self.sheet_names:
                self.sheet_listbox.insert(tk.END, sheet_name)
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
                self.data = df

                self.send_to_db_button['state'] = tk.NORMAL
                self.send_to_ml_button['state'] = tk.NORMAL
                self.visualize_button['state'] = tk.NORMAL
            except Exception as e:
                print(f"Error parsing sheet '{selected_sheet}':", e)

    def send_to_database(self):
        if self.data is not None:
            self.handle_db.create_table("file_data", self.data.columns.tolist())
            self.handle_db.insert_data("file_data", self.data)
        else:
            print("No file data loaded.")

    def send_to_ml(self):
        if self.data is not None:
            self.neural_network.load_data(self.data)
            self.neural_network.evaluate_models()
        else:
            print("No file data loaded.")

    def visualize_data(self):
        if self.data is not None:
            self.visualise.df = GraphTheory()
            self.visualise.df.data = self.data  # Set the data attribute in GraphTheory
            self.visualise.df.visualize_square_feet_vs_weight()
            self.visualise.df.visualize_histogram('Size')
            self.visualise.df.visualize_histogram('Weight')
            self.visualise.df.visualize_histogram('Sweetness')
            self.visualise.df.visualize_histogram('Softness')
            self.visualise.df.visualize_histogram('HarvestTime')
            self.visualise.df.visualize_histogram('Ripeness')
            self.visualise.df.visualize_histogram('Acidity')
            self.visualise.df.visualize_histogram('Quality')

            # Example usage of visualize_line_plot
            self.visualise.df.visualize_line_plot('Size', 'Weight')
            self.visualise.df.visualize_line_plot('Sweetness', 'Quality')
        else:
            print("No file data loaded.")


if __name__ == "__main__":
    window = WindowMaker()
    window.main()
