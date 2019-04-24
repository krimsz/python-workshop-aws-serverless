import json
from json import JSONDecodeError
from unittest import TestCase
from unittest.mock import patch, MagicMock
from lambda_src.common_deps.service.kinesis import write, read, MalformedRecordError

TARGET_STREAM = 'TEST-STREAM'


class TestKinesis(TestCase):
    def setUp(self):
        self.env = patch.dict('os.environ', {'STREAM_NAME': 'SOME-KINESIS'})
    def test_read_correct_entry(self):
        KINESIS_EVENT = {'Records':
            [
                {
                    'kinesis':
                        {
                            'data': 'eyJpZCI6ICJ0dDU5NDc0MjQiLCAicHJpbWFyeVRpdGxlIjogIlR1cm5waWtlIEd5cHNpZXMiLCAib3JpZ2luYWxUaXRsZSI6ICJUdXJucGlrZSBHeXBzaWVzIiwgImlzQWR1bHQiOiAiRmFsc2UiLCAic3RhcnRZZWFyIjogIk4vQSIsICJydW50aW1lTWludXRlcyI6ICJOL0EiLCAiZ2VucmVzIjogIkNvbWVkeSxEcmFtYSJ9',
                        }
                }
            ]
        }
        EXPECTED = [
                    {
                    'genres': 'Comedy,Drama',
                    'id': 'tt5947424',
                    'isAdult': 'False',
                    'originalTitle': 'Turnpike Gypsies',
                    'primaryTitle': 'Turnpike Gypsies',
                    'runtimeMinutes': 'N/A',
                    'startYear': 'N/A'
                    }
        ]
        movies_data = read(KINESIS_EVENT)
        self.assertEqual(EXPECTED, movies_data)

    def test_read_not_a_json_raises_JSONDecodeError(self):
        KINESIS_EVENT = {'Records':
            [
                {
                    'kinesis':
                        {
                            'data': 'SGVsbG9Xb3JsZA==',
                        }
                }
            ]
        }
        with self.assertRaises(JSONDecodeError):
            read(KINESIS_EVENT)

    def test_read_invalid_json_raises_MalformedRecordError(self):
        KINESIS_EVENT = {'Records':
            [
                {
                    'Whatever':
                        {
                            'data': 'SGVsbG9Xb3JsZA==',
                        }
                }
            ]
        }
        with self.assertRaises(MalformedRecordError):
            read(KINESIS_EVENT)

    def test_write_ok(self):
        RECORD = {
            'Data': {
                "id": "someId",
                "primaryTitle": "somePrimaryTitle",
                "originalTitle": "someOriginalTitle",
                "isAdult": True,
                "startYear": "2010",
                "runtimeMinutes": "180",
                "genres": "Action,Comedy"
            }
        }
        RECORDS = [RECORD] * 2
        KINESIS_RECORDS = [{'Data': json.dumps(record).encode('utf-8'), 'PartitionKey': 'default'} for record in
                           RECORDS]

        KINESIS_RETURN_VALUE = {
            'FailedRecordCount': 0,
            'Records': [
                {
                    'SequenceNumber': '1230SS0',
                    'ShardId': 'Shard-id-000000000'
                },
                {
                    'SequenceNumber': '1230SS1',
                    'ShardId': 'Shard-id-000000000'
                }
            ],
            'EncryptionType': 'NONE'
        }
        mock_client = MagicMock()
        mock_client.put_records = MagicMock(return_value=KINESIS_RETURN_VALUE)

        with patch('boto3.client') as mock_kinesis_client_factory:
            with self.env:
                mock_kinesis_client_factory.return_value = mock_client

                response = write(RECORDS, TARGET_STREAM)

                mock_client.put_records.assert_called_once_with(Records=KINESIS_RECORDS, StreamName=TARGET_STREAM)
                self.assertEqual(KINESIS_RETURN_VALUE, response)

    def test_write_not_a_list(self):
        RECORD_SINGLE_ITEM = {
            'Data': "Whatever"
        }
        mock_client = MagicMock()

        with patch('boto3.client') as mock_kinesis_client_factory:
            with self.env:
                mock_kinesis_client_factory.return_value = mock_client
                write(RECORD_SINGLE_ITEM, TARGET_STREAM)
                mock_client.assert_not_called()

    def test_write_not_serializable(self):
        RECORD_LIST = [{
            'Data': b"SomeBytes"
        }]
        mock_client = MagicMock()

        with patch('boto3.client') as mock_kinesis_client_factory:
            with self.env:
                with self.assertRaises(TypeError):
                    mock_kinesis_client_factory.return_value = mock_client
                    write([RECORD_LIST], TARGET_STREAM)