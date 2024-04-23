import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import pandas as pd
from main import WindowMaker, CRUDWindow, PredictionAlgorithm, GraphTheory
from database import DatabaseHandler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from models import Banana

"""
This is the CI/CD part of the code, "continous integration/ continous development"
I have 13 test cases just to be general, some wont pass on github due to github being a headless (not gui) environment, 
they all pass in a local env with all the files so it should all be good
the @patch decorator basically mocks the filedialog module from tkinter (as seen in windowmaker() ) and tries to open 
the button, it takes the "banana_quality" csv from the local "test" folder and tries with that
the rest of the code is self explanatory, the only one that might be confusing is the sqlite function
github cant really download and use postgres or oracle or aws and its not worth the hassle to set up a test case for 
postgres or oracle or aws here if i can spare some memory to test it out (just makes it more efficient)
everything should be self explanatory, any questions will be answered in the viva/dissertation
p.s. errors will show up here but that is nothing to worry about as the app is use pseudo data to test certain 
functionalities
"""


class Tests(unittest.TestCase):
    # Test opening a CSV file, wont work in a headless enviroment
    @patch('tkinter.filedialog.askopenfilename', return_value='banana_quality.csv')
    def test_open_csv_file(self, _):
        window = WindowMaker()
        window.open_file()
        self.assertIsNotNone(window.data)

    # Test pressing the open file button, once again, wont work in a headless env
    @patch('tkinter.filedialog.askopenfilename', return_value='banana_quality.csv')
    def test_press_open_file_button(self, _):
        window = WindowMaker()
        button = tk.Button(window.button_frame, text="Open File", command=window.open_file)
        button.invoke()
        self.assertIsNotNone(window.data)

    # Test visualizing histogram
    def test_visualize_histogram(self):
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        graph_theory = GraphTheory()
        graph_theory.data = data
        with patch('matplotlib.pyplot.show') as mock_show:
            graph_window = tk.Toplevel()
            graph_theory.visualize_histogram('Weight', graph_window)
            self.assertEqual(mock_show.call_count, 0)

    # Test visualizing line plot
    def test_visualize_line_plot(self):
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        graph_theory = GraphTheory()
        graph_theory.data = data
        with patch('matplotlib.pyplot.show') as mock_show:
            graph_window = tk.Toplevel()
            graph_theory.visualize_line_plot('x', 'y', graph_window)
            self.assertEqual(mock_show.call_count, 0)

    # Test visualizing scatter plot
    def test_visualize_scatter_plot(self):
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        graph_theory = GraphTheory()
        graph_theory.data = data
        with patch('matplotlib.pyplot.show') as mock_show:
            graph_window = tk.Toplevel()
            graph_theory.visualize_scatter_plot('x', 'y', graph_window)
            self.assertEqual(mock_show.call_count, 0)

    # Test visualizing box plot
    def test_visualize_box_plot(self):
        data = pd.DataFrame({'x': [1, 2, 3, 4, 5]})
        graph_theory = GraphTheory()
        graph_theory.data = data
        with patch('matplotlib.pyplot.show') as mock_show:
            graph_window = tk.Toplevel()
            graph_theory.visualize_box_plot('x', graph_window)
            self.assertEqual(mock_show.call_count, 0)

    # Test visualizing pair plot
    def test_visualize_pair_plot(self):
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        graph_theory = GraphTheory()
        graph_theory.data = data
        with patch('matplotlib.pyplot.show') as mock_show:
            graph_window = tk.Toplevel()
            graph_theory.visualize_pairplot(graph_window)
            self.assertEqual(mock_show.call_count, 0)

    # Test visualizing correlation heatmap
    def test_visualize_correlation_heatmap(self):
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        graph_theory = GraphTheory()
        graph_theory.data = data
        with patch('matplotlib.pyplot.show') as mock_show:
            graph_window = tk.Toplevel()
            graph_theory.visualize_correlation_heatmap(graph_window)
            self.assertEqual(mock_show.call_count, 0)

    # Set up an in-memory SQLite database
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    # Close the session after each test
    def tearDown(self):
        self.session.close()

    # Test adding a banana model to the database
    def test_banana_model(self):
        banana = Banana(size=50, weight=150.5, sweetness=3, softness=2, harvest_time=54, ripeness=4,
                        acidity=1, quality="good")

        self.session.add(banana)
        self.session.commit()

        retrieved_banana = self.session.query(Banana).filter_by(banana_id=1).first()

        self.assertEqual(retrieved_banana.size, 50)
        self.assertEqual(retrieved_banana.weight, 150.5)
        self.assertEqual(retrieved_banana.sweetness, 3)
        self.assertEqual(retrieved_banana.softness, 2)
        self.assertEqual(retrieved_banana.harvest_time, 54)
        self.assertEqual(retrieved_banana.ripeness, 4)
        self.assertEqual(retrieved_banana.acidity, 1)
        self.assertEqual(retrieved_banana.quality, "good")

    # Test creating an entry in the CRUD window
    def test_crud_window_create_entry(self):
        root = tk.Tk()
        data = pd.DataFrame()
        db_handler = DatabaseHandler("sqlite:///:memory:")
        file_path = "banana_quality.csv"
        crud_window = CRUDWindow(root, data, db_handler, file_path)

        crud_window.create_entry()
        self.assertIsNotNone(crud_window.create_form_frame)

        crud_window.destroy()

    # Test updating an entry in the CRUD window
    def test_crud_window_update_entry(self):
        root = tk.Tk()
        data = pd.DataFrame()
        db_handler = DatabaseHandler("sqlite:///:memory:")
        file_path = "banana_quality.csv"
        crud_window = CRUDWindow(root, data, db_handler, file_path)

        crud_window.update_entry()
        self.assertIsNotNone(crud_window.winfo_children()[1])

        crud_window.destroy()

    # Test deleting an entry in the CRUD window
    def test_crud_window_delete_entry(self):
        root = tk.Tk()
        data = pd.DataFrame()
        db_handler = DatabaseHandler("sqlite:///:memory:")
        file_path = "banana_quality.csv"
        crud_window = CRUDWindow(root, data, db_handler, file_path)

        crud_window.delete_entry()
        self.assertIsNotNone(crud_window.winfo_children()[1])

        crud_window.destroy()

    # Test visualizing data
    def test_visualize_data(self):
        window = WindowMaker()
        window.data = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        with patch('main.GraphSelectionWindow') as mock_graph_selection_window:
            window.visualize_data()
            mock_graph_selection_window.assert_called_once_with(window.window, ['A', 'B'])


if __name__ == '__main__':
    unittest.main()
