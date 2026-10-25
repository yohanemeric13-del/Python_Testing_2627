import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import server


class InputValidationTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        self.original_clubs_file = server.CLUBS_FILE
        self.original_competitions_file = server.COMPETITIONS_FILE
        self.temp_directory = TemporaryDirectory()
        server.CLUBS_FILE = Path(self.temp_directory.name) / 'clubs.json'
        server.COMPETITIONS_FILE = Path(self.temp_directory.name) / 'competitions.json'
        server.clubs = [{'name': 'Club connu', 'email': 'club@example.com', 'points': '10'}]
        server.competitions = [
            {
                'name': 'Compétition ouverte',
                'date': '2099-01-01 12:00:00',
                'numberOfPlaces': 10,
            },
            {
                'name': 'Compétition complète',
                'date': '2099-01-02 12:00:00',
                'numberOfPlaces': 0,
            },
        ]
        self.client = server.app.test_client()

    def tearDown(self):
        server.clubs = self.original_clubs
        server.competitions = self.original_competitions
        server.CLUBS_FILE = self.original_clubs_file
        server.COMPETITIONS_FILE = self.original_competitions_file
        self.temp_directory.cleanup()

    def login(self):
        return self.client.post('/showSummary', data={'email': 'club@example.com'})

    def test_missing_or_unknown_email_returns_message_instead_of_crashing(self):
        for data in ({}, {'email': 'inconnu@example.com'}):
            with self.subTest(data=data):
                response = self.client.post('/showSummary', data=data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn('Adresse e-mail inconnue'.encode(), response.data)

    def test_unknown_competition_in_booking_url_returns_message(self):
        self.login()
        response = self.client.get(
            '/book/Compétition%20inconnue/Club%20connu',
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('Compétition inconnue'.encode(), response.data)

    def test_purchase_with_missing_or_unknown_competition_returns_message(self):
        self.login()
        response = self.client.post('/purchasePlaces', data={'places': '1'}, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Compétition absente ou inconnue'.encode(), response.data)
        self.assertEqual(server.clubs[0]['points'], '10')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 10)

    def test_purchase_rejects_a_full_competition_without_changing_data(self):
        self.login()
        response = self.client.post('/purchasePlaces', data={
            'competition': 'Compétition complète',
            'places': '1',
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Cette compétition est complète'.encode(), response.data)
        self.assertEqual(server.clubs[0]['points'], '10')
        self.assertEqual(server.competitions[1]['numberOfPlaces'], 0)

    def test_booking_page_rejects_a_full_competition(self):
        self.login()
        response = self.client.get('/book/Compétition%20complète/Club%20connu')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Cette compétition est complète'.encode(), response.data)
        self.assertNotIn(b'name="places"', response.data)


if __name__ == '__main__':
    unittest.main()
