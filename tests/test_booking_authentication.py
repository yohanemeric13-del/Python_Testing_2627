import unittest

import server


class BookingAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        server.clubs = [
            {'name': 'Club connu', 'email': 'club@example.com', 'points': '10'},
            {'name': 'Autre club', 'email': 'autre@example.com', 'points': '10'},
        ]
        server.competitions = [{
            'name': 'Compétition connue',
            'date': '2099-01-01 12:00:00',
            'numberOfPlaces': 10,
        }]
        self.client = server.app.test_client()

    def tearDown(self):
        server.clubs = self.original_clubs
        server.competitions = self.original_competitions

    def login_as_known_club(self):
        return self.client.post('/showSummary', data={'email': 'club@example.com'})

    def test_booking_page_redirects_when_not_authenticated(self):
        response = self.client.get('/book/Compétition%20connue/Club%20connu')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')

    def test_purchase_redirects_when_not_authenticated_without_changing_data(self):
        response = self.client.post('/purchasePlaces', data={
            'club': 'Club connu',
            'competition': 'Compétition connue',
            'places': '2',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')
        self.assertEqual(server.clubs[0]['points'], '10')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 10)

    def test_login_allows_booking_for_the_authenticated_club(self):
        login_response = self.login_as_known_club()
        response = self.client.get('/book/Compétition%20connue/Club%20connu')

        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Compétition connue'.encode(), response.data)

    def test_authenticated_club_cannot_open_another_clubs_booking(self):
        self.login_as_known_club()
        response = self.client.get('/book/Compétition%20connue/Autre%20club')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')

    def test_logout_clears_session_and_blocks_booking(self):
        self.login_as_known_club()
        logout_response = self.client.get('/logout')
        booking_response = self.client.get('/book/Compétition%20connue/Club%20connu')

        self.assertEqual(logout_response.status_code, 302)
        self.assertEqual(booking_response.status_code, 302)
        self.assertEqual(booking_response.headers['Location'], '/')
        with self.client.session_transaction() as session:
            self.assertNotIn('club_email', session)

    def test_full_session_lifecycle_protects_booking_routes(self):
        before_login = self.client.get('/book/Compétition%20connue/Club%20connu')
        login_response = self.login_as_known_club()
        during_login = self.client.get('/book/Compétition%20connue/Club%20connu')
        logout_response = self.client.get('/logout')
        after_logout = self.client.post('/purchasePlaces', data={
            'club': 'Club connu',
            'competition': 'Compétition connue',
            'places': '1',
        })

        self.assertEqual(before_login.status_code, 302)
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(during_login.status_code, 200)
        self.assertEqual(logout_response.status_code, 302)
        self.assertEqual(after_logout.status_code, 302)
        self.assertEqual(server.clubs[0]['points'], '10')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 10)


if __name__ == '__main__':
    unittest.main()
