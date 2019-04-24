from unittest import TestCase
from unittest.mock import patch

from lambda_src.insert_to_db_consumer.handler import handle

MOVIES = [{"id": "tt5947424", "primaryTitle": "Turnpike Gypsies", "originalTitle": "Turnpike Gypsies", "isAdult": "False", "startYear": "N/A", "runtimeMinutes": "N/A", "genres": "Comedy,Drama"}]

class TestInsertToDBConsumerHandler(TestCase):
    def test_handler_calls_dynamo(self):

        with patch('lambda_src.insert_to_db_consumer.handler.logger') as mock_logger, \
            patch('lambda_src.insert_to_db_consumer.handler.read') as mock_read, \
            patch('lambda_src.insert_to_db_consumer.handler.DynamoMovieModel') as mock_dynamo:
            mock_read.return_value= MOVIES
            handle({}, None)
            mock_read.assert_called_once()
            mock_dynamo.assert_called_once()
