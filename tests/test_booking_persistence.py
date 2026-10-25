import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import server


class BookingPersistenceTests(unittest.TestCase):
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
            'date': '2099-01-01 12:00:00',
            'numberOfPlaces': 10,
        }]
        server.CLUBS_FILE.write_text(json.dumps({'clubs': server.clubs}))
        server.COMPETITIONS_FILE.write_text(json.dumps({'competitions': server.competitions}))
        self.client = server.app.test_client()
        self.client.post('/showSummary', data={'email': 'club@example.com'})

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

    def test_booking_data_survives_reloading_from_json(self):
        first_response = self.post_booking(3)
        self.assertEqual(first_response.status_code, 200)

        server.clubs = server.loadClubs()
        server.competitions = server.loadCompetitions()

        self.assertEqual(server.clubs[0]['points'], '7')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 7)
        self.assertEqual(
            server.competitions[0]['bookedPlacesByClub']['Club connu'],
            3,
        )

        second_response = self.post_booking(1)

        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(server.loadClubs()[0]['points'], '6')
        self.assertEqual(server.loadCompetitions()[0]['numberOfPlaces'], 6)
        self.assertEqual(
            server.loadCompetitions()[0]['bookedPlacesByClub']['Club connu'],
            4,
        )


if __name__ == '__main__':
    unittest.main()
