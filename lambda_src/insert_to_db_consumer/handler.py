from lambda_src.common_deps.service.dynamo import DynamoMovieModel
from lambda_src.common_deps.service.kinesis import read
from lambda_src.common_deps.service.logging import logger


def handle(event,context):
    logger.debug("Received event: {0}".format(event))
    movies=read(event)
    logger.debug("Storing {0} movies".format(len(movies)))
    for movie in movies:
        logger.debug("Storing {0}".format(movie))
        DynamoMovieModel(
            movie['id'],
            primaryTitle=movie['primaryTitle'],
            originalTitle=movie['originalTitle'],
            isAdult=movie['isAdult'],
            startYear=movie['startYear'],
            runtimeMinutes=movie['runtimeMinutes'],
            genres=movie['genres']
        ).save()
