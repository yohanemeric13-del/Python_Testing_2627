import unittest
from html.parser import HTMLParser

import server


class FormAssociationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.label_targets = []
        self.input_ids = set()
        self.inputs_by_id = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'label' and attributes.get('for'):
            self.label_targets.append(attributes['for'])
        if tag == 'input' and attributes.get('id'):
            self.input_ids.add(attributes['id'])
            self.inputs_by_id[attributes['id']] = attributes


class FormLabelTests(unittest.TestCase):
    def setUp(self):
        self.original_clubs = server.clubs
        self.original_competitions = server.competitions
        server.clubs = [{
            'name': 'Simply Lift',
            'email': 'john@simplylift.co',
            'points': '7',
        }]
        server.competitions = [{
            'name': 'Spring Festival',
            'date': '2099-03-27 10:00:00',
            'numberOfPlaces': 20,
            'bookedPlacesByClub': {'Simply Lift': 3},
        }]
        self.client = server.app.test_client()

    def tearDown(self):
        server.clubs = self.original_clubs
        server.competitions = self.original_competitions

    def assert_labels_target_inputs(self, html):
        parser = FormAssociationParser()
        parser.feed(html.decode())
        self.assertTrue(parser.label_targets)
        for target in parser.label_targets:
            self.assertIn(target, parser.input_ids)

    def test_email_label_targets_email_input(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assert_labels_target_inputs(response.data)
        parser = FormAssociationParser()
        parser.feed(response.data.decode())
        email_input = parser.inputs_by_id['email']
        self.assertIn('required', email_input)
        self.assertEqual(email_input.get('type'), 'email')

    def test_places_label_targets_places_input(self):
        self.client.post('/showSummary', data={'email': 'john@simplylift.co'})
        response = self.client.get('/book/Spring%20Festival/Simply%20Lift')

        self.assertEqual(response.status_code, 200)
        self.assert_labels_target_inputs(response.data)
        parser = FormAssociationParser()
        parser.feed(response.data.decode())
        places_input = parser.inputs_by_id['places']
        self.assertIn('required', places_input)
        self.assertEqual(places_input.get('min'), '1')
        self.assertEqual(places_input.get('max'), '7')
        self.assertEqual(places_input.get('step'), '1')

    def test_places_maximum_uses_stock_and_club_booking_limit(self):
        self.client.post('/showSummary', data={'email': 'john@simplylift.co'})
        server.clubs[0]['points'] = '20'
        server.competitions[0]['numberOfPlaces'] = 4
        response = self.client.get('/book/Spring%20Festival/Simply%20Lift')
        parser = FormAssociationParser()
        parser.feed(response.data.decode())
        self.assertEqual(parser.inputs_by_id['places'].get('max'), '4')

        server.competitions[0]['numberOfPlaces'] = 20
        server.competitions[0]['bookedPlacesByClub']['Simply Lift'] = 11
        response = self.client.get('/book/Spring%20Festival/Simply%20Lift')
        parser = FormAssociationParser()
        parser.feed(response.data.decode())
        self.assertEqual(parser.inputs_by_id['places'].get('max'), '1')


if __name__ == '__main__':
    unittest.main()
