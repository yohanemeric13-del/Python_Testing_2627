import unittest

import server


class BookUnknownClubTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        server.clubs = [{'name': 'Club connu', 'email': 'club@example.com', 'points': 10}]
        server.competitions = [{'name': 'Competition connue', 'date': '2099-01-01', 'numberOfPlaces': 10}]
        self.client = server.app.test_client()

    def tearDown(self):
        server.clubs = self.original_clubs
        server.competitions = self.original_competitions

    def test_unknown_club_shows_message_instead_of_crashing(self):
        response = self.client.get(
            '/book/Competition%20connue/Club-inconnu',
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Club inconnu', response.data)
        self.assertIn('Veuillez vérifier le lien de réservation'.encode(), response.data)


if __name__ == '__main__':
    unittest.main()
