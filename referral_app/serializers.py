from rest_framework import serializers as s
from referral_app.models import User


class LogInSignUpSerializer(s.Serializer):
    name = s.CharField(min_length=3, max_length=50, required=False)
    phone = s.RegexField(r'^[\+]?[0-9]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$', min_length=12, max_length=20)
    is_privileged = s.BooleanField(default=False)


class SMSVerificationSerializer(s.Serializer):
    """
    sms_code — Код, который подтверждает пользователь
    sms_token — JSON Web Token, зашифрованный, в полезной нагрузке которого :
            User: dict{name: str, phone: str, is_privileged: boolean}
            sent_sms_code: str - отправленный сервером sms код.

    sms_token может быть явно передан клиентом в теле запроса или, в противном случае, будет извлекаться из базы
    данных сессии (django session) при смс-верификации в браузере.
    """
    sms_token = s.CharField(required=False)
    sms_code = s.CharField(max_length=4, min_length=4)


class UserSerializer(s.ModelSerializer):
    invited_users_phones = s.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'phone', 'invitation_code', 'invited_by', 'invited_users_phones')

    def get_invited_users_phones(self, obj: User):
        return obj.invited_users.values_list('phone', flat=True)


class SetInvitationSerializer(s.Serializer):
    invitation_code = s.CharField(max_length=6)