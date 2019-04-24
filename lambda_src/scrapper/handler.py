import os

from lambda_src.common_deps.model.ApiGWResponse import ApiGWResponse
from lambda_src.common_deps.model.exception import ScrappingError
from lambda_src.scrapper.scrapper import get_page, extract_data
from lambda_src.common_deps.service.kinesis import write
from lambda_src.common_deps.service.logging import logger

SCRAP_URL = os.getenv('SCRAP_URL', 'DUMMY_URL')
PROCESS_DATA_STREAM_NAME=os.getenv('PROCESS_DATA_STREAM_NAME', 'DUMMY_DATA_STREAM')
PROCESS_ERROR_STREAM_NAME=os.getenv('PROCESS_ERROR_STREAM_NAME', 'DUMMY_ERROR_STREAM')

def handle(event, context):
    body = get_page(SCRAP_URL)
    try:
        movies = extract_data(body)
        write(movies, PROCESS_DATA_STREAM_NAME)
    except ScrappingError as e:
        logger.warning(e)
        write(_generate_error_message(body, e), PROCESS_ERROR_STREAM_NAME)
    return ApiGWResponse({}).to_dict()

def _generate_error_message(body, error):
    return [{
        "content": body.decode('utf-8'),
        "error_message": str(error)
    }]