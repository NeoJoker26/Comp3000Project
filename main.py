import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os


class PredictionAlgorithm:
    def __int__(self):
        pass


class SecurityCheck:
    def __int__(self):
        pass


class DatabaseHandler:
    def __int__(self):
        pass


class GraphTheory:
    def __int__(self):
        pass


class WindowMaker:
    def __init__(self):
        pd.set_option('display.max_column', None)  # max number of columns that pandas can pull up
        pd.set_option('display.max_rows', None)  # max number of rows that pandas can pull up
        pd.set_option('display.max_seq_items', None)  # removes the limit on the number of items that can be displayed
        pd.set_option('display.max_colwidth', 500)  # sets the max pandas column width to 500 chars
        pd.set_option('expand_frame_repr', True)  # ensures that the DF expands over a few lines
        pd.set_option('display.precision', 10)  # sets floats to 10 dp
        pd.set_option('display.colheader_justify', 'left')  # sets column headers to left

        self.window = tk.Tk()  # creates main window called window
        self.window.title("Search for Database")  # title of the tkinter window
        self.window.geometry("800x600")  # the size of the tkinter window
        self.window.minsize(800, 600)  # sets the min size of the tkinter window

        self.file_path = None  # file path for file
        self.df = None  # makes an empty dataframe until it can be used amongst the class

        self.excel_frame = tk.LabelFrame(self.window, text="Excel Database")  # title for Labelframe for  treeview
        self.excel_frame.pack(fill="both", expand=True)  #

        self.excel_treeview = ttk.Treeview(self.excel_frame, columns=(), show="headings")  # creates treeview to view db
        self.excel_treeview.pack(expand=True, fill="both")

        # creates the x and y scroll bars, put into frame not treeview for aesthetics
        self.y_scroll = tk.Scrollbar(self.excel_frame, orient="vertical", command=self.excel_treeview.yview)
        self.x_scroll = tk.Scrollbar(self.excel_frame, orient="horizontal", command=self.excel_treeview.xview)
        self.y_scroll.pack(side="right", fill="y")
        self.x_scroll.pack(side="bottom", fill="x")
        self.excel_treeview.config(yscrollcommand=self.y_scroll.set, xscrollcommand=self.x_scroll.set)

        # creates open file title for frame for button
        self.open_frame = tk.LabelFrame(self.window, text="Open File", labelanchor='n')
        self.open_frame.pack(fill="both", expand=True)

        # creates add db button
        self.add_database_button = tk.Button(self.open_frame, text="Add database", command=self.open_file)
        self.add_database_button.pack(expand=True)

        # title for chosen file
        self.database_label = tk.Label(self.open_frame, text="FileNaN")
        self.database_label.pack(expand=True)

    def main(self):
        self.window.mainloop()  # calls tkinter window

    def open_file(self):
        file_types = (
            ("Excel Files", "*.xlsx"),
            ("Excel Files", "*.xls"),
            ("CSV Files", "*.csv"),
            ("All Files", "*.*")
        )

        self.file_path = filedialog.askopenfilename(title="Open File", filetypes=file_types)

        if self.file_path:
            file_name = self.file_path
            self.database_label["text"] = os.path.basename(file_name)

            if file_name.endswith(".csv"):
                try:
                    self.df = pd.read_csv(self.file_path, encoding='ISO-8859-1')
                except:
                    self.df = pd.read_csv(self.file_path, encoding='utf-8')
            elif file_name.endswith(".xlsx"):
                self.df = pd.read_excel(self.file_path)
            else:
                messagebox.showerror("Unsupported File Type", "The selected file is not supported.")
        else:
            messagebox.showerror("Unsupported File Type", "The selected file is not supported.")


if __name__ == '__main__':
    exporter = WindowMaker()
    exporter.main()
