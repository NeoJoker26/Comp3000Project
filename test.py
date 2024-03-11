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
            self.visualise_df.visualize_histogram('Weight')
            self.visualise_df.visualize_histogram('Sweetness')
            self.visualise_df.visualize_histogram('Softness')
            self.visualise_df.visualize_histogram('HarvestTime')
            self.visualise_df.visualize_histogram('Ripeness')
            self.visualise_df.visualize_histogram('Acidity')
            self.visualise_df.visualize_quality()
            self.visualise_df.visualize_weight_distribution('Size')
            self.visualise_df.visualize_pairplot()
            self.visualise_df.visualize_correlation_heatmap()
            self.visualise_df.visualize_box_plot('Weight')
            self.visualise_df.visualize_scatter_matrix()
        else:
            print("No file data loaded.")
