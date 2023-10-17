import sys
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import sqlalchemy
import pandas as pd


class DatabaseExporter:
    def __init__(self):
        pass

    def main(self):
        window = tk.Tk()
        window.title("Search for Database")
        window.geometry("500x400")
        window.resizable(False, False)

        excelFrame = tk.LabelFrame(
            window,
            text="Excel Database"
        )
        excelFrame.place(height=200, width=480, relx=0.5, rely=0, anchor=tk.N)

        openFrame = tk.LabelFrame(
            window,
            text="Open File",
            labelanchor='n'
        )
        openFrame.place(height=130, width=240, relx=0.25, rely=0.5)

        addDatabaseButton = tk.Button(
            text="Add database",
            command=self.open_file
        )
        addDatabaseButton.place(relx=0.42, rely=0.73)

        self.databaseLabel = tk.Label(
            window,
            text="FileNan"
        )
        self.databaseLabel.place(relx=0.4, rely=0.65)

        excelTreeview = ttk.Treeview(
            window,

        )
        excelTreeview.place(height=175, width=470, relx=0.5, rely=0.05, anchor=tk.N)
        xScroll = tk.Scrollbar(
            excelTreeview,
            orient="vertical",
            command=excelTreeview.yview
        )
        yScroll = tk.Scrollbar(
            excelTreeview,
            orient="horizontal",
            command=excelTreeview.xview
        )
        excelTreeview.config(yscrollcommand=yScroll.set, xscrollcommand=xScroll.set)
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
                self.databaseLabel["text"] = file_name
                try:
                    filename = r"{}".format(file_name)
                    if filename[-4:] == ".csv":
                        df = pd.read_csv(filename)
                    else:
                        df = pd.read_excel(filename)
                except ValueError:
                    messagebox.showerror("Error!", "The file you have chosen is invalid!")
                    return None
                except FileNotFoundError:
                    tk.messagebox.showerror("Error!", f"No such file as {file_name}")
                    return None
            else:
                print("No file selected.")
                messagebox.showerror("Error!", "No file selected!")
        except Exception as e:
            print(f"An error occurred: {e}")
            messagebox.showerror("Error!", "An error occurred!")


if __name__ == '__main__':
    exporter = DatabaseExporter()
    exporter.main()