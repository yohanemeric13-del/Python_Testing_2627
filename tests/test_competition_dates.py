import unittest

import server


class CompetitionDateTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        server.clubs = [{'name': 'Club connu', 'email': 'club@example.com', 'points': '10'}]
        server.competitions = [
            {
                'name': 'Compétition de 2026',
                'date': '2026-03-27 10:00:00',
                'numberOfPlaces': 10,
            },
            {
                'name': 'Compétition de 2027',
                'date': '2027-01-01 10:00:00',
                'numberOfPlaces': 10,
            },
            {
                'name': 'Compétition de 2025',
                'date': '2025-12-31 10:00:00',
                'numberOfPlaces': 10,
            },
            {
                'name': 'Date invalide',
                'date': 'demain',
                'numberOfPlaces': 10,
            },
        ]
        self.client = server.app.test_client()

    def tearDown(self):
        server.clubs = self.original_clubs
        server.competitions = self.original_competitions

    def login(self):
        return self.client.post('/showSummary', data={'email': 'club@example.com'})

    def test_summary_shows_competitions_from_2026_onward(self):
        response = self.login()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Compétition de 2026'.encode(), response.data)
        self.assertIn('Compétition de 2027'.encode(), response.data)
        self.assertNotIn('Compétition de 2025'.encode(), response.data)
        self.assertNotIn('Date invalide'.encode(), response.data)

    def test_competition_before_2026_cannot_be_opened_or_booked(self):
        self.login()
        booking_page = self.client.get('/book/Compétition%20de%202025/Club%20connu')
        purchase_response = self.client.post('/purchasePlaces', data={
            'competition': 'Compétition de 2025',
            'places': '1',
        }, follow_redirects=True)

        self.assertEqual(booking_page.status_code, 200)
        self.assertIn('antérieure à 2026'.encode(), booking_page.data)
        self.assertNotIn(b'name="places"', booking_page.data)
        self.assertEqual(purchase_response.status_code, 200)
        self.assertIn('antérieure à 2026'.encode(), purchase_response.data)
        self.assertEqual(server.clubs[0]['points'], '10')
        self.assertEqual(server.competitions[2]['numberOfPlaces'], 10)

    def test_competition_in_2026_can_be_opened_even_if_its_date_has_passed(self):
        self.login()
        response = self.client.get('/book/Compétition%20de%202026/Club%20connu')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="places"', response.data)

    def test_invalid_date_is_not_considered_upcoming(self):
        self.assertFalse(server.is_competition_in_supported_year(server.competitions[3]))


if __name__ == '__main__':
    unittest.main()
