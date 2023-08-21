from django.db import models
import secrets


class User(models.Model):
    name = models.CharField(max_length=32, verbose_name="Имя", blank=True, null=True)
    phone = models.CharField(max_length=32, verbose_name="Номер телефона", unique=True)
    invitation_code = models.CharField(max_length=6)
    invited_by = models.ForeignKey('self', on_delete=models.RESTRICT, null=True)

    is_privileged = models.BooleanField(verbose_name="Привилегированный доступ", default=False)

    def __str__(self):
        return f'{self.name} {self.phone}'

    @property
    def invited_users(self):
        return User.objects.filter(invited_by=self.id)

    def save(self, *args, **kwargs):
        if not self.name:
            super().save(*args, **kwargs)
            self.name = f'user{self.id}'
            super().save()
        else:
            super().save(*args, **kwargs)

    def create_invitation_code(self):
        while invitation_code := secrets.token_hex(3):
            if User.objects.filter(invitation_code=invitation_code).exists():
                continue
            self.invitation_code = invitation_code
            break

    @classmethod
    def create_user(cls, credentials: dict):
        user = cls(**credentials)
        user.create_invitation_code()
        user.save()
        return user

    @classmethod
    def get_or_create_user(cls, credentials: dict):
        phone = credentials['phone']
        user = cls.objects.filter(phone=phone).first()
        if not user:
            user = cls.create_user(credentials)
        return user
