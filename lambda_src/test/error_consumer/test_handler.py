from unittest import TestCase
from unittest.mock import patch, MagicMock

from lambda_src.error_consumer.handler import handle


class TestErrorConsumerHandler(TestCase):
    def test_handler_calls_services(self):
        EVENT = {"hello": "world"}

        with patch('lambda_src.error_consumer.handler.logger') as mock_logger, \
             patch('lambda_src.error_consumer.handler.read') as mock_read:
            mock_read.return_value= EVENT
            mock_logger_info = MagicMock()
            mock_logger.info = mock_logger_info
            handle(EVENT, None)
            mock_logger_info.assert_called_once_with("The following information has errored {0}".format(EVENT))