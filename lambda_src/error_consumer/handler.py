from lambda_src.common_deps.service.kinesis import read
from lambda_src.common_deps.service.logging import logger


def handle(event: object, context: object) -> object:
    error_event = read(event)
    logger.info("The following information has errored {0}".format(error_event))