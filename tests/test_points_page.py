import unittest

import server


class PublicPointsPageTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        server.clubs = [
            {'name': 'Club Alpha', 'email': 'alpha@example.com', 'points': '17'},
            {'name': 'Club Beta', 'email': 'beta@example.com', 'points': '9'},
        ]
        self.client = server.app.test_client()

    def tearDown(self):
        server.clubs = self.original_clubs

    def test_points_page_is_public_and_shows_every_club_balance(self):
        response = self.client.get('/points')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Club Alpha', response.data)
        self.assertIn(b'17', response.data)
        self.assertIn(b'Club Beta', response.data)
        self.assertIn(b'9', response.data)

    def test_home_page_links_to_public_points_page(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'href="/points"', response.data)


if __name__ == '__main__':
    unittest.main()
