import base64
import json

import boto3

from lambda_src.common_deps.service.logging import logger

DATA_NAME = 'Data'
PARTITION_KEY_NAME = 'PartitionKey'
DEFAULT_PARTITION_KEY = 'default'


def write(records, stream_name):
    if isinstance(records,list):
        client = boto3.client('kinesis')
        kinesis_records = [{DATA_NAME: json.dumps(record).encode('utf-8'), PARTITION_KEY_NAME: DEFAULT_PARTITION_KEY} for
                           record in records]
        logger.debug("Writing to Kinesis: {0}".format(kinesis_records))
        return client.put_records(Records=kinesis_records, StreamName=stream_name)


def read(event):
    logger.debug("Processing kinesis event: {0}".format(event))
    records = event.get("Records")
    processed_records = [_read_record(record) for record in records]
    return [record for record in processed_records if record is not None]


def _read_record(record):
    logger.debug("Processing record: {0}".format(record))
    try:
        string_data = record["kinesis"]["data"]
        return json.loads(base64.b64decode(string_data))
    except KeyError:
        logger.error("The record {0} has thrown a KeyError".format(record))
        raise MalformedRecordError(record)


class MalformedRecordError(KeyError):
    def __init__(self, record):
        super().__init__()
        self.record = record

    def __str__(self):
        logger.error("Couldn't deserialize the following record: {0}".format(self.record))
        return "Couldn't deserialize the following record: {0}".format(self.record)