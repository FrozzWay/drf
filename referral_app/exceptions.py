from rest_framework.exceptions import APIException
from rest_framework import status


class HttpException(APIException):
    def __init__(self, detail=None, status_code=None, code=None):
        super().__init__(detail, code)
        self.status_code = status_code if status_code else status.HTTP_400_BAD_REQUEST