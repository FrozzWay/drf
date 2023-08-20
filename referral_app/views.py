import time
from datetime import datetime
from datetime import timedelta

import jose.exceptions
from jose import jwt, jwe

from django.shortcuts import redirect, render
from django.conf import settings

from rest_framework import status, generics, mixins
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import HttpException
from .models import User
from .auth import PrivilegeAccessPermission, UserAuthentication
from .serializers import *


class AuthView(APIView):
    step_1_template = 'referral_app/login.html'
    step_2_template = 'referral_app/sms_conf.html'

    def get(self, request: Request):
        if request.query_params.get('sms_confirmation'):
            if request.session.get('sms_token'):
                return render(request, self.step_2_template, context={})
            return redirect('referral_app:login')
        return render(request, self.step_1_template, context={})

    def post(self, request: Request):
        if request.query_params.get('sms_confirmation'):
            return self.verify_sms(request)  # step 2
        return self.perform_auth_attempt(request)  # step 1

    def perform_auth_attempt(self, request: Request):
        serializer = LogInSignUpSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            encrypted_token = self.create_sms_token(serializer.data)

            if request.accepted_media_type == 'application/json':
                return Response(status=status.HTTP_200_OK, data={
                    'sms_token': encrypted_token,
                    'url_to_confirm': request.stream.path + '?sms_confirmation=1',
                    'fields_to_be_required': ['sms_code']
                })

            request.session['sms_token'] = encrypted_token.decode('utf-8')
            return redirect('/login?sms_confirmation=1')

    def verify_sms(self, request: Request):
        serializer = SMSVerificationSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user_sms_code = serializer.data.get('sms_code')
            sms_token = serializer.data.get('sms_token') or request.session.get('sms_token')

            if not sms_token:
                raise HttpException('sms token is not provided')

            token = self.decrypt_token(sms_token)
            payload = self.decode_token(token, key='')

            # Verify sms code
            if payload.get('sent_sms_code') != user_sms_code:
                raise HttpException('Wrong sms code', status_code=status.HTTP_401_UNAUTHORIZED)

            return self.authorize(request, payload['credentials'])

    def authorize(self, request: Request, credentials: dict):
        user = User.get_or_create_user(credentials)
        token = self.create_bearer_token(user)
        return Response({
            'message': 'You have successfully authenticated',
            'bearer_token': token
        })

    @staticmethod
    def create_bearer_token(user: User) -> str:
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=settings.SESSION_COOKIE_AGE),
            'user_id': user.id
        }
        return jwt.encode(payload, settings.SECRET_KEY)

    @staticmethod
    def create_sms_token(credentials) -> bytes:
        time.sleep(2)  # задержка по условию
        sms_code = '0000'  # stub
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=60*5),
            'credentials': dict(credentials),
            'sent_sms_code': sms_code,
        }
        token = jwt.encode(payload, '')
        encrypted_token = jwe.encrypt(token.encode("utf-8"), key=settings.JWE_SECRET, encryption='A256CBC-HS512')
        return encrypted_token

    @staticmethod
    def decrypt_token(token) -> str:
        try:
            return jwe.decrypt(token, settings.JWE_SECRET).decode()
        except (jose.exceptions.JWEError, jose.exceptions.JWEParseError):
            raise HttpException('Invalid token')

    @staticmethod
    def decode_token(token, *args, **kwargs) -> dict:
        try:
            return jwt.decode(token, *args, **kwargs)
        except jose.exceptions.JWTError:
            raise HttpException('Token lifetime is expired or invalid token is sent')


class ProfileView(mixins.RetrieveModelMixin, generics.GenericAPIView):
    authentication_classes = [UserAuthentication]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, pk=None):
        if pk is None:
            self.kwargs['pk'] = request.user.id
            return self.retrieve(request)

        if not (request.user.is_privileged or request.user.id == pk):
            raise HttpException('You don\'t have permission for that', status.HTTP_403_FORBIDDEN)

        return self.retrieve(request)


class ListProfileView(generics.ListAPIView):
    authentication_classes = [UserAuthentication]
    permission_classes = [PrivilegeAccessPermission]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SetInvitationView(APIView):
    authentication_classes = [UserAuthentication]

    def post(self, request):
        serializer = SetInvitationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            invitation_code = serializer.data.get('invitation_code')
            partner_user = User.objects.filter(invitation_code=invitation_code).first()

            if request.user.invited_by is not None:
                raise HttpException('Invitation code is already set', status_code=status.HTTP_409_CONFLICT)
            if not partner_user:
                raise HttpException('User with such invitation code doest not exist')
            if partner_user.id == request.user.id:
                raise HttpException('Can\'t use your own code')

            request.user.invited_by = partner_user
            request.user.save()
            return Response(UserSerializer(request.user).data)