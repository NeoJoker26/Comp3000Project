import unittest
from unittest.mock import patch
from tkinter import filedialog
from main import WindowMaker


class TestOpenFile(unittest.TestCase):
    @patch('tkinter.filedialog.askopenfilename', return_value='test_data.csv')
    def test_open_csv_file(self, _):
        window = WindowMaker()
        window.open_file()
        self.assertIsNotNone(window.data)

    @patch('tkinter.filedialog.askopenfilename', return_value='test_data.xlsx')
    def test_open_excel_file(self, _):
        window = WindowMaker()
        window.open_file()
        self.assertIsNotNone(window.data)


if __name__ == '__main__':
    unittest.main()
