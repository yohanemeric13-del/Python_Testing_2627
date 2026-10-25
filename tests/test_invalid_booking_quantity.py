import unittest

import server


class InvalidBookingQuantityTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        server.clubs = [{'name': 'Club connu', 'email': 'club@example.com', 'points': 10}]
        server.competitions = [{
            'name': 'Compétition connue',
            'date': '2099-01-01',
            'numberOfPlaces': 10,
        }]
        self.client = server.app.test_client()

    def tearDown(self):
        server.clubs = self.original_clubs
        server.competitions = self.original_competitions

    def post_booking(self, places=None, include_places=True):
        data = {
            'club': 'Club connu',
            'competition': 'Compétition connue',
        }
        if include_places:
            data['places'] = places
        return self.client.post('/purchasePlaces', data=data)

    def assert_invalid_quantity_is_rejected(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertIn('nombre entier de places valide'.encode(), response.data)
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 10)

    def test_missing_quantity_shows_error_without_changing_stock(self):
        response = self.post_booking(include_places=False)

        self.assert_invalid_quantity_is_rejected(response)

    def test_non_integer_quantity_shows_error_without_changing_stock(self):
        response = self.post_booking(places='beaucoup')

        self.assert_invalid_quantity_is_rejected(response)


if __name__ == '__main__':
    unittest.main()
