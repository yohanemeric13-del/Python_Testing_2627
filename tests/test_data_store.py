import json
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

import data_store


class DataStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = TemporaryDirectory()
        self.clubs_file = Path(self.temp_directory.name) / 'clubs.json'
        self.competitions_file = Path(self.temp_directory.name) / 'competitions.json'

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_clubs_can_be_saved_and_loaded_through_data_store(self):
        clubs = [{'name': 'Club Étoile', 'email': 'etoile@example.com', 'points': '12'}]

        data_store.save_clubs(self.clubs_file, clubs)

        self.assertEqual(data_store.load_clubs(self.clubs_file), clubs)
        self.assertEqual(json.loads(self.clubs_file.read_text(encoding='utf-8'))['clubs'], clubs)

    def test_competitions_can_be_saved_and_loaded_through_data_store(self):
        competitions = [{
            'name': 'Compétition de test',
            'date': '2027-06-01 12:00:00',
            'numberOfPlaces': 8,
        }]

        data_store.save_competitions(self.competitions_file, competitions)

        self.assertEqual(data_store.load_competitions(self.competitions_file), competitions)
        self.assertEqual(
            json.loads(self.competitions_file.read_text(encoding='utf-8'))['competitions'],
            competitions,
        )


if __name__ == '__main__':
    unittest.main()
