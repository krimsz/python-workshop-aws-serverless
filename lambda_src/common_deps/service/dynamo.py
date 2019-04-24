import os

from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model

MOVIES_TABLE_NAME = os.getenv("MOVIES_TABLE_NAME",'dummy')
AWS_DEFAULT_REGION=os.getenv("AWS_DEFAULT_REGION","eu-west-2")

class DynamoMovieModel(Model):
    class Meta:
        table_name = MOVIES_TABLE_NAME
        region=AWS_DEFAULT_REGION
    id = UnicodeAttribute(hash_key=True)
    primaryTitle = UnicodeAttribute()
    originalTitle = UnicodeAttribute()
    isAdult = UnicodeAttribute()
    startYear = UnicodeAttribute()
    runtimeMinutes = UnicodeAttribute()
    genres = UnicodeAttribute()
