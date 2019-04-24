import os
from unittest import TestCase

from lambda_src.common_deps.model.exception import ScrappingError
from lambda_src.scrapper.scrapper import extract_data

resources_path='{0}/mock_resources'.format(os.path.dirname(os.path.realpath(__file__)))

class TestScrapper(TestCase):

    def test_scrapper_known_format_returns_expected_object(self):
        type_1_html = read_file('{0}/type1.html'.format(resources_path))
        result =extract_data(type_1_html)
        self.assertEqual(1,len(result))
        self.assertEqual('tt0292215',result[0]['id'])
        self.assertEqual('Jüri Rumm',result[0]['primaryTitle'])
        self.assertEqual('Jüri Rumm',result[0]['originalTitle'])
        self.assertEqual('False',result[0]['isAdult'])
        self.assertEqual('1994',result[0]['startYear'])
        self.assertEqual('90',result[0]['runtimeMinutes'])
        self.assertEqual('Adventure,Drama',result[0]['genres'])

    def test_scrapper_unknown_format_raises_ScrappingError(self):
        with self.assertRaises(ScrappingError):
            type_2_html = read_file('{0}/type2.html'.format(resources_path))
            extract_data(type_2_html)


def read_file(path):
    with open(path) as f:
        content = f.read()
    return content