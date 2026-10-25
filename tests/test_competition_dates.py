import unittest

import server


class CompetitionDateTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        server.clubs = [{'name': 'Club connu', 'email': 'club@example.com', 'points': '10'}]
        server.competitions = [
            {
                'name': 'Compétition future',
                'date': '2099-12-31 10:00:00',
                'numberOfPlaces': 10,
            },
            {
                'name': 'Compétition passée',
                'date': '2000-01-01 10:00:00',
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

    def test_summary_shows_future_competitions_only(self):
        response = self.login()

        self.assertEqual(response.status_code, 200)
        self.assertIn('Compétition future'.encode(), response.data)
        self.assertNotIn('Compétition passée'.encode(), response.data)
        self.assertNotIn('Date invalide'.encode(), response.data)

    def test_past_competition_cannot_be_opened_or_booked(self):
        self.login()
        booking_page = self.client.get('/book/Compétition%20passée/Club%20connu')
        purchase_response = self.client.post('/purchasePlaces', data={
            'competition': 'Compétition passée',
            'places': '1',
        }, follow_redirects=True)

        self.assertEqual(booking_page.status_code, 200)
        self.assertIn('Cette compétition est passée'.encode(), booking_page.data)
        self.assertNotIn(b'name="places"', booking_page.data)
        self.assertEqual(purchase_response.status_code, 200)
        self.assertIn('Cette compétition est passée'.encode(), purchase_response.data)
        self.assertEqual(server.clubs[0]['points'], '10')
        self.assertEqual(server.competitions[1]['numberOfPlaces'], 10)

    def test_future_competition_can_be_opened(self):
        self.login()
        response = self.client.get('/book/Compétition%20future/Club%20connu')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="places"', response.data)

    def test_invalid_date_is_not_considered_upcoming(self):
        self.assertFalse(server.is_competition_upcoming(server.competitions[2]))


if __name__ == '__main__':
    unittest.main()
