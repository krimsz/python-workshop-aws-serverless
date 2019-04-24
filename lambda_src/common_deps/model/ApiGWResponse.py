import json


class ApiGWResponse(object):

    def __init__(self, body, status_code=200, headers={}):
        self._body = body
        self._status_code = status_code
        self._headers = headers

    @property
    def body(self):
        return self._body

    @property
    def status_code(self):
        return self._status_code

    @property
    def headers(self):
        return self._headers

    def to_dict(self):
        response = {
            'statusCode': self.status_code,
            'headers': self.headers,
            'body': json.dumps(self.body)
        }
        return response
