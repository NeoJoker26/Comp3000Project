import timeit
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import pandas as pd


columns = []

"""
This is a test file for seeing which machine learning algorithm would be faster, the regressor worked fastest for the 
excel file provided which was my original testing file but i also wanted to test with csv files which became a priority
"""
def open_file():
    try:
        file = pd.read_excel('housing_price_dataset.xlsx', index_col=0)
        process_file(file)
    except FileNotFoundError:
        print("File missing, maybe put it in the directory")
        return None
    except Exception as e:
        print(f"There was an error: {e}")
        return None


def process_file(file):
    for col in file:
        try:
            file[col] = pd.to_numeric(file[col])
            columns.append(col)
        except ValueError:
            file = file.drop(col, axis=1)

    scaler = MinMaxScaler()
    file[columns] = scaler.fit_transform(file[columns])
    X = file[columns]
    y = file['Price']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    models = [
        RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
        MLPRegressor(hidden_layer_sizes=(50, 25), max_iter=1000, activation='relu', random_state=42),
        SVR(kernel='rbf', C=100, gamma=0.1),
    ]

    for model in models:
        start_time = timeit.default_timer()  # Record start time
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        end_time = timeit.default_timer()  # Record end time
        elapsed_time = end_time - start_time  # Calculate elapsed time

        print(f"Model: {model.__class__.__name__}")
        print(f"Elapsed Time: {elapsed_time} seconds")


open_file()
