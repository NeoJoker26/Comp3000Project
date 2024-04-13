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


class WindowMakerTest(unittest.TestCase):
    @patch('tkinter.filedialog.askopenfilename', return_value='banana_quality.csv')
    def test_open_csv_file(self, _):
        window = WindowMaker()
        window.open_file()
        self.assertIsNotNone(window.data)

    @patch('tkinter.filedialog.askopenfilename', return_value='banana_quality.csv')
    def test_press_open_file_button(self, _):
        window = WindowMaker()
        button = tk.Button(window.button_frame, text="Open File", command=window.open_file)
        button.invoke()
        self.assertIsNotNone(window.data)

    @patch('tkinter.filedialog.askopenfilename', return_value='banana_quality.csv')
    @patch('main.PredictionAlgorithm.load_data', return_value=None)
    @patch('main.PredictionAlgorithm.evaluate_models', return_value=None)
    def test_press_send_to_ml_button(self, _, __, ___):
        window = WindowMaker()
        window.open_file()
        button = tk.Button(window.button_frame, text="Send Through Machine Learning", command=window.send_to_ml)
        button.invoke()
        self.assertEqual(window.send_to_ml_button['state'], tk.NORMAL)

    def test_visualize_histogram(self):
        data = pd.DataFrame({'Weight': [1, 2, 3, 4, 5]})
        graph_theory = GraphTheory(data)
        with patch('matplotlib.pyplot.show') as mock_show:
            graph_theory.visualize_histogram('Weight')
            self.assertEqual(mock_show.call_count, 1)

    def test_visualize_line_plot(self):
        data = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        graph_theory = GraphTheory(data)
        with patch('matplotlib.pyplot.show') as mock_show:
            graph_theory.visualize_line_plot('x', 'y')
            self.assertEqual(mock_show.call_count, 1)

    def setUp(self):
        # Create an in-memory SQLite database
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def tearDown(self):
        self.session.close()

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


if __name__ == '__main__':
    unittest.main()
