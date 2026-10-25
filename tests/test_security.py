import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import server


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        self.original_clubs_file = server.CLUBS_FILE
        self.original_competitions_file = server.COMPETITIONS_FILE
        self.temp_directory = TemporaryDirectory()
        server.CLUBS_FILE = Path(self.temp_directory.name) / 'clubs.json'
        server.COMPETITIONS_FILE = Path(self.temp_directory.name) / 'competitions.json'
        server.clubs = [
            {'name': 'Club connu', 'email': 'club@example.com', 'points': '10'},
            {'name': 'Autre club', 'email': 'autre@example.com', 'points': '10'},
        ]
        server.competitions = [{
            'name': 'Compétition connue',
            'date': '2099-01-01 12:00:00',
            'numberOfPlaces': 10,
        }]
        server.CLUBS_FILE.write_text(json.dumps({'clubs': server.clubs}))
        server.COMPETITIONS_FILE.write_text(json.dumps({'competitions': server.competitions}))
        self.client = server.app.test_client()

    def tearDown(self):
        server.clubs = self.original_clubs
        server.competitions = self.original_competitions
        server.CLUBS_FILE = self.original_clubs_file
        server.COMPETITIONS_FILE = self.original_competitions_file
        self.temp_directory.cleanup()

    def test_secret_key_comes_from_environment_and_is_not_hard_coded(self):
        with patch.dict(os.environ, {'FLASK_SECRET_KEY': 'test-only-secret'}):
            self.assertEqual(server.get_secret_key(), 'test-only-secret')
        self.assertNotEqual(server.app.config['SECRET_KEY'], 'something_special')

    def test_purchase_uses_authenticated_club_not_tampered_form_name(self):
        self.client.post('/showSummary', data={'email': 'club@example.com'})
        response = self.client.post('/purchasePlaces', data={
            'club': 'Autre club',
            'competition': 'Compétition connue',
            'places': '2',
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(server.clubs[0]['points'], '8')
        self.assertEqual(server.clubs[1]['points'], '10')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 8)

    def test_authenticated_user_cannot_tamper_booking_url_to_another_club(self):
        self.client.post('/showSummary', data={'email': 'club@example.com'})
        response = self.client.get('/book/Compétition%20connue/Autre%20club')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')


if __name__ == '__main__':
    unittest.main()
