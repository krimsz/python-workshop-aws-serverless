from unittest import TestCase
from unittest.mock import patch

from lambda_src.common_deps.model.exception import ScrappingError
from lambda_src.scrapper.handler import handle

get_page_binary_error_data = b'SomeBinaryData'
EXPECTED_ERROR_CONTENT = [{"content": get_page_binary_error_data.decode('utf-8'), "error_message": ''}]

MOVIES = [
    {"id": "tt5947424", "primaryTitle": "Turnpike Gypsies", "originalTitle": "Turnpike Gypsies", "isAdult": "False",
     "startYear": "N/A", "runtimeMinutes": "N/A", "genres": "Comedy,Drama"}]


class TestScrapperHandler(TestCase):

    def test_handler_write_data_stream(self):
        with patch('lambda_src.scrapper.handler.extract_data') as mock_extract_data, \
          patch('lambda_src.scrapper.handler.get_page'),\
          patch('lambda_src.scrapper.handler.write') as mock_write:
            mock_extract_data.return_value=MOVIES
            response = handle({}, None)
            mock_write.assert_called_once_with(MOVIES,'DUMMY_DATA_STREAM')
            self.assertDictEqual({},response['headers'])
            self.assertEqual('{}',response['body'])
            self.assertEqual(200,response['statusCode'])

    def test_handler_write_error_stream(self):
        with patch('lambda_src.scrapper.handler.extract_data') as mock_extract_data, \
          patch('lambda_src.scrapper.handler.get_page') as mock_get_page,\
          patch('lambda_src.scrapper.handler.write') as mock_write:
            mock_extract_data.side_effect=raise_ScrappingError
            mock_get_page.return_value= get_page_binary_error_data
            response = handle({}, None)
            mock_write.assert_called_once_with(EXPECTED_ERROR_CONTENT,
                'DUMMY_ERROR_STREAM')
            self.assertDictEqual({}, response['headers'])
            self.assertEqual('{}', response['body'])
            self.assertEqual(200, response['statusCode'])

def raise_ScrappingError(a):
    raise ScrappingError()