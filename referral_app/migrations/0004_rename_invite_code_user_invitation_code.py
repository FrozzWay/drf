# Generated by Django 4.2.4 on 2023-08-18 22:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('referral_app', '0003_user_is_privileged_alter_user_phone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='invite_code',
            new_name='invitation_code',
        ),
    ]
