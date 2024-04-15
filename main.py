import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pyarrow as py
import chardet
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import psycopg2
from database import DatabaseHandler
import psutil
import threading
import multiprocessing
import logging

# start global logger
logger = logging.getLogger(__name__)


# noinspection PyAttributeOutsideInit
class CRUDWindow(tk.Toplevel):
    def __init__(self, parent, data, db_handler):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        self.db_handler = db_handler
        self.colorblind_mode = False  # Flag for colorblind mode
        self.colorblind_type = "None"  # Default colorblind type

        # Set window title and size
        self.title("CRUD Operations")
        self.geometry("800x600")

        # Regular button colors
        self.regular_palette = {"confirm_bg": "green", "back_bg": "red"}
        # Colorblind button colors
        self.colorblind_palette = {
            "Protanopia": {"confirm_bg": "blue", "back_bg": "orange"},
            "Deuteranopia": {"confirm_bg": "purple", "back_bg": "yellow"},
            "Tritanopia": {"confirm_bg": "green", "back_bg": "red"}
        }

        # Frame for buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(pady=20)

        # Create button
        self.create_button = tk.Button(self.button_frame, text="Create", command=self.create_entry,
                                       font=("Helvetica", 12), width=10, height=2, relief=tk.RAISED, bd=2)
        self.create_button.pack(side=tk.LEFT, padx=10)

        # Read button
        self.read_button = tk.Button(self.button_frame, text="Read", command=self.visualise,
                                     font=("Helvetica", 12), width=10, height=2, relief=tk.RAISED, bd=2)
        self.read_button.pack(side=tk.LEFT, padx=10)

        # Update button
        self.update_button = tk.Button(self.button_frame, text="Update", command=self.update_entry,
                                       font=("Helvetica", 12), width=10, height=2, relief=tk.RAISED, bd=2)
        self.update_button.pack(side=tk.LEFT, padx=10)

        # Delete button
        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_entry,
                                       font=("Helvetica", 12), width=10, height=2, relief=tk.RAISED, bd=2)
        self.delete_button.pack(side=tk.LEFT, padx=10)

        # Colorblind mode dropdown
        self.colorblind_var = tk.StringVar()
        colorblind_options = ["None", "Protanopia", "Deuteranopia", "Tritanopia"]
        colorblind_dropdown = tk.OptionMenu(self.button_frame, self.colorblind_var, *colorblind_options,
                                            command=self.update_colorblind_mode)
        colorblind_dropdown.pack(side=tk.LEFT, padx=10)
        self.colorblind_var.set("None")  # Set default value

        # Variables for form frame and input fields
        self.create_form_frame = None
        self.input_fields = None

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

            entry = tk.Entry(self.create_form_frame, font=("Helvetica", 12))
            entry.grid(row=i, column=1, padx=10, pady=8, ipadx=10, sticky="ew")
            self.input_fields.append(entry)

        # Confirm button to submit data
        confirm_button = tk.Button(self.create_form_frame, text="Confirm", command=self.submit_data,
                                   font=("Helvetica", 12), width=10, height=2, relief=tk.RAISED, bd=2)
        confirm_button.grid(row=len(labels), column=0, columnspan=2, pady=20, padx=10)

        # Back button
        back_button = tk.Button(self.create_form_frame, text="Back", command=self.clear_window,
                                font=("Helvetica", 12), width=10, height=2, relief=tk.RAISED, bd=2)
        back_button.grid(row=len(labels) + 1, column=0, columnspan=2, pady=10, padx=10)

        self.set_button_colors(confirm_button, back_button)

    def submit_data(self):
        # Check if all input fields are filled
        if all(entry.get() for entry in self.input_fields):
            values = [entry.get() for entry in self.input_fields]
            # Create new banana in the db
            banana_id = self.db_handler.create_banana(*values)
            # added "professional" messages to handle the errors
            messagebox.showinfo("Success", f"New banana entry created with id: {banana_id}")
            logger.info(f"New banana entry created with id: {banana_id}")
        else:
            messagebox.showerror("Error", "Please enter all fields.")
            logger.error("Error occurred while entering data.")

    def update_entry(self):
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

        confirm_button = tk.Button(update_frame, text="Confirm",
                                   command=lambda: self.show_update_form(banana_id_entry.get()),
                                   font=font_style, width=10, height=2, relief=tk.RAISED, bd=2)
        confirm_button.grid(row=1, column=0, columnspan=2, pady=20, padx=10)

        back_button = tk.Button(update_frame, text="Back", command=self.clear_window,
                                font=font_style, width=10, height=2, relief=tk.RAISED, bd=2)
        back_button.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

        self.set_button_colors(confirm_button, back_button)

    def show_update_form(self, banana_id):
        # check if banana ID is provided
        if banana_id:
            try:
                # try to cast as int
                banana_id = int(banana_id)
                # retrieve banana from the database
                banana_data = self.db_handler.read_banana(banana_id)
                if banana_data:
                    # if the banana is retrieved, clear and display it
                    self.clear_window()
                    update_form_frame = tk.Frame(self)
                    update_form_frame.pack(pady=10)

                    font_style = ("Helvetica", 12)

                    labels = ["Size:", "Weight:", "Sweetness:", "Softness:", "Harvest Time:", "Ripeness:", "Acidity:",
                              "Quality:"]
                    self.update_fields = []

                    # creates labels and entry fields to update banana
                    for i, label_text in enumerate(labels):
                        label = tk.Label(update_form_frame, text=label_text, font=font_style)
                        label.grid(row=i, column=0, sticky="W")
                        entry = tk.Entry(update_form_frame, font=font_style)
                        entry.grid(row=i, column=1)
                        entry.insert(0, getattr(banana_data, labels[i].lower().replace(":", "").replace(" ", "_")))
                        self.update_fields.append(entry)

                    confirm_button = tk.Button(update_form_frame, text="Confirm",
                                               command=lambda: self.update_banana(banana_id),
                                               font=font_style, width=10, height=2, relief=tk.RAISED, bd=2)
                    confirm_button.grid(row=len(labels), column=0, columnspan=2, pady=20, padx=10)

                    back_button = tk.Button(update_form_frame, text="Back", command=self.clear_window,
                                            font=font_style, width=10, height=2, relief=tk.RAISED, bd=2)
                    back_button.grid(row=len(labels) + 1, columnspan=2, pady=10)

                    self.set_button_colors(confirm_button, back_button)
                else:
                    messagebox.showerror("Error", "Failed to retrieve banana data from the database.")
                    logger.error("Failed to retrieve banana data from the database.")
            except ValueError:
                messagebox.showerror("Error", "Invalid Banana ID. Please enter a valid integer.")
                logger.error("Invalid Banana ID. Please enter a valid integer.")
        else:
            messagebox.showerror("Error", "Please enter a Banana ID.")
            logger.error("Please enter a Banana ID.")

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
            logger.info("Banana data updated successfully.")
        else:
            messagebox.showerror("Error", "Failed to update banana data in the database.")
            logger.error("Failed to update banana data in the database.")

    # delete banana (or concept field)
    def delete_entry(self):
        self.clear_window()

        delete_frame = tk.Frame(self)
        delete_frame.pack(pady=10)

        font_style = ("Helvetica", 12)

        banana_id_label = tk.Label(delete_frame, text="Enter Banana ID:", font=font_style)
        banana_id_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        banana_id_entry = tk.Entry(delete_frame, font=font_style)
        banana_id_entry.grid(row=0, column=1, padx=10, pady=10)

        confirm_button = tk.Button(delete_frame, text="Confirm",
                                   command=lambda: self.delete_banana(banana_id_entry.get()),
                                   font=font_style, width=10, height=2, relief=tk.RAISED, bd=2)
        confirm_button.grid(row=1, column=0, columnspan=2, pady=20, padx=10)

        back_button = tk.Button(delete_frame, text="Back", command=self.clear_window,
                                font=font_style, width=10, height=2, relief=tk.RAISED, bd=2)
        back_button.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

        self.set_button_colors(confirm_button, back_button)

    def delete_banana(self, banana_id):
        # Delete banana data from the database
        if banana_id:
            try:
                banana_id = int(banana_id)
                success = self.db_handler.delete_banana(banana_id)
                if success:
                    messagebox.showinfo("Success", "Banana data deleted successfully.")
                    logger.info("Banana data deleted successfully.")
                else:
                    messagebox.showerror("Error", "Failed to delete banana data from the database.")
                    logger.error("Failed to delete banana data from the database.")
            except ValueError:
                messagebox.showerror("Error", "Invalid Banana ID. Please enter a valid integer.")
                logger.error("Invalid Banana ID. Please enter a valid integer.")
        else:
            messagebox.showerror("Error", "Please enter a Banana ID.")
            logger.error("Please enter a Banana ID.")

    # this is a bit funky as it will show the _sa_ instance state too but i would like to keep that just incase there
    # is an error, also shows everything in a list
    def visualise(self):
        self.clear_window()

        read_frame = tk.Frame(self)
        read_frame.pack(pady=10)

        font_style = ("Helvetica", 12)

        banana_id_label = tk.Label(read_frame, text="Enter Banana ID:", font=font_style)
        banana_id_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        banana_id_entry = tk.Entry(read_frame, font=font_style)
        banana_id_entry.grid(row=0, column=1, padx=10, pady=10)

        confirm_button = tk.Button(read_frame, text="Confirm", command=lambda: self.read_entry(banana_id_entry.get()),
                                   font=font_style, width=10, height=2, relief=tk.RAISED, bd=2)
        confirm_button.grid(row=1, column=0, columnspan=2, pady=20, padx=10)

        back_button = tk.Button(read_frame, text="Back", command=self.clear_window,
                                font=font_style, width=10, height=2, relief=tk.RAISED, bd=2)
        back_button.grid(row=2, column=0, columnspan=2, pady=10, padx=10)

        self.set_button_colors(confirm_button, back_button)

        # Create the banana_data_label but hide it initially
        self.banana_data_label = tk.Label(read_frame, text="", font=font_style, wraplength=400)
        self.banana_data_label.grid(row=3, columnspan=2, pady=10, sticky="nsew")
        self.banana_data_label.grid_remove()  # Hide the label

    def read_entry(self, banana_id):
        if banana_id:
            try:
                banana_id = int(banana_id)
                banana_data = self.db_handler.read_banana(banana_id)
                if banana_data:
                    banana_data_str = "\n".join([f"{key}: {value}" for key, value in banana_data.__dict__.items()])
                    self.banana_data_label.config(text=banana_data_str)
                    self.banana_data_label.grid()  # Show the label
                else:
                    self.banana_data_label.grid_remove()  # Hide the label
                    messagebox.showerror("Error", "Failed to retrieve banana data from the database.")
                    logger.error("Failed to retrieve banana data from the database.")
            except ValueError:
                self.banana_data_label.grid_remove()  # Hide the label
                messagebox.showerror("Error", "Invalid Banana ID. Please enter a valid integer.")
                logger.error("Invalid Banana ID. Please enter a valid integer.")
        else:
            self.banana_data_label.grid_remove()  # Hide the label
            messagebox.showerror("Error", "Please enter a Banana ID.")
            logger.error("Please enter a Banana ID.")

    def clear_window(self):
        # clear window to either display error or new window/widget
        for widget in self.winfo_children():
            if widget != self.button_frame:
                widget.destroy()

    def toggle_colorblind_mode(self):
        # toggle colorblind mode
        self.colorblind_mode = not self.colorblind_mode
        self.update_button_colors()

    def update_colorblind_mode(self, mode):
        # use flag to determine if colorblind mode is on or off
        self.colorblind_mode = mode != "None"
        self.colorblind_type = mode
        self.update_button_colors()

    def set_button_colors(self, *buttons):
        # Set colors for specified buttons based on colorblind type
        palette = self.colorblind_palette.get(self.colorblind_type, self.regular_palette)

        for button in buttons:
            if button["text"] in ["Confirm", "Submit"]:
                button.configure(bg=palette["confirm_bg"], fg="white")
            elif button["text"] == "Back":
                button.configure(bg=palette["back_bg"], fg="white")

    def update_button_colors(self):
        # Update colors for all buttons in the window
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) and widget["text"] in ["Confirm", "Submit", "Back"]:
                self.set_button_colors(widget)


# this function is created to show different types of relationships that the csv file may have, it creates histograms
# based of the input, makes a heatmap, pairplot and more can be made however, i limited it to just these to 1) not
# overwhelm the person but 2) as a potential change, i could make a new child GUI, put buttons in and make it create
# different graphs based of different inputs e.g. if i want a bar chart of x and y, the user would be able to select
# that from the file and print it with a button, but this is just a concept for the time being
class GraphSelectionWindow(tk.Toplevel):
    def __init__(self, parent, headers):
        super().__init__(parent)
        self.parent = parent
        self.headers = headers
        self.selected_headers = []
        self.graph_type = tk.StringVar(value="histogram")

        self.title("Graph Selection")
        self.geometry("500x600")

        # Create widgets for header selection and graph type
        header_frame = tk.Frame(self)
        header_frame.pack(pady=10)

        header_label = tk.Label(header_frame, text="Select headers to compare (max 10):")
        header_label.pack()

        self.header_var = tk.StringVar()
        self.header_dropdown = tk.OptionMenu(header_frame, self.header_var, *self.headers)
        self.header_dropdown.pack()

        button_frame = tk.Frame(header_frame)
        button_frame.pack()

        add_button = tk.Button(button_frame, text="+", command=self.add_header)
        add_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(button_frame, text="-", command=self.delete_header)
        delete_button.pack(side=tk.LEFT, padx=5)

        self.selected_headers_listbox = tk.Listbox(header_frame, height=10)
        self.selected_headers_listbox.pack(fill=tk.BOTH, expand=True)

        graph_type_frame = tk.Frame(self)
        graph_type_frame.pack(pady=10)

        graph_type_label = tk.Label(graph_type_frame, text="Select graph type:")
        graph_type_label.pack()

        graph_types = ["Histogram", "Line Plot", "Scatter Plot", "Box Plot", "Pair Plot", "Heatmap"]
        for graph in graph_types:
            tk.Radiobutton(graph_type_frame, text=graph, variable=self.graph_type, value=graph.lower()).pack(
                anchor=tk.W)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.visualize_button = tk.Button(button_frame, text="Visualize")
        self.visualize_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.LEFT, padx=5)

    def add_header(self):
        # Add selected header to the list
        selected_header = self.header_var.get()
        if selected_header and len(self.selected_headers) < 10:
            self.selected_headers.append(selected_header)
            self.selected_headers_listbox.insert(tk.END, selected_header)

    def delete_header(self):
        # Delete selected header from the list
        selected_index = self.selected_headers_listbox.curselection()
        if selected_index:
            self.selected_headers_listbox.delete(selected_index)
            del self.selected_headers[selected_index[0]]

    def visualize(self):
        # Visualize selected headers with chosen graph type
        if len(self.selected_headers) < 2:
            messagebox.showwarning("Warning", "Please select at least 2 headers.")
            logger.warning("Insufficient headers selected for visualization.")
            return

        self.destroy()


class GraphTheory:
    def __init__(self):
        self.data = None

    def visualize_histogram(self, column, graph_window):
        # Visualize histogram for a given column
        try:
            if self.data is not None:
                fig = Figure(figsize=(6, 4), dpi=100)
                ax = fig.add_subplot(111)

                # Convert the data to a DataFrame
                data = pd.DataFrame(self.data[column], columns=[column])

                sns.histplot(data=data, x=column, ax=ax)
                ax.set_xlabel(column)
                ax.set_ylabel('Frequency')
                ax.set_title(f'Histogram of {column}')

                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                print("DataFrame is empty. Please load data first.")
                logger.warning("DataFrame is empty. Please load data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the histogram: {str(e)}")
            logger.error(f"An error occurred while creating the histogram: {str(e)}")

    def visualize_line_plot(self, x_column, y_column, graph_window):
        # Visualize line plot for given x and y columns
        try:
            if self.data is not None:
                fig = Figure(figsize=(6, 4), dpi=100)
                ax = fig.add_subplot(111)

                # Convert the data to a DataFrame
                data = pd.DataFrame(self.data[[x_column, y_column]])

                sns.lineplot(x=x_column, y=y_column, data=data, ax=ax)
                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
                ax.set_title(f'Line Plot of {y_column} against {x_column}')

                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                print("DataFrame is empty. Please load data first.")
                logger.warning("DataFrame is empty. Please load data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the line plot: {str(e)}")
            logger.error(f"An error occurred while creating the line plot: {str(e)}")

    def visualize_scatter_plot(self, x_column, y_column, graph_window):
        # Visualize scatter plot for given x and y columns
        try:
            if self.data is not None:
                fig = Figure(figsize=(6, 4), dpi=100)
                ax = fig.add_subplot(111)

                # Convert the data to a DataFrame
                data = pd.DataFrame(self.data[[x_column, y_column]])

                sns.scatterplot(x=x_column, y=y_column, data=data, ax=ax)
                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
                ax.set_title(f'Scatter Plot of {y_column} against {x_column}')

                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                print("DataFrame is empty. Please load data first.")
                logger.warning("DataFrame is empty. Please load data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the scatter plot: {str(e)}")
            logger.error(f"An error occurred while creating the scatter plot: {str(e)}")

    def visualize_box_plot(self, column, graph_window):
        # Visualize box plot for a given column
        try:
            if self.data is not None:
                fig = Figure(figsize=(6, 4), dpi=100)
                ax = fig.add_subplot(111)

                # Convert the data to a DataFrame
                data = pd.DataFrame(self.data[column], columns=[column])

                sns.boxplot(x=column, data=data, ax=ax)
                ax.set_xlabel(column)
                ax.set_ylabel('Value')
                ax.set_title(f'Box Plot of {column}')

                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                print("DataFrame is empty. Please load data first.")
                logger.warning("DataFrame is empty. Please load data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the box plot: {str(e)}")
            logger.error(f"An error occurred while creating the box plot: {str(e)}")

    def visualize_pairplot(self, graph_window):
        # Visualize pair plot
        try:
            if self.data is not None:
                fig = sns.pairplot(self.data)
                fig.fig.suptitle("Pair Plot")
                fig.fig.subplots_adjust(top=0.95)

                canvas = FigureCanvasTkAgg(fig.fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                print("DataFrame is empty. Please load data first.")
                logger.warning("DataFrame is empty. Please load data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the pair plot: {str(e)}")
            logger.error(f"An error occurred while creating the pair plot: {str(e)}")

    def visualize_correlation_heatmap(self, graph_window):
        # Visualize correlation heatmap
        try:
            if self.data is not None:
                fig = Figure(figsize=(8, 6), dpi=100)
                ax = fig.add_subplot(111)

                sns.heatmap(self.data.corr(), annot=True, cmap='coolwarm', ax=ax)
                ax.set_title('Correlation Heatmap')

                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                print("DataFrame is empty. Please load data first.")
                logger.warning("DataFrame is empty. Please load data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the correlation heatmap: {str(e)}")
            logger.error(f"An error occurred while creating the correlation heatmap: {str(e)}")


class PredictionAlgorithm:
    def __init__(self):
        self.file = None
        self.columns = []
        self.data = None

    # loading and pre-processing the columns
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
        # Evaluate models using MLPRegressor
        file = self.file
        scaler = MinMaxScaler()
        file[self.columns] = scaler.fit_transform(file[self.columns])
        X = file[self.columns]
        y = file['Size']
        X = scaler.fit_transform(X)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=1000, activation='relu', random_state=42)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        num_predictions_to_print = int(0.2 * len(predictions))  # add user control
        predictions_df = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
        print(predictions_df.head(num_predictions_to_print))
        logger.info("Models evaluated successfully.")

        # Visualize actual vs. predicted values
        plt.figure(figsize=(8, 6))
        plt.scatter(y_test, predictions)
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title('Actual vs. Predicted Values')
        plt.grid(True)
        plt.show()

        # Visualize density plot of predicted values
        plt.figure(figsize=(8, 6))
        sns.kdeplot(predictions, label='Predicted', fill=True)
        plt.xlabel('Predicted Values')
        plt.ylabel('Density')
        plt.title('Density Plot of Predicted Values')
        plt.legend()
        plt.grid(True)
        plt.show()


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
        # self.sheet_listbox = tk.Listbox(self.window, selectmode=tk.SINGLE, yscrollcommand=self.y_scrollbar.set)
        # self.sheet_listbox.pack(fill=tk.BOTH, expand=True)
        #
        # # Bind double-click event on the listbox to select the sheet
        # self.sheet_listbox.bind('<Double-Button-1>', self.select_sheet)

        # Send file to other classes
        self.db_handler = DatabaseHandler("postgresql://neojoker26:password123@localhost:5432/dissertation")
        self.neural_network = PredictionAlgorithm()
        self.visualise = GraphTheory()

        # Event object for threading
        self.stop_event = threading.Event()

    def main(self):
        # Start a thread for displaying stats
        stats_thread = threading.Thread(target=self.display_stats, daemon=True)
        stats_thread.start()

        # Start the main tkinter window
        self.window.mainloop()

        # Set stop event and wait for stats thread to join
        self.stop_event.set()
        stats_thread.join()

    def display_stats(self):
        # Display CPU and memory utilization stats
        cpu_percent = psutil.cpu_percent(interval=None)
        memory_percent = psutil.virtual_memory().percent

        print(f"CPU Utilization: {cpu_percent}%")
        print(f"Memory Utilization: {memory_percent}%")

        # Schedule the next call to display_stats after 10 seconds
        self.window.after(10000, self.display_stats)

    def open_file(self):
        try:
            # Open a file dialog to select a CSV or Excel file
            self.file_path = filedialog.askopenfilename(filetypes=[
                ("CSV Files", "*.csv"),
                ("Excel Files", "*.xlsx *.xls"),
                ("All Files", "*.*")
            ])
            if self.file_path:
                if self.file_path.endswith(".csv"):
                    self.parse_csv()
                # elif self.file_path.endswith((".xlsx", ".xls")):
                #     self.parse_excel(self.file_path)
                else:
                    messagebox.showerror("Error", "Unsupported file type. Please select a CSV or Excel file.")
                    logger.error("Unsupported file type. Please select a CSV or Excel file.")
        except FileNotFoundError:
            messagebox.showerror("Error", "File was not found.")
            logger.error("File was not found.")
        except PermissionError:
            messagebox.showerror("Error", "Permission denied")
            logger.error("Permission denied")
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred  {str(e)}")
            logger.error(f"Error occurred: {str(e)}")

    def parse_csv(self):
        # Parse CSV file and display content in text box
        try:
            # Clear the text box
            self.text_box.delete('1.0', tk.END)
            # Read the file in binary mode to detect encoding
            with open(self.file_path, 'rb') as f:
                rawdata = f.read()
            # Detect the encoding of the file
            encoding = chardet.detect(rawdata)['encoding']
            # Read the CSV file using detected encoding
            df = pd.read_csv(self.file_path, encoding=encoding)
            # Insert CSV data into the text box
            self.text_box.insert(tk.END, df.to_string(index=False))
            # Store the DataFrame in self.data
            self.data = df
            # Enable buttons for sending data to database and ML model, and visualization
            self.send_to_db_button['state'] = tk.NORMAL
            self.send_to_ml_button['state'] = tk.NORMAL
            self.visualize_button['state'] = tk.NORMAL
        except Exception as e:
            # Handle any errors and print error message
            print("Error:", e)

    # def parse_excel(self, file_path):
    #     try:
    #         self.text_box.delete('1.0', tk.END)
    #         self.sheet_listbox.delete(0, tk.END)
    #         excel_file = pd.ExcelFile(file_path)
    #         self.sheet_names = excel_file.sheet_names
    #         for sheet_name in self.sheet_names:
    #             self.sheet_listbox.insert(tk.END, sheet_name)
    #     except Exception as e:
    #         print("Error parsing Excel file:", e)
    #
    # def select_sheet(self, event):
    #     selected_index = self.sheet_listbox.curselection()
    #     if selected_index:
    #         selected_sheet = self.sheet_listbox.get(selected_index)
    #         excel_file = pd.ExcelFile(self.file_path)
    #         try:
    #             df = excel_file.parse(selected_sheet)
    #             self.text_box.delete('1.0', tk.END)
    #             self.text_box.insert(tk.END, df.to_string(index=False))
    #             self.data = df
    #
    #             self.send_to_db_button['state'] = tk.NORMAL
    #             self.send_to_ml_button['state'] = tk.NORMAL
    #             self.visualize_button['state'] = tk.NORMAL
    #         except Exception as e:
    #             print(f"Error parsing sheet '{selected_sheet}':", e)

    def send_to_database(self):
        # Send data to database CRUD window
        if self.data is not None:
            # Open CRUD window for database interaction
            crud_window = CRUDWindow(self.window, self.data, self.db_handler)
            crud_window.mainloop()
        else:
            print("No file data loaded.")
            logger.info("No file data loaded.")

    def send_to_ml(self):
        # Send data to ML model for evaluation
        if self.data is not None:
            # Load data into neural network and evaluate models
            self.neural_network.load_data(self.data)
            self.neural_network.evaluate_models()
        else:
            print("No file data loaded.")
            logger.info("No file data loaded.")

    def visualize_data(self):
        # Visualize data using graph selection window
        if self.data is not None:
            # Create graph selection window with headers
            headers = list(self.data.columns)
            graph_selection_window = GraphSelectionWindow(self.window, headers)
            # Configure visualize button to create graph
            graph_selection_window.visualize_button.config(command=lambda: self.create_graph(graph_selection_window))
        else:
            print("No file data loaded.")
            logger.info("No file data loaded.")

    def create_graph(self, graph_selection_window):
        # Create graph based on selected headers and graph type
        selected_headers = graph_selection_window.selected_headers
        graph_type = graph_selection_window.graph_type.get()

        if selected_headers:
            self.visualise_df = GraphTheory()
            self.visualise_df.data = self.data[selected_headers]

            # Analyze selected variables and provide suggestions
            suggestions = []

            if len(selected_headers) == 1:
                # Univariate analysis suggestions
                suggestions.append(
                    "For a single variable, consider using a histogram or box plot to visualize its distribution and "
                    "identify outliers.")

            elif len(selected_headers) == 2:
                # Bivariate analysis suggestions
                suggestions.append("For two variables, a scatter plot is effective in visualizing their relationship.")
                suggestions.append(
                    "If one variable is categorical and the other is numerical, consider using a violin plot or box "
                    "plot.")
                suggestions.append(
                    "Computing the correlation coefficient can provide insights into the strength and direction of "
                    "the relationship.")

            else:
                # Multivariate analysis suggestions
                suggestions.append(
                    "For multiple variables, a pair plot can help visualize pairwise relationships, while a "
                    "correlation heatmap identifies correlations among them.")
                suggestions.append(
                    "Principal Component Analysis (PCA) can be applied to reduce the dimensionality of the data.")

            # Check data types of selected headers
            data_types = self.data[selected_headers].dtypes
            if all(data_types == 'float64') or all(data_types == 'int64'):
                # Suggestions for numerical data
                suggestions.append(
                    "As all selected variables are numerical, consider calculating summary statistics such as mean, "
                    "median, and standard deviation.")
                suggestions.append(
                    "Exploring the distribution of each variable using histograms or density plots can provide "
                    "valuable insights.")

            elif any(data_types == 'object'):
                # Suggestions for categorical data
                suggestions.append(
                    "For categorical variables, bar plots or count plots can visualize the frequency distribution.")
                suggestions.append(
                    "Stacked or grouped bar plots can be used to compare categories across different variables.")

            # Suggestions for data transformations and aggregations
            if len(selected_headers) >= 2:
                suggestions.append(
                    "Consider computing ratios, differences, or sums between selected columns to derive new "
                    "meaningful features. Aggregating the data by a categorical variable and calculating summary "
                    "statistics can reveal patterns.")

            # Show consolidated suggestions in one messagebox
            messagebox.showinfo("Suggestions", "\n\n".join(suggestions))
            logger.info("Display suggestions for graph visualization.")

            # Visualize the selected graph type in a new window
            try:
                if graph_type == "histogram":
                    graph_window = tk.Toplevel(self.window)
                    graph_window.title("Histogram")
                    for header in selected_headers:
                        self.visualise_df.visualize_histogram(header, graph_window)
                elif graph_type == "line plot":
                    if len(selected_headers) == 2:
                        graph_window = tk.Toplevel(self.window)
                        graph_window.title("Line Plot")
                        self.visualise_df.visualize_line_plot(selected_headers[0], selected_headers[1], graph_window)
                    else:
                        messagebox.showwarning("Warning", "Line plot requires exactly 2 headers.")
                elif graph_type == "scatter plot":
                    if len(selected_headers) == 2:
                        graph_window = tk.Toplevel(self.window)
                        graph_window.title("Scatter Plot")
                        self.visualise_df.visualize_scatter_plot(selected_headers[0], selected_headers[1], graph_window)
                    else:
                        messagebox.showwarning("Warning", "Scatter plot requires exactly 2 headers.")
                elif graph_type == "box plot":
                    graph_window = tk.Toplevel(self.window)
                    graph_window.title("Box Plot")
                    for header in selected_headers:
                        self.visualise_df.visualize_box_plot(header, graph_window)
                elif graph_type == "pair plot":
                    graph_window = tk.Toplevel(self.window)
                    graph_window.title("Pair Plot")
                    self.visualise_df.visualize_pairplot(graph_window)
                elif graph_type == "heatmap":
                    graph_window = tk.Toplevel(self.window)
                    graph_window.title("Correlation Heatmap")
                    self.visualise_df.visualize_correlation_heatmap(graph_window)
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while visualizing the data: {str(e)}")
                logger.error("Error occurred while visualizing the data.")


if __name__ == "__main__":
    window = WindowMaker()
    window.main()
