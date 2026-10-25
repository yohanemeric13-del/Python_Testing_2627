import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import server


class BookingPointsBalanceTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        self.original_clubs_file = server.CLUBS_FILE
        self.original_competitions_file = server.COMPETITIONS_FILE
        self.temp_directory = TemporaryDirectory()
        server.CLUBS_FILE = Path(self.temp_directory.name) / 'clubs.json'
        server.COMPETITIONS_FILE = Path(self.temp_directory.name) / 'competitions.json'
        server.clubs = [{'name': 'Club connu', 'email': 'club@example.com', 'points': '10'}]
        server.competitions = [{
            'name': 'Compétition connue',
            'date': '2099-01-01',
            'numberOfPlaces': 10,
        }]
        self.client = server.app.test_client()

    def tearDown(self):
        server.clubs = self.original_clubs
        server.competitions = self.original_competitions
        server.CLUBS_FILE = self.original_clubs_file
        server.COMPETITIONS_FILE = self.original_competitions_file
        self.temp_directory.cleanup()

    def post_booking(self, places):
        return self.client.post('/purchasePlaces', data={
            'club': 'Club connu',
            'competition': 'Compétition connue',
            'places': str(places),
        })

    def test_successful_booking_deducts_points_and_persists_changes(self):
        response = self.post_booking(3)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(server.clubs[0]['points'], '7')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 7)
        self.assertEqual(server.loadClubs()[0]['points'], '7')
        self.assertEqual(server.loadCompetitions()[0]['numberOfPlaces'], 7)

    def test_booking_without_enough_points_is_rejected_without_changes(self):
        server.clubs[0]['points'] = '2'

        response = self.post_booking(3)

        self.assertEqual(response.status_code, 200)
        self.assertIn('pas de suffisamment de points'.encode(), response.data)
        self.assertEqual(server.clubs[0]['points'], '2')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 10)


if __name__ == '__main__':
    unittest.main()
