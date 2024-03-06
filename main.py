import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import chardet
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from database import DatabaseHandler

# db_handler.create_banana(size=10, weight=100, sweetness=0.8, softness=0.6, harvest_time=2024, ripeness=0.7,
# acidity=0.5, quality="good")


class CRUDWindow(tk.Toplevel):
    def __init__(self, parent, data, db_handler):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        self.db_handler = db_handler
        self.title("CRUD Operations")
        self.geometry("800x600")

        # Create buttons for CRUD operations
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=10)

        create_button = tk.Button(self.button_frame, text="Create", command=self.create_entry)
        create_button.pack(side=tk.LEFT, padx=5)

        update_button = tk.Button(self.button_frame, text="Update", command=self.update_entry)
        update_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_entry)
        delete_button.pack(side=tk.LEFT, padx=5)

        visualize_button = tk.Button(self.button_frame, text="Visualize", command=self.visualize_data)
        visualize_button.pack(side=tk.LEFT, padx=5)

        # Create widgets for CRUD operations
        self.create_form_frame = None
        self.input_fields = None
        self.banana_data_label = None

    def create_entry(self):
        self.clear_window()
        self.create_form_frame = tk.Frame(self)
        self.create_form_frame.pack(pady=10)

        labels = ["Size:", "Weight:", "Sweetness:", "Softness:", "Harvest Time:", "Ripeness:", "Acidity:", "Quality:"]
        self.input_fields = []

        for i, label_text in enumerate(labels):
            label = tk.Label(self.create_form_frame, text=label_text)
            label.grid(row=i, column=0, sticky="W")

            entry = tk.Entry(self.create_form_frame)
            entry.grid(row=i, column=1)
            self.input_fields.append(entry)

        submit_button = tk.Button(self.create_form_frame, text="Submit", command=self.submit_data)
        submit_button.grid(row=len(labels), columnspan=2, pady=10)

        back_button = tk.Button(self.create_form_frame, text="Back", command=self.clear_window)
        back_button.grid(row=len(labels) + 1, columnspan=2, pady=10)

    def submit_data(self):
        if all(entry.get() for entry in self.input_fields):
            values = [entry.get() for entry in self.input_fields]
            banana_id = self.db_handler.create_banana(*values)
            messagebox.showinfo("Success", f"New banana entry created with id: {banana_id}")
        else:
            messagebox.showerror("Error", "Please enter all fields.")

    def update_entry(self):
        pass

    def delete_entry(self):
        pass

    def visualize_data(self):
        # Clear the window
        self.clear_window()

        # Create a new frame to hold the read entry functionality
        read_frame = tk.Frame(self)
        read_frame.pack(pady=10)

        # Create a label and entry widget for the Banana ID
        banana_id_label = tk.Label(read_frame, text="Enter Banana ID:")
        banana_id_label.grid(row=0, column=0)

        banana_id_entry = tk.Entry(read_frame)
        banana_id_entry.grid(row=0, column=1)

        # Create a button to submit the Banana ID
        submit_button = tk.Button(read_frame, text="Submit", command=lambda: self.read_entry(banana_id_entry.get()))
        submit_button.grid(row=0, column=2, padx=5)

        # Create a label to display the retrieved Banana data
        self.banana_data_label = tk.Label(read_frame, text="")
        self.banana_data_label.grid(row=1, columnspan=3, pady=10)

        # Create a back button to return to the main CRUD window
        back_button = tk.Button(read_frame, text="Back", command=self.clear_window)
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
            plt.figure(figsize=(8, 6))
            sns.histplot(data=self.data, x=size_column, y='Weight', bins=20, kde=True)
            plt.xlabel(size_column)
            plt.ylabel('Weight')
            plt.title(f'Weight Distribution as {size_column} Changes')
            plt.show()
        else:
            print("DataFrame is empty. Please load data first.")


class PredictionAlgorithm:
    def __init__(self):
        self.file = None
        self.columns = []
        self.data = None

    def load_data(self, file):
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

        num_predictions_to_print = int(0.2 * len(predictions))
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


class EnhanceSecurity:
    def __int__(self):
        pass


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
            # self.handle_db.create_table("csv_data", df.columns.tolist())
            # self.handle_db.insert_data("csv_data", df)

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
            # Open the CRUD window
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
            self.visualise.df = GraphTheory()
            self.visualise.df.data = self.data  # Set the data attribute in GraphTheory
            self.visualise.df.visualize_square_feet_vs_weight()
            self.visualise.df.visualize_histogram('Weight')
            self.visualise.df.visualize_histogram('Sweetness')
            self.visualise.df.visualize_histogram('Softness')
            self.visualise.df.visualize_histogram('HarvestTime')
            self.visualise.df.visualize_histogram('Ripeness')
            self.visualise.df.visualize_histogram('Acidity')
            self.visualise.df.visualize_quality()
            self.visualise.df.visualize_weight_distribution('Size')
        else:
            print("No file data loaded.")


if __name__ == "__main__":
    window = WindowMaker()
    window.main()
