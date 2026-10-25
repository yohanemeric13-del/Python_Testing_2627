import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import server


class ClubBookingLimitTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        self.original_clubs_file = server.CLUBS_FILE
        self.original_competitions_file = server.COMPETITIONS_FILE
        self.temp_directory = TemporaryDirectory()
        server.CLUBS_FILE = Path(self.temp_directory.name) / 'clubs.json'
        server.COMPETITIONS_FILE = Path(self.temp_directory.name) / 'competitions.json'
        server.clubs = [{'name': 'Club connu', 'email': 'club@example.com', 'points': '20'}]
        server.competitions = [{
            'name': 'Compétition connue',
            'date': '2099-01-01',
            'numberOfPlaces': 20,
        }]
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

    def test_rejects_more_than_12_places_in_one_booking(self):
        response = self.post_booking(13)

        self.assertEqual(response.status_code, 200)
        self.assertIn('plus de 12 places'.encode(), response.data)
        self.assertEqual(server.clubs[0]['points'], '20')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 20)
        self.assertNotIn('bookedPlacesByClub', server.competitions[0])

    def test_rejects_bookings_that_cumulatively_exceed_12(self):
        server.competitions[0]['bookedPlacesByClub'] = {'Club connu': 10}

        response = self.post_booking(3)

        self.assertEqual(response.status_code, 200)
        self.assertIn('plus de 12 places'.encode(), response.data)
        self.assertEqual(server.clubs[0]['points'], '20')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 20)
        self.assertEqual(server.competitions[0]['bookedPlacesByClub']['Club connu'], 10)

    def test_accepts_exactly_12_and_persists_the_booking_count(self):
        response = self.post_booking(12)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Réservation confirmée : 12 places.'.encode(), response.data)
        self.assertEqual(server.clubs[0]['points'], '8')
        self.assertEqual(server.competitions[0]['numberOfPlaces'], 8)
        persisted_competition = server.loadCompetitions()[0]
        self.assertEqual(persisted_competition['bookedPlacesByClub']['Club connu'], 12)

    def test_limit_is_tracked_separately_for_each_club(self):
        server.clubs.append({
            'name': 'Autre club',
            'email': 'autre@example.com',
            'points': '20',
        })
        self.post_booking(12)
        self.client.post('/showSummary', data={'email': 'autre@example.com'})

        response = self.client.post('/purchasePlaces', data={
            'club': 'Autre club',
            'competition': 'Compétition connue',
            'places': '1',
        })

        self.assertEqual(response.status_code, 200)
        bookings = server.competitions[0]['bookedPlacesByClub']
        self.assertEqual(bookings['Club connu'], 12)
        self.assertEqual(bookings['Autre club'], 1)


if __name__ == '__main__':
    unittest.main()
