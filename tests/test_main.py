import unittest
from main import WindowMaker
from database import DatabaseHandler
from models import Banana


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

    def test_parse_csv_invalid_file(self):
        self.window_maker.file_path = "tests/nonexistent_file.csv"
        with self.assertRaises(FileNotFoundError):
            self.window_maker.parse_csv()

    def test_create_banana_invalid_quality(self):
        with self.assertRaises(ValueError):
            self.db_handler.create_banana(
                size=5.0,
                weight=100.0,
                sweetness=4.5,
                softness=3.7,
                harvest_time=1.2,
                ripeness=0.8,
                acidity=2.1,
                quality="Average"
            )

    def test_read_nonexistent_banana(self):
        nonexistent_banana_id = 9999999
        banana = self.db_handler.read_banana(nonexistent_banana_id)
        self.assertIsNone(banana)

    def test_update_banana(self):
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
        updated_banana = Banana(
            size=6.0,
            weight=110.0,
            sweetness=4.7,
            softness=3.8,
            harvest_time=1.5,
            ripeness=0.9,
            acidity=2.2,
            quality="Excellent"
        )
        self.assertTrue(self.db_handler.update_banana(banana_id, updated_banana))
        retrieved_banana = self.db_handler.read_banana(banana_id)
        self.assertEqual(retrieved_banana.quality, "Excellent")

    def test_delete_banana(self):
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
        self.assertTrue(self.db_handler.delete_banana(banana_id))
        self.assertIsNone(self.db_handler.read_banana(banana_id))


if __name__ == '__main__':
    unittest.main()
