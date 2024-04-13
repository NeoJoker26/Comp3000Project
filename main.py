import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pyarrow as py
import chardet
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import psycopg2
from database import DatabaseHandler
import psutil
import tracemalloc
import time
import threading
import multiprocessing


# noinspection PyAttributeOutsideInit
class CRUDWindow(tk.Toplevel):
    def __init__(self, parent, data, db_handler):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        self.db_handler = db_handler

        # Set window title and size
        self.title("CRUD Operations")
        self.geometry("800x600")

        # Frame for buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=20)

        # Create button
        create_button = tk.Button(self.button_frame, text="Create", command=self.create_entry, padx=15, pady=5,
                                  font=("Helvetica", 12))
        create_button.pack(side=tk.LEFT)

        # Update button
        update_button = tk.Button(self.button_frame, text="Update", command=self.update_entry, padx=15, pady=5,
                                  font=("Helvetica", 12))
        update_button.pack(side=tk.LEFT)

        # Delete button
        delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_entry, padx=15, pady=5,
                                  font=("Helvetica", 12))
        delete_button.pack(side=tk.LEFT)

        # Visualize button
        visualize_button = tk.Button(self.button_frame, text="Visualize", command=self.visualize_data, padx=15, pady=5,
                                     font=("Helvetica", 12))
        visualize_button.pack(side=tk.LEFT)

        # Variables for form frame and input fields
        self.create_form_frame = None
        self.input_fields = None
        self.banana_data_label = None

    def create_entry(self):
        # calls to destroy the window, sounds more pleasant than read
        self.clear_window()

        # frame for the entry form
        self.create_form_frame = tk.Frame(self)
        self.create_form_frame.pack(pady=20)

        # Labels for the entry form fields as a "concept", this could be anything, it could be a bunch of labels for
        # a dog food company etc
        labels = ["Size:", "Weight:", "Sweetness:", "Softness:", "Harvest Time:", "Ripeness:", "Acidity:", "Quality:"]
        self.input_fields = []

        # Create label and entry fields for each label
        for i, label_text in enumerate(labels):
            label = tk.Label(self.create_form_frame, text=label_text, fg="black", font=("Helvetica", 12))
            label.grid(row=i, column=0, sticky="W", padx=10, pady=8)

            entry = tk.Entry(self.create_form_frame, bg="white", font=("Helvetica", 12), bd=3, relief=tk.SOLID)
            entry.grid(row=i, column=1, padx=10, pady=8, ipadx=10, sticky="ew")
            self.input_fields.append(entry)

        # Confirm button to submit data
        confirm_button = tk.Button(self.create_form_frame, text="Confirm", command=self.submit_data, bg="green",
                                   fg="white", relief=tk.FLAT, font=("Helvetica", 12))
        confirm_button.grid(row=len(labels), column=0, columnspan=2, pady=20, padx=10, ipadx=50, sticky="ew")

        # Back button
        back_button = tk.Button(self.create_form_frame, text="Back", command=self.clear_window, bg="red", fg="white",
                                relief=tk.FLAT, font=("Helvetica", 12))
        back_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10, padx=10, ipadx=50, sticky="ew")

    def submit_data(self):
        # Check if all input fields are filled
        if all(entry.get() for entry in self.input_fields):
            values = [entry.get() for entry in self.input_fields]
            # Create new banana in the db
            banana_id = self.db_handler.create_banana(*values)
            # added "professional" messages to handle the errors
            messagebox.showinfo("Success", f"New banana entry created with id: {banana_id}")
        else:
            messagebox.showerror("Error", "Please enter all fields.")

    def update_entry(self):
        # Clear the window before updating
        self.clear_window()

        # Create a frame for updating
        update_frame = tk.Frame(self)
        update_frame.pack(pady=10)

        # experimenting with different style of using fonts, tempted to make this a self.font and then use that for
        # every font in the CRUD class
        font_style = ("Helvetica", 12)

        # Label and entry for the banana ID, this is probably the best way i can think of to make this gui,
        # manual entering instead of searching through an index, this db has 8000 + my own creations but imagine
        # scrolling through a million, of even more, i will also want to add a feature that searches for the other
        # criteria but for now this is the only concept i have
        banana_id_label = tk.Label(update_frame, text="Enter Banana ID:", font=font_style)
        banana_id_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        banana_id_entry = tk.Entry(update_frame, font=font_style)
        banana_id_entry.grid(row=0, column=1, padx=10, pady=10)

        # Confirm button
        confirm_button = tk.Button(update_frame, text="Confirm",
                                   command=lambda: self.show_update_form(banana_id_entry.get()),
                                   bg="green", fg="white", relief=tk.FLAT, font=font_style, padx=15, pady=5)
        confirm_button.grid(row=1, column=0, columnspan=2, pady=20, padx=10, sticky="ew")

        # Back button
        back_button = tk.Button(update_frame, text="Back", command=self.clear_window, bg="red", fg="white",
                                relief=tk.FLAT, font=font_style, padx=15, pady=5)
        back_button.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

    def show_update_form(self, banana_id):
        # Check if the banana ID is provided
        if banana_id:
            try:
                # Convert the provided banana ID to an integer
                banana_id = int(banana_id)
                # Retrieve banana data from the database based on the provided ID
                banana_data = self.db_handler.read_banana(banana_id)
                if banana_data:
                    # Clear the window before showing the update form
                    self.clear_window()
                    update_form_frame = tk.Frame(self)
                    update_form_frame.pack(pady=10)

                    font_style = ("Helvetica", 12)

                    labels = ["Size:", "Weight:", "Sweetness:", "Softness:", "Harvest Time:", "Ripeness:", "Acidity:",
                              "Quality:"]
                    self.update_fields = []

                    for i, label_text in enumerate(labels):
                        label = tk.Label(update_form_frame, text=label_text, font=font_style)
                        label.grid(row=i, column=0, sticky="W")
                        entry = tk.Entry(update_form_frame, font=font_style)
                        entry.grid(row=i, column=1)
                        # Populate entry fields with existing data
                        entry.insert(0, getattr(banana_data, labels[i].lower().replace(":", "").replace(" ", "_")))
                        self.update_fields.append(entry)

                    # update button
                    update_button = tk.Button(update_form_frame, text="Update",
                                              command=lambda: self.update_banana(banana_id), bg="green", fg="white",
                                              relief=tk.FLAT, font=font_style, padx=15, pady=5)
                    update_button.grid(row=len(labels), columnspan=2, pady=10)

                    # back button
                    back_button = tk.Button(update_form_frame, text="Back", command=self.clear_window, bg="red",
                                            fg="white", relief=tk.FLAT, font=font_style, padx=15, pady=5)
                    back_button.grid(row=len(labels) + 1, columnspan=2, pady=10)
                else:
                    messagebox.showerror("Error", "Failed to retrieve banana data from the database.")
            except ValueError:
                messagebox.showerror("Error", "Invalid Banana ID. Please enter a valid integer.")
        else:
            messagebox.showerror("Error", "Please enter a Banana ID.")

    def update_banana(self, banana_id):
        # Get values from update fields
        values = [entry.get() for entry in self.update_fields]
        # Prepare banana data dictionary
        banana_data = {
            "size": float(values[0]),
            "weight": float(values[1]),
            "sweetness": float(values[2]),
            "softness": float(values[3]),
            "harvest_time": float(values[4]),
            "ripeness": float(values[5]),
            "acidity": float(values[6]),
            "quality": values[7]
        }
        # finally, update said banana
        updated_banana = self.db_handler.update_banana(banana_id, **banana_data)
        if updated_banana:
            messagebox.showinfo("Success", "Banana data updated successfully.")
        else:
            messagebox.showerror("Error", "Failed to update banana data in the database.")

    # self explanatory, delete banana (or concept field)
    def delete_entry(self):
        self.clear_window()

        delete_frame = tk.Frame(self)
        delete_frame.pack(pady=10)

        font_style = ("Helvetica", 12)

        banana_id_label = tk.Label(delete_frame, text="Enter Banana ID:", font=font_style)
        banana_id_label.pack(side=tk.LEFT)

        banana_id_entry = tk.Entry(delete_frame, font=font_style)
        banana_id_entry.pack(side=tk.LEFT)

        submit_button = tk.Button(delete_frame, text="Delete",
                                  command=lambda: self.delete_banana(banana_id_entry.get()), bg="green", fg="white",
                                  relief=tk.FLAT, font=font_style, padx=15, pady=5)
        submit_button.pack(side=tk.LEFT, padx=5)

        back_button = tk.Button(delete_frame, text="Back", command=self.clear_window, bg="red", fg="white",
                                relief=tk.FLAT, font=font_style, padx=15, pady=5)
        back_button.pack(side=tk.LEFT, padx=5)

    def delete_banana(self, banana_id):
        if banana_id:
            try:
                banana_id = int(banana_id)
                success = self.db_handler.delete_banana(banana_id)
                if success:
                    messagebox.showinfo("Success", "Banana data deleted successfully.")
                else:
                    messagebox.showerror("Error", "Failed to delete banana data from the database.")
            except ValueError:
                messagebox.showerror("Error", "Invalid Banana ID. Please enter a valid integer.")
        else:
            messagebox.showerror("Error", "Please enter a Banana ID.")

    # this is a bit funky as it will show the _sa_ instance state too but i would like to keep that just incase there
    # is an error, also shows everything in a list
    def visualize_data(self):
        self.clear_window()

        read_frame = tk.Frame(self)
        read_frame.pack(pady=10)

        font_style = ("Helvetica", 12)

        banana_id_label = tk.Label(read_frame, text="Enter Banana ID:", font=font_style)
        banana_id_label.grid(row=0, column=0)

        banana_id_entry = tk.Entry(read_frame, font=font_style)
        banana_id_entry.grid(row=0, column=1)

        submit_button = tk.Button(read_frame, text="Submit", command=lambda: self.read_entry(banana_id_entry.get()),
                                  bg="green", fg="white", relief=tk.FLAT, font=font_style, padx=15, pady=5)
        submit_button.grid(row=0, column=2, padx=5)

        self.banana_data_label = tk.Label(read_frame, text="", font=font_style)
        self.banana_data_label.grid(row=1, columnspan=3, pady=10)

        back_button = tk.Button(read_frame, text="Back", command=self.clear_window, bg="red", fg="white",
                                relief=tk.FLAT, font=font_style, padx=15, pady=5)
        back_button.grid(row=2, columnspan=3, pady=5)

    def read_entry(self, banana_id):
        if banana_id:
            try:
                banana_id = int(banana_id)
                banana_data = self.db_handler.read_banana(banana_id)
                if banana_data:
                    banana_data_str = "\n".join([f"{key}: {value}" for key, value in banana_data.__dict__.items()])
                    self.banana_data_label.config(text=banana_data_str)
                else:
                    messagebox.showerror("Error", "Failed to retrieve banana data from the database.")
            except ValueError:
                messagebox.showerror("Error", "Invalid Banana ID. Please enter a valid integer.")
        else:
            messagebox.showerror("Error", "Please enter a Banana ID.")

    def clear_window(self):
        for widget in self.winfo_children():
            if widget != self.button_frame:
                widget.destroy()


# this function is created to show different types of relationships that the csv file may have, it creates histograms
# based of the input, makes a heatmap, pairplot and more can be made however, i limited it to just these to 1) not
# overwhelm the person but 2) as a potential change, i could make a new child GUI, put buttons in and make it create
# different graphs based of different inputs e.g. if i want a bar chart of x and y, the user would be able to select
# that from the file and print it with a button, but this is just a concept for the time being
class GraphTheory:
    def __init__(self, data=None):
        self.data = data

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

    def visualize_quality(self):
        if self.data is not None:
            if 'Quality' in self.data.columns:
                quality_counts = self.data['Quality'].value_counts()
                plt.figure(figsize=(6, 4))
                quality_counts.plot(kind='bar', color=['green', 'red'])
                plt.xlabel('Quality')
                plt.ylabel('Frequency')
                plt.title('Frequency of Quality')
                plt.xticks(rotation=0)
                plt.show()
            else:
                print("DataFrame does not contain a 'Quality' column.")
        else:
            print("DataFrame is empty. Please load data first.")

    def visualize_weight_distribution(self, size_column):
        if self.data is not None:
            sns.set_style("whitegrid")
            plt.figure(figsize=(10, 6))
            sns.histplot(data=self.data, x=size_column, y='Weight', bins=20, kde=True, color='skyblue')
            plt.xlabel(size_column, fontsize=14)
            plt.ylabel('Weight', fontsize=14)
            plt.title(f'Weight Distribution as {size_column} Changes', fontsize=16)
            plt.grid(True)
            plt.show()
        else:
            print("DataFrame is empty. Please load data first.")

    def visualize_pairplot(self):
        if self.data is not None:
            sns.pairplot(self.data)
            plt.show()
        else:
            print("DataFrame is empty. Please load data first.")

    def visualize_correlation_heatmap(self):
        if self.data is not None:
            data_copy = self.data.copy()
            if 'Quality' in data_copy.columns:
                data_copy['Quality'] = data_copy['Quality'].map({'Good': 1, 'Bad': 0})

            plt.figure(figsize=(8, 6))
            sns.heatmap(data_copy.corr(), annot=True, cmap='coolwarm')
            plt.title('Correlation Heatmap')
            plt.show()
        else:
            print("DataFrame is empty. Please load data first.")

    def visualize_box_plot(self, column):
        if self.data is not None:
            plt.figure(figsize=(8, 6))
            sns.boxplot(data=self.data, x='Quality', y=column)
            plt.xlabel('Quality')
            plt.ylabel(column)
            plt.title(f'Box Plot of {column} by Quality')
            plt.show()
        else:
            print("DataFrame is empty. Please load data first.")

    def visualize_scatter_matrix(self):
        if self.data is not None:
            sns.set(style="ticks")
            sns.pairplot(self.data, diag_kind="kde")
            plt.show()
        else:
            print("DataFrame is empty. Please load data first.")


class PredictionAlgorithm:
    def __init__(self):
        self.file = None
        self.columns = []
        self.data = None

    # loading and pre processing the columns

    def load_data(self, file):
        self.file = file
        for col in file:
            try:
                file[col] = pd.to_numeric(file[col])
                self.columns.append(col)
            except ValueError:
                file = file.drop(col, axis=1)

    # where the magic happens, the csv file is evaluated with the MLPRegressor model (neural network) and it shows
    # the next 20% predictions with graphs, this is tested at 97-98% accuracy
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

        num_predictions_to_print = int(0.2 * len(predictions))  # add user control
        predictions_df = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
        print(predictions_df.head(num_predictions_to_print))

        plt.figure(figsize=(8, 6))
        plt.scatter(y_test, predictions)
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title('Actual vs. Predicted Values')
        plt.grid(True)
        plt.show()

        plt.figure(figsize=(8, 6))
        sns.kdeplot(predictions, label='Predicted', fill=True)
        plt.xlabel('Predicted Values')
        plt.ylabel('Density')
        plt.title('Density Plot of Predicted Values')
        plt.legend()
        plt.grid(True)
        plt.show()

    def visualize_quality_bar_chart(self):
        if self.data is not None:
            if 'Sweetness' in self.data.columns and 'Quality' in self.data.columns:
                quality_counts = self.data.groupby('Sweetness')['Quality'].value_counts().unstack().fillna(0)
                quality_counts.plot(kind='bar', stacked=True, color=['red', 'green'])

                plt.xlabel('Sweetness')
                plt.ylabel('Frequency')
                plt.title('Frequency of Quality by Sweetness')
                plt.legend(title='Quality', labels=['Bad', 'Good'])
                plt.xticks(rotation=45)
                plt.show()
            else:
                print("DataFrame is missing either 'Sweetness' or 'Quality' column.")
        else:
            print("DataFrame is empty. Please load data first.")


# this is the main window, ive set it up like i did CRUD window, the main buttons are in the init and all the actions
# for the buttons are in modular functions, it took a while to design a good gui as i used a treeview at first but
# then i realised how laggy it was and how awful the scroll bars were so i removed it and just left it as a label,
# in theory i could've used a decorator or some sort of inbuilt function but for ease for slower systems, i used a label
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
        self.db_handler = DatabaseHandler("postgresql://neojoker26:password123@localhost:5432/dissertation")
        self.neural_network = PredictionAlgorithm()
        self.visualise = GraphTheory()

        #
        self.stop_event = threading.Event()

    def main(self):
        tracemalloc.start()
        stats_thread = threading.Thread(target=self.display_stats, daemon=True)
        stats_thread.start()

        self.window.mainloop()

        self.stop_event.set()
        stats_thread.join()

    def display_stats(self):
        while not self.stop_event.is_set():
            if tracemalloc.is_tracing():
                snapshot = tracemalloc.take_snapshot()
                for stat in snapshot.statistics('lineno'):
                    print(stat)
            else:
                print("tracemalloc is not tracing memory allocations.")

            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            print(f"CPU Utilization: {cpu_percent}%")
            print(f"Memory Utilization: {memory_percent}%")

            time.sleep(15)

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
            crud_window = CRUDWindow(self.window, self.data, self.db_handler)
            crud_window.mainloop()
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
            self.visualise_df = GraphTheory()
            self.visualise_df.data = self.data  # Set the data attribute in GraphTheory

            # Create a pool of worker processes
            pool = multiprocessing.Pool(processes=4)  # Adjust the number of processes as needed

            # Run the visualization tasks in parallel
            pool.apply_async(self.visualise_df.visualize_histogram, args=('Weight',))
            pool.apply_async(self.visualise_df.visualize_histogram, args=('Sweetness',))
            pool.apply_async(self.visualise_df.visualize_histogram, args=('Softness',))
            pool.apply_async(self.visualise_df.visualize_histogram, args=('HarvestTime',))
            pool.apply_async(self.visualise_df.visualize_histogram, args=('Ripeness',))
            pool.apply_async(self.visualise_df.visualize_histogram, args=('Acidity',))
            pool.apply_async(self.visualise_df.visualize_quality)
            pool.apply_async(self.visualise_df.visualize_weight_distribution, args=('Size',))
            pool.apply_async(self.visualise_df.visualize_pairplot)
            pool.apply_async(self.visualise_df.visualize_correlation_heatmap)
            pool.apply_async(self.visualise_df.visualize_box_plot, args=('Weight',))
            pool.apply_async(self.visualise_df.visualize_scatter_matrix)

            # Wait for all tasks to complete
            pool.close()
            pool.join()
        else:
            print("No file data loaded.")


if __name__ == "__main__":
    window = WindowMaker()
    window.main()
