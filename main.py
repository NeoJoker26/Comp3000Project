import sys
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from  sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional
import pandas as pd


class DatabaseExporter():
    def __init__(self):
        pass

    def main(self):

        excel_frame = tk.LabelFrame(
            window,
            text="Excel Database"
        )
        excel_frame.pack(fill="both")

        self.excel_treeview = ttk.Treeview(
            window,
        )
        self.excel_treeview.pack(expand=True, fill="both")

        open_frame = tk.LabelFrame(
            window,
            text="Open File",
            labelanchor='n'
        )
        open_frame.pack(expand=True, fill="both")

        add_database_button = tk.Button(
            open_frame,
            text="Add database",
            command=self.open_file
        )
        add_database_button.pack(expand=True)

        self.database_label = tk.Label(
            open_frame,
            text="FileNaN"
        )
        self.database_label.pack(expand=True)

        xScroll = tk.Scrollbar(
            self.excel_treeview,
            orient="vertical",
            command=self.excel_treeview.yview
        )
        yScroll = tk.Scrollbar(
            self.excel_treeview,
            orient="horizontal",
            command=self.excel_treeview.xview
        )
        self.excel_treeview.config(yscrollcommand=yScroll.set, xscrollcommand=xScroll.set)
        yScroll.pack(side="bottom", fill="x")
        xScroll.pack(side="right", fill="y")

        window.mainloop()

    def open_file(self):
        try:
            file_types = (
                ("Excel Files", "*.xlsx"),
                ("CSV Files", "*.csv"),
                ("All Files", "*.*")
            )

            file_path = filedialog.askopenfilename(
                title="Open File",
                filetypes=file_types
            )

            if file_path:
                print(f"Selected file: {file_path}")
                file_name = os.path.basename(file_path)
                self.database_label["text"] = file_name

                try:
                    if file_name[-4:] == ".csv":
                        df = pd.read_csv(file_path)
                    else:
                        df = pd.read_excel(file_path)

                    # Clear the existing rows in the Treeview
                    for item in self.excel_treeview.get_children():
                        self.excel_treeview.delete(item)

                    # Define column names based on DataFrame columns
                    column_names = df.columns.tolist()
                    # Set columns in Treeview
                    self.excel_treeview["columns"] = column_names

                    # Insert data into Treeview
                    for index, row in df.iterrows():
                        # Insert a new row in the Treeview
                        item_id = self.excel_treeview.insert("", "end", values=tuple(row))

                        # Print each row to the Treeview
                        for i, value in enumerate(row):
                            self.excel_treeview.set(item_id, column_names[i], value)

                except ValueError:
                    messagebox.showerror("Error!", "The file you have chosen is invalid!")
                    return None
                except FileNotFoundError:
                    messagebox.showerror("Error!", f"No such file as {file_name}")
                    return None
            else:
                print("No file selected.")
                messagebox.showerror("Error!", "No file selected!")

        except Exception as e:
            print(f"An error occurred: {e}")
            messagebox.showerror("Error!", "An error occurred!")


if __name__ == '__main__':
    window = tk.Tk()
    window.title("Search for Database")
    window.minsize(500, 400)
    pd.set_option('display.max_column', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_seq_items', None)
    pd.set_option('display.max_colwidth', 500)
    pd.set_option('expand_frame_repr', True)
    exporter = DatabaseExporter()
    exporter.main()
