# Comp3000Project
# Banana Quality CRUD Application

## Features (Concept)

- **Create:** Users can add new entries for banana quality attributes such as size, weight, sweetness, softness, harvest time, ripeness, acidity, and overall quality.
- **Read:** Users can view existing banana quality entries by entering the ID of the banana.
- **Update:** Users can update an existing banana quality entry by entering the banana ID.
- **Delete:** Users can delete an existing banana quality entry by entering the banana ID.
- **Visualize:** Users can visualize the data stored in the database using various graph types, including histograms, line plots, scatter plots, box plots, pair plots, and correlation heatmaps. The application provides suggestions for appropriate graph types based on the selected variables.
- **Machine Learning:** The application utilizes the MLPRegressor model from Scikit-learn to predict banana quality based on the provided attributes. It allows users to evaluate the model's performance and visualize the actual vs. predicted values.
- **Data Validation:** The application includes data validation checks to ensure that the entered data is in the expected format and contains the required columns. It handles invalid or missing data gracefully and provides informative error messages to guide users.
- **Logging:** The application incorporates logging functionality to track important events, errors, and warnings during runtime. Logs are stored for debugging and monitoring purposes.
- **Colorblind Mode:** The application offers a colorblind mode to enhance accessibility for users with color vision deficiencies. Users can select from different colorblind profiles to adjust the color scheme of the user interface.

## Dependencies

- Python 3.9
- Tkinter
- SQLAlchemy
- PostgreSQL
- Psycopg2
- Scikit-learn (for neural network functionality)
- Seaborn
- Matplotlib
- Pandas
- Chardet

**Installation**
- Clone the repository: git clone https://github.com/NeoJoker26/Comp3000Project.git
- Install the required dependencies: pip install -r requirements.txt
- Set up the PostgreSQL database and update the database connection string in the database.py file.
- Run the application: python main.py

**Usage**
Launch the application by running python main.py.
Use the "Open File" button to select a CSV file containing banana quality data.
The loaded data will be displayed in the main window. You can scroll horizontally and vertically to view the entire dataset.
Use the "Send Through Database" button to open the CRUD Operations window, where you can perform Create, Read, Update, and Delete operations on banana quality entries.
Use the "Send Through Machine Learning" button to evaluate the MLPRegressor model.
Use the "Visualize" button to open the Graph Selection window, where you can select the desired variables and graph type to visualize the data (Suggestions provided).
