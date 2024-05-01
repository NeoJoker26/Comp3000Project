import os
import tkinter as tk
from datetime import datetime
from tkinter import ttk, filedialog, messagebox

import netifaces
import numpy as np
import pandas as pd
import chardet
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, explained_variance_score, max_error, \
    mean_squared_log_error, median_absolute_error
from sklearn.model_selection import train_test_split, cross_val_predict
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import MinMaxScaler
import psycopg2
from sqlalchemy import column
from database import DatabaseHandler
import psutil
import threading
import logging
import csv
from netmiko import ConnectHandler
import subprocess
import platform
import re

# start global logger
logger = logging.getLogger(__name__)

# noinspection PyAttributeOutsideInit
""" 
CRUD window + Scripts for SQLALchemy/PostgreSQL work
This class basically inits the CRUD window (Create, read, update, delete and scripts)
I wanted the buttons to be universally availble so i set them up in the init, i then created a few modular functions per
function if that makes sense? 
I also added a logger and auditor for security purposes, if the user presses a button, the system will log it to the 
audit file (audit.log)
Added a colorblind option for the buttons so if the user is colorblind, they can see the buttons
I also tried to make the error/log messages quite professional as if the app ever does become a large scale application,
the tech that works with it wont have to worry about the error/log messages, it wont seem like some junior has written
the error messages and it also lets the tech diagnose the error/log messages
i.e. if the db isnt connected, error/log shows up, if the db is missing a PK, the tech is notified 
I wanted to make everything modular so if someone does acquire this app they can easily workout what is what, what is 
where and how to edit things with ease
"""


class CRUDWindow(tk.Toplevel):
    def __init__(self, parent, data, db_handler, file_path):
        # Call the constructor of the superclass
        super().__init__(parent)
        self.parent = parent
        self.data = data
        self.db_handler = db_handler
        self.file_path = file_path
        self.colorblind_mode = False  # Flag for colorblind mode
        self.colorblind_type = "None"  # Default colorblind type

        # Create an audit logger
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        audit_handler = logging.FileHandler('audit.log')
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter('%(asctime)s - %(message)s')
        audit_handler.setFormatter(audit_formatter)
        self.audit_logger.addHandler(audit_handler)

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
        self.create_button = ttk.Button(self.button_frame, text="Create", command=self.create_entry)
        self.create_button.pack(side=tk.LEFT, padx=10)

        # Read button
        self.read_button = ttk.Button(self.button_frame, text="Read", command=self.visualise)
        self.read_button.pack(side=tk.LEFT, padx=10)

        # Update button
        self.update_button = ttk.Button(self.button_frame, text="Update", command=self.update_entry)
        self.update_button.pack(side=tk.LEFT, padx=10)

        # Delete button
        self.delete_button = ttk.Button(self.button_frame, text="Delete", command=self.delete_entry)
        self.delete_button.pack(side=tk.LEFT, padx=10)

        # Scripts button
        self.scripts_button = ttk.Button(self.button_frame, text="Scripts", command=self.run_scripts)
        self.scripts_button.pack(side=tk.LEFT, padx=10)

        # Colorblind mode dropdown
        self.colorblind_var = tk.StringVar()
        colorblind_options = ["None", "Protanopia", "Deuteranopia", "Tritanopia"]
        colorblind_dropdown = ttk.OptionMenu(self.button_frame, self.colorblind_var, *colorblind_options,
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

        # Method for setting button colors
        self.set_button_colors(confirm_button, back_button)

        self.audit_logger.info(f"User clicked 'Create' button")

    def submit_data(self):
        # Check if all input fields are filled
        if all(entry.get() for entry in self.input_fields):
            values = [entry.get() for entry in self.input_fields]
            try:
                # Append new data to the CSV file
                with open(self.file_path, 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(values)
                # Create new banana in the database
                banana_id = self.db_handler.create_banana(*values)
                messagebox.showinfo("Success",
                                    f"New entry appended to the CSV file and created in the database with id: {banana_id}")
                logger.info(f"New entry appended to the CSV file and created in the database with id: {banana_id}")
            except AttributeError as e:
                messagebox.showerror("Error", f"The file path is not accessible: {str(e)}")
                logger.error(f"The file path is not accessible: {str(e)}")
                print("The new entry could not be appended because the file path is not accessible.")
            except Exception as e:
                messagebox.showerror("Error",
                                     f"An error occurred while appending data to the CSV file and creating a new banana entry: {str(e)}")
                logger.error(
                    f"An error occurred while appending data to the CSV file and creating a new banana entry: {str(e)}")
                print(
                    "The new entry could not be appended and created due to file permissions, "
                    "file corruption, or database connectivity issues.")
        else:
            messagebox.showerror("Error", "Please enter all fields.")
            logger.error("Error occurred while entering data.")
            print(
                "The new entry was not appended and created because some input fields were left empty.")

    def update_entry(self):
        self.clear_window()

        # Create a frame for updating
        update_frame = tk.Frame(self)
        update_frame.pack(pady=10)

        # experimenting with different style of using fonts, tempted to make this a self.font and then use that for
        # every font in the CRUD class
        font_style = ("Helvetica", 12)

        """ Label and entry for the banana ID, this is probably the best way i can think of to make this gui,
         manual entering instead of searching through an index, this db has 8000 + my own creations but imagine
        scrolling through a million, of even more, i will also want to add a feature that searches for the other
         criteria but for now this is the only concept i have
        """
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

        self.audit_logger.info(f"User clicked 'Update' button")

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
        try:
            # Update data in the CSV file
            updated_data = []
            with open(self.file_path, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == str(banana_id):
                        updated_data.append(values)
                    else:
                        updated_data.append(row)
            with open(self.file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(updated_data)
            # Update banana data in the database
            updated_banana = self.db_handler.update_banana(banana_id, **banana_data)
            if updated_banana:
                messagebox.showinfo("Success", "Banana data updated successfully in the CSV file and database.")
                logger.info("Banana data updated successfully in the CSV file and database.")
            else:
                messagebox.showerror("Error", "Failed to update banana data in the database.")
                logger.error("Failed to update banana data in the database.")
                print(
                    "The banana data could not be updated in the database due to connectivity issues or invalid data.")
        except AttributeError as e:
            messagebox.showerror("Error", f"The file path is not accessible: {str(e)}")
            logger.error(f"The file path is not accessible: {str(e)}")
            print("The banana data could not be updated because the file path is not accessible.")
        except Exception as e:
            messagebox.showerror("Error",
                                 f"An error occurred while updating banana data in the CSV file and database: {str(e)}")
            logger.error(f"An error occurred while updating banana data in the CSV file and database: {str(e)}")
            print(
                "The banana data could not be updated due to file permissions, file corruption, or database connectivity issues.")

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

        self.audit_logger.info(f"User clicked 'Delete' button")

    def delete_banana(self, banana_id):
        # Delete data from the CSV file and database
        if banana_id:
            try:
                banana_id = int(banana_id)
                # Delete data from the CSV file
                updated_data = []
                with open(self.file_path, 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        if row[0] != str(banana_id):
                            updated_data.append(row)
                with open(self.file_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(updated_data)
                # Delete banana data from the database
                success = self.db_handler.delete_banana(banana_id)
                if success:
                    messagebox.showinfo("Success", "Banana data deleted successfully from the CSV file and database.")
                    logger.info("Banana data deleted successfully from the CSV file and database.")
                else:
                    messagebox.showerror("Error", "Failed to delete banana data from the database.")
                    logger.error("Failed to delete banana data from the database.")
                    print(
                        "The banana data could not be deleted from the database due to connectivity issues or invalid data.")
            except ValueError:
                messagebox.showerror("Error", "Invalid Banana ID. Please enter a valid integer.")
                logger.error("Invalid Banana ID. Please enter a valid integer.")
                print("The banana data was not deleted because an invalid ID was entered.")
            except AttributeError as e:
                messagebox.showerror("Error", f"The file path is not accessible: {str(e)}")
                logger.error(f"The file path is not accessible: {str(e)}")
                print("The banana data could not be deleted because the file path is not accessible.")
            except Exception as e:
                messagebox.showerror("Error",
                                     f"An error occurred while deleting banana data from the CSV file and database: {str(e)}")
                logger.error(f"An error occurred while deleting banana data from the CSV file and database: {str(e)}")
                print(
                    "The banana data could not be deleted due to file permissions, file corruption, or database connectivity issues.")
        else:
            messagebox.showerror("Error", "Please enter a Banana ID.")
            logger.error("Please enter a Banana ID.")
            print("The banana data was not deleted because no ID was entered.")

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
                    self.audit_logger.info(f"User clicked 'Read' button with Banana ID: {banana_id}")
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

    def run_scripts(self):
        script_window = tk.Toplevel(self)  # Create a new window for running scripts
        script_window.title("Scripts")  # Set the title of the script window
        script_window.geometry("800x1000")  # Set the size of the script window

        # Create a frame for the script selection
        script_frame = tk.Frame(script_window)
        script_frame.pack(pady=10)

        # Create a listbox for script selection
        script_listbox = tk.Listbox(script_frame, height=10, width=60)
        script_listbox.pack()

        # Add script options to the listbox
        script_options = [
            "Show bottom 100",
            "Show top 100",
            "Count records",
            "Calculate average for column",
            "Find maximum value for column",
            "Find minimum value for column"
        ]

        #  Iterate over the script options
        for option in script_options:
            # Insert each option into the script listbox
            script_listbox.insert(tk.END, option)

        # Create a frame for additional input fields
        input_frame = tk.Frame(script_window)
        input_frame.pack(pady=10)

        # Table name dropdown menu
        table_label = tk.Label(input_frame, text="Select table:")
        # Create a label for table selection
        table_label.grid(row=0, column=0, sticky="e")

        # Position the table label in the input frame
        table_var = tk.StringVar(script_window)
        # Create a StringVar to hold the selected table

        table_dropdown = tk.OptionMenu(input_frame, table_var, "")
        # Create a dropdown menu for table selection
        table_dropdown.grid(row=0, column=1)

        # Column name dropdown menu
        column_label = tk.Label(input_frame, text="Select column:")
        column_label.grid(row=1, column=0, sticky="e")
        column_var = tk.StringVar(script_window)
        column_dropdown = tk.OptionMenu(input_frame, column_var, "")
        column_dropdown.grid(row=1, column=1)

        # Populate table and column dropdown menus
        table_names = self.db_handler.get_table_names()
        table_var.set(table_names[0])  # Set the default selected table
        table_dropdown['menu'].delete(0, 'end')
        for table in table_names:
            # tk._setit is a method in Tkinter used to associate a variable with a value when an option is chosen
            # from a dropdown menu.
            table_dropdown['menu'].add_command(label=table, command=tk._setit(table_var, table))

        # used args to accept a number of positional arguments
        def update_column_dropdown(*args):
            #  Get the selected table
            selected_table = table_var.get()
            column_names = self.db_handler.get_column_names(selected_table)
            column_var.set(column_names[0])  # Set the default selected column
            column_dropdown['menu'].delete(0, 'end')
            for column in column_names:
                column_dropdown['menu'].add_command(label=column, command=tk._setit(column_var, column))

        table_var.trace('w', update_column_dropdown)

        # Create a text area to display the script results
        result_text = tk.Text(script_window, height=20, width=80)  # Increased text area size
        result_text.pack(pady=10)

        def run_selected_script():
            # Get the selected indices from the script listbox
            selected_indices = script_listbox.curselection()

            # Check if any script is selected
            if selected_indices:
                selected_script = script_listbox.get(selected_indices[0])
                table_name = table_var.get()
                column_name = column_var.get()

                # Audit log the selected script
                self.audit_logger.info(f"User ran script: {selected_script}")

                if selected_script == "Show bottom 100":
                    result = self.db_handler.show_bottom_100(table_name)
                    # Format the result as a string
                    formatted_result = '\n'.join(str(banana) for banana in result)
                    result_text.delete('1.0', tk.END)
                    # tk.END represents the end of the text widget
                    result_text.insert(tk.END, formatted_result)
                elif selected_script == "Show top 100":
                    result = self.db_handler.show_top_100(table_name)
                    formatted_result = '\n'.join(str(banana) for banana in result)
                    result_text.delete('1.0', tk.END)
                    result_text.insert(tk.END, formatted_result)
                elif selected_script == "Count records":
                    result = self.db_handler.count_records()
                    result_text.delete('1.0', tk.END)
                    result_text.insert(tk.END, str(result))
                elif selected_script == "Calculate average for column":
                    result = self.db_handler.calculate_average(column_name)
                    result_text.delete('1.0', tk.END)
                    result_text.insert(tk.END, str(result))
                elif selected_script == "Find maximum value for column":
                    result = self.db_handler.find_max_value(column_name)
                    result_text.delete('1.0', tk.END)
                    result_text.insert(tk.END, str(result))
                elif selected_script == "Find minimum value for column":
                    result = self.db_handler.find_min_value(column_name)
                    result_text.delete('1.0', tk.END)
                    result_text.insert(tk.END, str(result))
            else:
                messagebox.showinfo("No Selection", "Please select a script from the list.")

        # Create a button to run the selected script
        run_button = tk.Button(script_window, text="Run Script", command=run_selected_script)
        run_button.pack(pady=10)

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
            # check what button is chosen
            if button["text"] in ["Confirm", "Submit"]:
                button.configure(bg=palette["confirm_bg"], fg="white")
            elif button["text"] == "Back":
                button.configure(bg=palette["back_bg"], fg="white")

    def update_button_colors(self):
        # Update colors for all buttons in the window
        for widget in self.winfo_children():
            if isinstance(widget, tk.Button) and widget["text"] in ["Confirm", "Submit", "Back"]:
                self.set_button_colors(widget)


""" 
this function is created to show different types of relationships that the csv file may have, it creates histograms
#based of the input, makes a heatmap, pairplot and more can be made however, i limited it to just these to 1) not
#overwhelm the person but 2) as a potential change, i could make a new child GUI, put buttons in and make it create
 different graphs based of different inputs e.g. if i want a bar chart of x and y, the user would be able to select
 that from the file and print it with a button, but this is just a concept for the time being
"""


class GraphSelectionWindow(tk.Toplevel):
    def __init__(self, parent, headers):
        super().__init__(parent)
        self.parent = parent
        self.headers = headers
        self.selected_headers = []
        self.graph_type = tk.StringVar(value="histogram")

        self.title("Graph Selection")
        self.geometry("500x600")

        # Create frames for header selection and graph type
        header_frame = tk.Frame(self)
        header_frame.pack(pady=10)

        graph_type_frame = tk.Frame(self)
        graph_type_frame.pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        # Create widgets for header selection
        header_label = ttk.Label(header_frame, text="Select headers to compare (max 10):")
        header_label.grid(row=0, column=0, sticky="w")

        self.header_var = tk.StringVar()
        self.header_dropdown = ttk.OptionMenu(header_frame, self.header_var, *self.headers)
        self.header_dropdown.grid(row=1, column=0, sticky="w")

        add_button = ttk.Button(header_frame, text="+", command=self.add_header)
        add_button.grid(row=1, column=1, padx=5)

        delete_button = ttk.Button(header_frame, text="-", command=self.delete_header)
        delete_button.grid(row=1, column=2, padx=5)

        self.selected_headers_listbox = tk.Listbox(header_frame, height=10)
        self.selected_headers_listbox.grid(row=2, column=0, columnspan=3, sticky="ew")

        # Create widgets for graph type selection
        graph_type_label = ttk.Label(graph_type_frame, text="Select graph type:")
        graph_type_label.grid(row=0, column=0, sticky="w")

        graph_types = ["Histogram", "Line Plot", "Scatter Plot", "Box Plot", "Pair Plot", "Heatmap"]
        for i, graph in enumerate(graph_types):
            ttk.Radiobutton(graph_type_frame, text=graph, variable=self.graph_type, value=graph.lower()).grid(row=i + 1,
                                                                                                              column=0,
                                                                                                              sticky="w")

        # Create visualize and cancel buttons
        self.visualize_button = ttk.Button(button_frame, text="Visualize")
        self.visualize_button.pack(side=tk.LEFT, padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
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


"""
This class is where i use seaborn and matplotlib to make different graphs based of different inputs
i could add alot more however too many graphs may be counter intuitive 
I also set it to a min of 2 so that the user can compare different graphs based of different inputs as opposed to just 
visualsing one graph and having less data (as the aim of this app is to show relationships between different columns in 
a database/file
once again i tried to make the error messages professional and added a logger so that once again, if there is a tech
they can see what is going wrong or if not a tech then a user
"""


class GraphTheory:
    def __init__(self):
        self.data = None

    def visualize_histogram(self, column, graph_window):
        # Visualize histogram for a given column
        try:
            if self.data is not None:
                # Create a Figure object, set to large size but open to change for user preference
                fig = Figure(figsize=(6, 4), dpi=100)
                # Add a subplot to the figure
                ax = fig.add_subplot(111)

                # Convert the data to a DataFrame
                data = pd.DataFrame(self.data[column], columns=[column])

                # create hisogram with seaborn, set some specifics but once again, open to user preference
                sns.histplot(data=data, x=column, ax=ax, kde=True, color='skyblue', bins=20, edgecolor='black',
                             alpha=0.7)
                ax.set_xlabel(column)
                ax.set_ylabel('Frequency')
                ax.set_title(f'Histogram of {column}')
                ax.legend([column])

                # Add mean and median vertical lines
                mean = data[column].mean()
                median = data[column].median()
                ax.axvline(mean, color='red', linestyle='--', label=f'Mean: {mean:.2f}')
                ax.axvline(median, color='green', linestyle='--', label=f'Median: {median:.2f}')
                ax.legend()

                # Create a FigureCanvasTkAgg object to display the plot in the graph window
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

                sns.lineplot(x=x_column, y=y_column, data=data, ax=ax, color='blue', linewidth=2, marker='o',
                             markersize=6)
                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
                ax.set_title(f'Line Plot of {y_column} against {x_column}')

                # Add value labels to data points
                for x, y in zip(data[x_column], data[y_column]):
                    ax.text(x, y, f'({x:.2f}, {y:.2f})', fontsize=8, ha='left', va='bottom')

                # Add grid lines
                ax.grid(True, linestyle='--', alpha=0.7)

                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                print("DataFrame is empty. Please load data first.")
                logger.warning("DataFrame is empty. Please load data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the line plot: {str(e)}")
            logger.error(f"An error occurred while creating the line plot: {str(e)}")

    def visualize_scatter_plot(self, x_column, y_column, graph_window, hue_column=None):
        # Visualize scatter plot for given x and y columns
        try:
            if self.data is not None:
                fig = Figure(figsize=(10, 8), dpi=150)
                ax = fig.add_subplot(111)

                # Convert the data to a DataFrame
                if hue_column is None:
                    data = pd.DataFrame(self.data[[x_column, y_column]])
                else:
                    data = pd.DataFrame(self.data[[x_column, y_column, hue_column]])

                if hue_column is None:
                    sns.scatterplot(x=x_column, y=y_column, data=data, ax=ax, color='darkblue', s=60, alpha=0.7)
                else:
                    sns.scatterplot(x=x_column, y=y_column, hue=hue_column, data=data, ax=ax, palette='viridis', s=60,
                                    alpha=0.7)
                    ax.legend(title=hue_column, loc='upper right')

                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
                ax.set_title(f'Scatter Plot of {y_column} against {x_column}')

                # Add value labels to data points
                for _, row in data.iterrows():
                    ax.text(row[x_column], row[y_column], f'({row[x_column]:.2f}, {row[y_column]:.2f})', fontsize=8,
                            ha='left', va='bottom')

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
                fig = Figure(figsize=(8, 6), dpi=100)
                ax = fig.add_subplot(111)

                # Convert the data to a DataFrame
                data = pd.DataFrame(self.data[column], columns=[column])

                sns.boxplot(x=column, data=data, ax=ax, color='skyblue', linewidth=1.5, fliersize=3)
                ax.set_xlabel(column)
                ax.set_ylabel('Value')
                ax.set_title(f'Box Plot of {column}')

                # Add data points as scatter points
                sns.stripplot(x=column, data=data, ax=ax, color='darkblue', size=4, alpha=0.5)

                # Display statistical summary
                quartiles = data[column].quantile([0.25, 0.5, 0.75])
                q1, median, q3 = quartiles[0.25], quartiles[0.5], quartiles[0.75]
                iqr = q3 - q1
                ax.text(0.95, 0.95, f'Median: {median:.2f}\nQ1: {q1:.2f}, Q3: {q3:.2f}\nIQR: {iqr:.2f}',
                        transform=ax.transAxes, fontsize=10, ha='right', va='top',
                        bbox=dict(facecolor='white', alpha=0.8))

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
                fig = sns.pairplot(self.data, diag_kind='kde', height=3,
                                   aspect=1.5)
                fig.fig.suptitle("Pair Plot", fontsize=16)
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

                corr_matrix = self.data.corr()
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax, fmt='.2f', linewidths=0.5,
                            annot_kws={"fontsize": 10})
                ax.set_title('Correlation Heatmap')

                # Add a color bar
                cbar = ax.collections[0].colorbar
                cbar.ax.tick_params(labelsize=10)

                canvas = FigureCanvasTkAgg(fig, master=graph_window)
                canvas.draw()
                canvas.get_tk_widget().pack()
            else:
                print("DataFrame is empty. Please load data first.")
                logger.warning("DataFrame is empty. Please load data first.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while creating the correlation heatmap: {str(e)}")
            logger.error(f"An error occurred while creating the correlation heatmap: {str(e)}")


"""
This is the neural network, it took alot of tinkering to make it efficient and have good metrics
in this case, the concept file is used but whoever uses this application can simply change a few variables to adjust it 
to their goals
it is used for regressive tasks e.g., house price prediction or energy consumption prediction
however, a classifier could also be implemented with similar parameters
"""


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
                # Convert the column values to numeric type
                file[col] = pd.to_numeric(file[col])
                self.columns.append(col)
            except ValueError:
                # Drop the column if it cannot be converted to numeric type
                file = file.drop(col, axis=1)
                # Check if "banana_id" column exists in the file
        if "banana_id" in file.columns:
            # Drop the "banana_id" column from the file for purpose of testing as it is the primary key in the
            # database, once again, this can be changed per user choice, only added as a safety measure
            self.file = file.drop("banana_id", axis=1)

    # where the magic happens, the csv file is evaluated with the MLPRegressor model (neural network) and it shows
    # the next 20% predictions with graphs, this is tested at 97-98% accuracy
    def evaluate_models(self):
        # Evaluate models using MLPRegressor
        file = self.file
        # Create an instance of MinMaxScaler for feature scaling
        scaler = MinMaxScaler()
        file[self.columns] = scaler.fit_transform(file[self.columns])
        X = file[self.columns]
        y = file['Size']
        X = scaler.fit_transform(X)

        # this is a meticulously edited regressor, I have experimented with different test sizes (0.1,0.15, 0.2,
        # 0.25, 0.3) and 25% gave the best accuracy, random state made the least difference but anywhere from 30-50
        # returns the same/similar value, added shuffle for extra randomness layer wise, this was interesting as I
        # still have no clue how to perfect it BUT, this was a genuine pain, i started with 2 layers,
        # based the amount of layers on % of the "database" i was working (8000 inputs), started with 200,
        # 100 as a baseline (figured this would be good as its not too small and not too large) and then
        # experiemented. to my knowledge, layer 1 would work on the low level features and layer two would work on
        # the combining features to learn) After experimenting with i think over 20 different set ups (
        # decreasing/increasing both layers), i figured i would look at the documentation and i figured out there
        # could be more than 2 layers...However, the issue with having more layers does mean there is a higher chance
        # of overfitting or errors, i found that even if i add 1 more layer, there are more outliers and more
        # erroneous data. After discovering oh there can be more layers, i added a 3rd layer... and once again i had
        # to spend countless hours adjusting and experimenting with layers, this 150,75,25 has given me the best
        # metrics compared to my previous experiments next came the activation, this was simple as im working with
        # random data not, binary or hyperbolic solver once again was easy, from the 3 - adam, lbfgs, sgd - adam was
        # the fastest and most efficient alpha i tested between 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001,
        # this had the best score based of different metrics (to 7sf), each alpha i ran 3 times to confirm the
        # scores, unfortunately the scores werent TOO different, with the difference being very minor however,
        # this showed the best scores every time learning rate  also made little difference but once again,
        # i tested it 3 times and this gave the best score 2/3 time the iterations also make a difference,
        # if this code ever becomes open source, it would be best to adjust 1:8 (1 epoch per 8 inputs) as ive noticed
        # that after a while the iterations start to plateau, the lower the tol the technically better, ive set this
        # to such a small number so that it can be very precise finally, the batch size is set to auto as this does
        # depend on the system and if i adjust it to my set up, it may not be as good on another system
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=30, shuffle=True)
        model = MLPRegressor(hidden_layer_sizes=(150, 75, 25), activation='relu', solver='adam', alpha=0.01,
                             learning_rate='adaptive', max_iter=1000, random_state=42, tol=0.00001, batch_size='auto')
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        num_predictions_to_print = int(0.2 * len(predictions))  # add user control as a future option
        predictions_df = pd.DataFrame({'Actual': y_test, 'Predicted': predictions})
        print(predictions_df.head(num_predictions_to_print))
        logger.info("Models evaluated successfully.")

        # Call the function for neural network visualizations and statistics
        self.neural_network_visualisations_and_statistics(y_test, predictions, model, X_train, y_train)

    def neural_network_visualisations_and_statistics(self, y_test, predictions, model, X_train, y_train):
        # Scatter plot of actual vs. predicted values
        plt.figure(figsize=(8, 6))
        plt.scatter(y_test, predictions)
        plt.xlabel('Actual Values')
        plt.ylabel('Predicted Values')
        plt.title('Actual vs. Predicted Values')
        plt.grid(True)
        plt.show()

        # Density plot of predicted values
        plt.figure(figsize=(8, 6))
        sns.kdeplot(predictions, label='Predicted', fill=True)
        plt.xlabel('Predicted Values')
        plt.ylabel('Density')
        plt.title('Density Plot of Predicted Values')
        plt.legend()
        plt.grid(True)
        plt.show()

        # Distribution of prediction errors (residuals)
        residuals = y_test - predictions
        plt.figure(figsize=(8, 6))
        sns.histplot(residuals, kde=True)
        plt.xlabel('Prediction Errors')
        plt.ylabel('Frequency')
        plt.title('Distribution of Prediction Errors')
        plt.grid(True)
        plt.show()

        # Scatter plot of residuals vs. predicted values
        plt.figure(figsize=(8, 6))
        plt.scatter(predictions, residuals)
        plt.xlabel('Predicted Values')
        plt.ylabel('Residuals')
        plt.title('Residuals vs. Predicted Values')
        plt.grid(True)
        plt.axhline(y=0, color='r', linestyle='--')
        plt.show()

        # Mean Squared Error (MSE)
        mse = mean_squared_error(y_test, predictions)
        print(f"Mean Squared Error: {mse:.7f}")

        # R-squared score
        r2 = r2_score(y_test, predictions)
        print(f"R-squared Score: {r2:.7f}")

        # Explained variance score
        explained_variance = explained_variance_score(y_test, predictions)
        print(f"Explained Variance Score: {explained_variance:.7f}")

        # Mean Absolute Error (MAE)
        mae = mean_absolute_error(y_test, predictions)
        print(f"Mean Absolute Error: {mae:.7f}")

        # Root Mean Squared Error (RMSE)
        rmse = np.sqrt(mse)
        print(f"Root Mean Squared Error: {rmse:.4f}")

        # Max Error
        max_error_val = max_error(y_test, predictions)
        print(f"Max Error: {max_error_val:.7f}")

        # Mean Squared Logarithmic Error (MSLE)
        msle = mean_squared_log_error(y_test, predictions)
        print(f"Mean Squared Logarithmic Error: {msle:.7f}")

        # Median Squared Error
        median_se = median_absolute_error(y_test, predictions) ** 2
        print(f"Median Squared Error: {median_se:.7f}")

        # Cross-validation
        predictions_cv = cross_val_predict(model, X_train, y_train, cv=5)
        mse_cv = mean_squared_error(y_train, predictions_cv)
        r2_cv = r2_score(y_train, predictions_cv)
        print(f"Cross-Validation Mean Squared Error: {mse_cv:.7f}")
        print(f"Cross-Validation R-squared Score: {r2_cv:.7f}")


"""
 this is the main window, ive set it up like i did CRUD window, the main buttons are in the init and all the actions
 for the buttons are in modular functions, it took a while to design a good gui as i used a treeview at first but
 then i realised how laggy it was and how awful the scroll bars were so i removed it and just left it as a label,
"""


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

        # Create the main window
        self.window = tk.Tk()
        self.window.title("Data Analysis Tool")
        self.window.geometry("800x600")
        self.window.minsize(800, 600)

        # Create a frame for buttons
        self.button_frame = tk.Frame(self.window)
        self.button_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Create a frame for file information
        self.file_info_frame = tk.Frame(self.window)
        self.file_info_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        # Create a frame for the text box
        self.text_frame = tk.Frame(self.window)
        self.text_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Configure grid weights to make the text frame expandable
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # Create the "Open File" button
        self.open_button = ttk.Button(self.button_frame, text="Open File", command=self.open_file)
        self.open_button.grid(row=0, column=0, padx=5)

        # Create the "Send to Database" button (initially disabled)
        self.send_to_db_button = ttk.Button(self.button_frame, text="Send to Database", command=self.send_to_database,
                                            state=tk.DISABLED)
        self.send_to_db_button.grid(row=0, column=1, padx=5)

        # Create the "Send to Machine Learning" button (initially disabled)
        self.send_to_ml_button = ttk.Button(self.button_frame, text="Send to Machine Learning", command=self.send_to_ml,
                                            state=tk.DISABLED)
        self.send_to_ml_button.grid(row=0, column=2, padx=5)

        # Create the "Visualize" button (initially disabled)
        self.visualize_button = ttk.Button(self.button_frame, text="Visualize", command=self.visualize_data,
                                           state=tk.DISABLED)
        self.visualize_button.grid(row=0, column=3, padx=5)

        # Create the "Upload to PostgreSQL" button (initially disabled)
        self.upload_button = ttk.Button(self.button_frame, text="Upload to PostgreSQL",
                                        command=self.upload_to_postgresql, state=tk.DISABLED)
        self.upload_button.grid(row=0, column=4, padx=5)

        # Create VLAN Configuration button
        self.vlan_config_button = ttk.Button(self.button_frame, text="VLAN Configuration",
                                             command=self.configure_vlan_tagging, state=tk.DISABLED)
        self.vlan_config_button.grid(row=0, column=5, padx=5)

        # Create a label to display the selected file name
        self.label_filename = ttk.Label(self.file_info_frame, text="No file selected")
        self.label_filename.grid(row=0, column=0, sticky="w")

        # Create a text box with scrollbars
        self.text_box = tk.Text(self.text_frame, wrap=tk.NONE)
        self.text_box.grid(row=0, column=0, sticky="nsew")

        # Create a vertical scrollbar for the text box
        self.y_scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.VERTICAL, command=self.text_box.yview)
        self.y_scrollbar.grid(row=0, column=1, sticky="ns")

        # Create a horizontal scrollbar for the text box
        self.x_scrollbar = ttk.Scrollbar(self.text_frame, orient=tk.HORIZONTAL, command=self.text_box.xview)
        self.x_scrollbar.grid(row=1, column=0, sticky="ew")

        # Configure the text box to use the scrollbars
        self.text_box.config(yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)

        # Configure the text frame to expand with the window
        self.text_frame.grid_rowconfigure(0, weight=1)
        self.text_frame.grid_columnconfigure(0, weight=1)

        # Initialize variables for file path and data
        self.file_path = ""
        self.data = None

        # Initialize variables for sheets
        self.sheet_names = None
        self.sheet_data = {}

        # Create instances of other classes
        self.db_handler = DatabaseHandler("postgresql://neojoker26:password123@localhost:5432/dissertation")
        self.neural_network = PredictionAlgorithm()
        self.visualise = GraphTheory()

        # Create an event object for threading
        self.stop_event = threading.Event()

        # Create an audit logger
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        audit_handler = logging.FileHandler('audit.log')
        audit_handler.setLevel(logging.INFO)
        audit_formatter = logging.Formatter('%(asctime)s - %(message)s')
        audit_handler.setFormatter(audit_formatter)
        self.audit_logger.addHandler(audit_handler)

    """
    this is a static method that does take a bit to load however, the reason this is here is just incase this application
    is moved from one set of hardware to another e.g., from a linux server to solaris or some type of oracle server
    rack 
    it gatheres the user set up which would let a technician optimise the application for the bespoke hardware if need be
    it lists all connections and such so that is a VLAn is needed, the technician can set one up (or even the user if 
    need be)
    """

    @staticmethod
    def run_hardware_tests():
        messagebox.showinfo('Testing', 'Running hardware tests, please bare with the application for a moment')
        try:
            # Get operating system information
            os_name = platform.system()
            os_version = platform.release()
            logger.info(f'Operating System: {os_name} {os_version}')
            print(f'Operating System: {os_name} {os_version}')

            # Get CPU information
            cpu_info = psutil.cpu_freq()
            logger.info(f'CPU Information:')
            logger.info(f'  Frequency: {cpu_info.current:.2f} MHz')
            logger.info(f'  Core Count: {psutil.cpu_count()}')
            print(f'CPU Information:')
            print(f'  Frequency: {cpu_info.current:.2f} MHz')
            print(f'  Core Count: {psutil.cpu_count()}')

            # Get memory information
            memory_info = psutil.virtual_memory()
            logger.info(f'Memory Information:')
            logger.info(f'  Total: {memory_info.total / (1024 * 1024):.2f} MB')
            logger.info(f'  Available: {memory_info.available / (1024 * 1024):.2f} MB')
            print(f'Memory Information:')
            print(f'  Total: {memory_info.total / (1024 * 1024):.2f} MB')
            print(f'  Available: {memory_info.available / (1024 * 1024):.2f} MB')

            # Get disk information
            disk_info = psutil.disk_partitions()
            logger.info(f'Disk Information:')
            for partition in disk_info:
                logger.info(f'  Device: {partition.device}')
                logger.info(f'  Mountpoint: {partition.mountpoint}')
                logger.info(f'  File System Type: {partition.fstype}')
                usage = psutil.disk_usage(partition.mountpoint)
                logger.info(f'  Total Size: {usage.total / (1024 * 1024):.2f} MB')
                logger.info(f'  Used Space: {usage.used / (1024 * 1024):.2f} MB')
                logger.info(f'  Free Space: {usage.free / (1024 * 1024):.2f} MB')
                print(f'  Device: {partition.device}')
                print(f'  Mountpoint: {partition.mountpoint}')
                print(f'  File System Type: {partition.fstype}')
                print(f'  Total Size: {usage.total / (1024 * 1024):.2f} MB')
                print(f'  Used Space: {usage.used / (1024 * 1024):.2f} MB')
                print(f'  Free Space: {usage.free / (1024 * 1024):.2f} MB')

            # Get network information
            network_info = psutil.net_if_addrs()
            logger.info(f'Network Information:')
            for interface, addrs in network_info.items():
                logger.info(f'  Interface: {interface}')
                for addr in addrs:
                    if addr.family == 2:  # AF_INET (IPv4)
                        logger.info(f'    IP Address: {addr.address}')
                        logger.info(f'    Netmask: {addr.netmask}')
                        logger.info(f'    Broadcast: {addr.broadcast}')
                        print(f'  Interface: {interface}')
                        print(f'    IP Address: {addr.address}')
                        print(f'    Netmask: {addr.netmask}')
                        print(f'    Broadcast: {addr.broadcast}')

            # Run network topology check
            if os_name == 'Windows':
                topology_output = subprocess.check_output(['tracert', 'google.com'])
            else:
                topology_output = subprocess.check_output(['traceroute', 'google.com'])
            logger.info('Network Topology:')
            logger.info(topology_output.decode('utf-8'))
            print('Network Topology:')
            print(topology_output.decode('utf-8'))

            # Run VLAN tagging check
            if os_name == 'Windows':
                vlan_output = subprocess.check_output(['netsh', 'interface', 'ip', 'show', 'interfaces'])
            else:
                vlan_output = subprocess.check_output(['cat', '/proc/net/vlan/config'])
            logger.info('VLAN Tagging:')
            logger.info(vlan_output.decode('utf-8'))
            print('VLAN Tagging:')
            print(vlan_output.decode('utf-8'))


        except Exception as e:
            logger.error(f'Hardware test failed: {str(e)}')
            messagebox.showerror('Hardware Tests', 'Hardware tests failed')

        if platform.system() == 'Linux':
            try:
                # Run CPU stress test
                try:
                    cpu_test_output = subprocess.check_output(['stress-ng', '--cpu', '4', '--timeout', '30s'])
                    logger.info('CPU stress test completed')
                    logger.info(cpu_test_output.decode('utf-8'))
                    print('CPU stress test completed\n', cpu_test_output.decode('utf-8'))
                except FileNotFoundError:
                    logger.warning('stress-ng command not found. Skipping CPU stress test.')

                # Run memory test
                try:
                    memory_test_output = subprocess.check_output(['memtester', '1M', '1'])
                    logger.info('Memory test completed')
                    logger.info(memory_test_output.decode('utf-8'))
                    print('Memory test completed\n', memory_test_output.decode('utf-8'))
                except FileNotFoundError:
                    logger.warning('memtester command not found. Skipping memory test.')

                # Run disk test
                try:
                    disk_test_output = subprocess.check_output(['smartctl', '-t', 'short', '/dev/sda'])
                    logger.info('Disk test completed')
                    logger.info(disk_test_output.decode('utf-8'))
                    print('Disk test completed\n', disk_test_output.decode('utf-8'))
                except FileNotFoundError:
                    logger.warning('smartctl command not found. Skipping disk test.')

                # Run network test
                try:
                    network_test_output = subprocess.check_output(['ping', '-c', '4', 'google.com'])
                    logger.info('Network test completed')
                    logger.info(network_test_output.decode('utf-8'))
                    print('Network test completed\n', network_test_output.decode('utf-8'))
                except FileNotFoundError:
                    logger.warning('ping command not found. Skipping network test.')

                messagebox.showinfo('Hardware Tests', 'Hardware tests completed')
            except subprocess.CalledProcessError as e:
                logger.error(f'Hardware test failed: {str(e)}')
                messagebox.showerror('Hardware Tests', 'Hardware tests failed')

        elif platform.system() == 'Windows':
            try:
                # Run CPU stress test
                try:
                    cpu_test_output = subprocess.check_output(['wmic', 'cpu', 'get', 'LoadPercentage'])
                    logger.info('CPU stress test completed')
                    logger.info(cpu_test_output.decode('utf-8'))
                    print('CPU stress test completed\n', cpu_test_output.decode('utf-8'))
                except subprocess.CalledProcessError as e:
                    logger.warning(f'CPU stress test failed: {str(e)}')

                # Run memory test
                try:
                    memory_test_output = subprocess.check_output(['wmic', 'memorychip', 'get', 'Capacity'])
                    logger.info('Memory test completed')
                    logger.info(memory_test_output.decode('utf-8'))
                    print('Memory test completed\n', memory_test_output.decode('utf-8'))
                except subprocess.CalledProcessError as e:
                    logger.warning(f'Memory test failed: {str(e)}')

                # Run disk test
                try:
                    disk_test_output = subprocess.check_output(['wmic', 'diskdrive', 'get', 'Status'])
                    logger.info('Disk test completed')
                    logger.info(disk_test_output.decode('utf-8'))
                    print('Disk test completed\n', disk_test_output.decode('utf-8'))
                except subprocess.CalledProcessError as e:
                    logger.warning(f'Disk test failed: {str(e)}')

                # Run network test
                try:
                    network_test_output = subprocess.check_output(['ping', '-n', '4', 'google.com'])
                    logger.info('Network test completed')
                    logger.info(network_test_output.decode('utf-8'))
                    print('Network test completed\n', network_test_output.decode('utf-8'))
                except subprocess.CalledProcessError as e:
                    logger.warning(f'Network test failed: {str(e)}')

                messagebox.showinfo('Hardware Tests', 'Hardware tests completed')
            except Exception as e:
                logger.error(f'Hardware test failed: {str(e)}')
                messagebox.showerror('Hardware Tests', 'Hardware tests failed')
        else:
            messagebox.showinfo('Hardware Tests', 'Hardware tests are only supported on Linux and Windows.')

    def main(self):
        # Run hardware tests before starting the main application, does take a few seconds to run
        # self.run_hardware_tests()

        # Start a thread for displaying stats
        stats_thread = threading.Thread(target=self.display_stats, daemon=True)
        stats_thread.start()

        # Call the setup_replication() method
        self.db_handler.setup_replication()

        # Call the perform_backup() method
        self.db_handler.perform_backup()

        # Start the main tkinter event loop
        self.window.mainloop()

        # Set the stop event and wait for the stats thread to join
        self.stop_event.set()
        stats_thread.join()

    def display_stats(self):
        # Get the current CPU utilization percentage
        cpu_percent = psutil.cpu_percent(interval=None)
        # Get the current memory utilization percentage
        memory_percent = psutil.virtual_memory().percent

        # Get disk usage statistics
        disk_usage = psutil.disk_usage('/')
        disk_percent = disk_usage.percent

        # Get network statistics
        network_stats = psutil.net_io_counters()
        sent_bytes = network_stats.bytes_sent
        received_bytes = network_stats.bytes_recv

        # Print the CPU, memory, disk, and network utilization stats
        print(f"CPU Utilization: {cpu_percent}%")
        print(f"Memory Utilization: {memory_percent}%")
        print(f"Disk Usage: {disk_percent}%")
        print(f"Bytes Sent: {sent_bytes}")
        print(f"Bytes Received: {received_bytes}")

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

        self.audit_logger.info(f"User opened file: {self.file_path}")

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

            # Enable buttons for sending data to database, ML model, visualization and uploading to postgreSQL
            self.send_to_db_button['state'] = tk.NORMAL
            self.send_to_ml_button['state'] = tk.NORMAL
            self.visualize_button['state'] = tk.NORMAL
            self.upload_button['state'] = tk.NORMAL

            # this wont work as this is a concept idea
            self.vlan_config_button['state'] = tk.NORMAL
        except Exception as e:
            # Handle any errors and print error message
            print("Error:", e)

    def send_to_database(self):
        # Send data to database CRUD window
        if self.data is not None:
            # Open CRUD window for database interaction
            crud_window = CRUDWindow(self.window, self.data, self.db_handler, self.file_path)
            crud_window.mainloop()
        else:
            print("No file data loaded.")
            logger.info("No file data loaded.")

        self.audit_logger.info(f"User sent data to database")

    def send_to_ml(self):
        # Send data to ML model for evaluation
        if self.data is not None:
            # Load data into neural network and evaluate models
            self.neural_network.load_data(self.data)
            self.neural_network.evaluate_models()
        else:
            print("No file data loaded.")
            logger.info("No file data loaded.")

        self.audit_logger.info(f"User sent data to machine learning model")

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

        self.audit_logger.info(f"User clicked 'Visualize' button")

    def create_graph(self, graph_selection_window):
        # Create graph based on selected headers and graph type
        selected_headers = graph_selection_window.selected_headers
        graph_type = graph_selection_window.graph_type.get()

        if selected_headers:
            self.visualise_df = GraphTheory()
            self.visualise_df.data = self.data[selected_headers]

            # Analyze selected variables and provide suggestions
            suggestions = []
            """
            Reasearch into this was interesting which actually taught me some maths
            I tried to make this sound professional so that once again, if need be the user can understand better
            how to use the application or how to query for relationships between columns 
            """

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

    def upload_to_postgresql(self):
        if self.data is not None:
            try:
                # Establish a connection to the PostgreSQL database
                conn = psycopg2.connect("postgresql://neojoker26:password123@localhost:5432/dissertation")
                cur = conn.cursor()

                # Generate a unique table name based on the current timestamp
                file_name = os.path.basename(self.file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Remove invalid characters and replace them with underscores
                # the name can be changed in postgreSQL later on
                file_name = re.sub(r'[^a-zA-Z0-9]', '_', file_name)
                table_name = f"{file_name}_uploaded_{timestamp}"

                # Create a new table to store the CSV data with appropriate data types
                columns = []
                for col in self.data.columns:
                    if self.data[col].dtype == 'object':
                        columns.append(f"{col} TEXT")
                    else:
                        columns.append(f"{col} NUMERIC")
                columns_def = ', '.join(columns)
                create_table_query = f"CREATE TABLE {table_name} ({columns_def})"
                cur.execute(create_table_query)

                # Insert the data into the table
                insert_query = f"INSERT INTO {table_name} ({', '.join(self.data.columns)}) VALUES ({', '.join(['%s'] * len(self.data.columns))})"
                for _, row in self.data.iterrows():
                    cur.execute(insert_query, tuple(row))

                # Commit the transaction and show success message
                conn.commit()
                messagebox.showinfo("Success", f"Data uploaded to PostgreSQL successfully. Table name: {table_name}")
                logger.info(f"Data uploaded to PostgreSQL successfully. Table name: {table_name}")
            except psycopg2.Error as e:
                messagebox.showerror("Error", f"An error occurred while uploading data to PostgreSQL: {str(e)}")
                logger.error(f"An error occurred while uploading data to PostgreSQL: {str(e)}")
            finally:
                # Close the cursor and connection after upload, if they are open
                if cur:
                    cur.close()
                if conn:
                    conn.close()
        else:
            messagebox.showwarning("Warning", "No data available to upload.")
            logger.warning("No data available to upload.")

        self.audit_logger.info(f"User uploaded data to PostgreSQL")

    """
    This will not work unless needed, for example if the user were to use VLAN tagging on a network switch
    I've set it up so that the user could just change the dummy device metadata and adjust it for their device
    an error message will appear that shows ALL of the devices possible (both CLI and messagebox) so that the user knows
    which devices are compatible with VLAN tagging
    I have also set up a SSH command to connect to the "network switch" device
    I've also added a logger if the user does use this which is stored in "vlan_tagging.log" however this will most
    likely remain empty
    """

    def configure_vlan_tagging(self):
        # Netmiko configuration for VLAN tagging
        try:
            # Configure logger to write logs to a file
            file_handler = logging.FileHandler('vlan_tagging.log')
            file_handler.setLevel(logging.DEBUG)
            # Define device parameters for your network switch
            device = {
                'device_type': 'some_type_of_device_maybe_cisco',
                'host': 'switch_ip_address',
                'username': 'network_manager_username/sysadmin_username/whatever_role_username',
                'password': 'network_manager_password/sysadmin_password/whatever_role_password',
                'secret': 'network_manager_password/sysadmin_password/whatever_role_password'
            }

            #  SSH command to connect to the "network" switch
            # ssh_command = [
            #     'ssh',
            #     f"{device['username']}@{device['host']}",
            #
            #     # Disable strict host key checking
            #     '-o', 'StrictHostKeyChecking=no',
            #     # Disable known hosts file
            #     '-o', 'UserKnownHostsFile=/dev/null',
            #     # Enable password authentication
            #     '-o', 'PasswordAuthentication=yes',
            #     '-o', 'KexAlgorithms=+diffie-hellman-group1-sha1',
            # ]
            #
            # # Send commands to the SSH process
            # commands = [
            #     'enable',  # Enter privileged exec mode
            #     'configure terminal',  # Enter global configuration mode
            #     'vlan 10',  # Create VLAN with ID 10
            #     'name VLAN_10',  # Assign a name to the VLAN
            #     'interface Ethernet1/1',  # Enter interface configuration mode for a specific interface
            #     'switchport mode access',  # Set the interface to access mode
            #     'switchport access vlan 10',  # Assign the VLAN to the interface
            #     'no shutdown',  # Enable the interface
            #     'end',  # Exit from global configuration mode
            #     'write memory',  # Save the configuration
            #     'exit',  # Exit from the SSH session
            # ]

            # Connect to the network switch
            with ConnectHandler(**device) as net_connect:
                # Enter privileged exec mode
                net_connect.enable()

                # Example configuration for VLAN tagging
                # all of this is fake until actually put into a VLAN setup

                vlan_id = '10'
                interface = 'Ethernet1/1'
                vlan_name = 'VLAN_10'

                # Create VLAN
                create_vlan_command = f'vlan {vlan_id}; name {vlan_name}'
                output = net_connect.send_config_set(create_vlan_command)
                logger.info(f"Create VLAN command output: {output}")

                # Configure VLAN on the interface
                interface_config_commands = [
                    f'interface {interface}',
                    'switchport mode access',
                    f'switchport access vlan {vlan_id}',
                    'no shutdown'
                ]
                output = net_connect.send_config_set(interface_config_commands)
                logger.info(f"Interface configuration output: {output}")

                # Save the configuration
                save_command = 'write memory'
                output = net_connect.send_command(save_command)
                logger.info(f"Save configuration output: {output}")

                messagebox.showinfo("Success", "VLAN configuration completed successfully.")
                print(output)
        except Exception as e:
            # Handle any errors that occur during VLAN tagging configuration
            error_message = f"Error occurred during VLAN tagging configuration: {str(e)}"
            messagebox.showerror("Error", error_message)
            logger.error(error_message)


    def setup_network_bonding(self):
        # Configure network bonding for increased bandwidth and fault tolerance
        interfaces = netifaces.interfaces()
        bond_interface = "bond_example"

        # Create bond interface
        subprocess.run(["ip", "link", "add", bond_interface, "type", "bond"])

        # Add network interfaces to the bond
        for interface in interfaces:
            if interface.startswith("eth"):
                subprocess.run(["ip", "link", "set", interface, "master", bond_interface])

        # Configure bond mode and other bonding options
        subprocess.run(["ip", "link", "set", bond_interface, "type", "bond", "mode", "802.3ad"])

        # Assign IP address to the bond interface
        subprocess.run(["ip", "addr", "add", "192.168.0.100/x", "dev", bond_interface])

        # Bring up the bond interface
        subprocess.run(["ip", "link", "set", bond_interface, "up"])

        print("Network bonding configured successfully.")


if __name__ == "__main__":
    window = WindowMaker()
    window.main()

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
