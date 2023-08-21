from django.conf import settings
from jose import JWTError
from jose import jwt
from rest_framework.request import Request

from .exceptions import HttpException
from .models import User
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.permissions import BasePermission


class UserAuthentication(authentication.BaseAuthentication):
    auth_exception = exceptions.AuthenticationFailed('Not authenticated')

    def authenticate(self, request: Request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '.')
        token = auth_header.split()[-1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
        except JWTError:
            raise self.auth_exception

        user_id = payload.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise self.auth_exception

        return user, self.__class__


class PrivilegeAccessPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_privileged)
