import unittest
from html.parser import HTMLParser

import server


class FormAssociationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.label_targets = []
        self.input_ids = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'label' and attributes.get('for'):
            self.label_targets.append(attributes['for'])
        if tag == 'input' and attributes.get('id'):
            self.input_ids.add(attributes['id'])


class FormLabelTests(unittest.TestCase):
    def setUp(self):
        self.client = server.app.test_client()

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

    def test_places_label_targets_places_input(self):
        self.client.post('/showSummary', data={'email': 'john@simplylift.co'})
        response = self.client.get('/book/Spring%20Festival/Simply%20Lift')

        self.assertEqual(response.status_code, 200)
        self.assert_labels_target_inputs(response.data)


if __name__ == '__main__':
    unittest.main()
