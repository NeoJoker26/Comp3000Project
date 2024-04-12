import unittest
from unittest.mock import patch, MagicMock
import tkinter as tk
import pandas as pd
from main import WindowMaker, CRUDWindow, PredictionAlgorithm, GraphTheory


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
        button.invoke()  # Simulate button press
        self.assertIsNotNone(window.data)

    @patch('tkinter.filedialog.askopenfilename', return_value='banana_quality.csv')
    @patch('main.PredictionAlgorithm.load_data', return_value=None)
    @patch('main.PredictionAlgorithm.evaluate_models', return_value=None)
    def test_press_send_to_ml_button(self, _, __, ___):
        window = WindowMaker()
        window.open_file()
        button = tk.Button(window.button_frame, text="Send Through Machine Learning", command=window.send_to_ml)
        button.invoke()  # Simulate button press
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


if __name__ == '__main__':
    unittest.main()
