from os.path import abspath, dirname, join

project_root = abspath(join(dirname(__file__), '..'))

import sys

sys.path.append(project_root)

from main import WindowMaker
from database import DatabaseHandler
import unittest


class TestWindowMaker(unittest.TestCase):
    def setUp(self):
        self.window_maker = WindowMaker()
        self.db_handler = DatabaseHandler("postgresql://neojoker26:password123@localhost:5432/dissertation")

    def test_open_file(self):
        self.window_maker.file_path = "tests/test_data.csv"
        self.window_maker.parse_csv()
        self.assertIsNotNone(self.window_maker.data)

    def test_create_banana(self):
        banana_id = self.db_handler.create_banana(
            size=5.0,
            weight=100.0,
            sweetness=4.5,
            softness=3.7,
            harvest_time=1.2,
            ripeness=0.8,
            acidity=2.1,
            quality="Good"
        )
        self.assertIsNotNone(banana_id)

    def test_read_banana(self):
        banana_id = self.db_handler.create_banana(
            size=5.0,
            weight=100.0,
            sweetness=4.5,
            softness=3.7,
            harvest_time=1.2,
            ripeness=0.8,
            acidity=2.1,
            quality="Good"
        )
        banana = self.db_handler.read_banana(banana_id)
        self.assertIsNotNone(banana)
        self.assertEqual(banana.size, 5.0)


if __name__ == '__main__':
    unittest.main()
