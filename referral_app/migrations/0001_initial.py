# Generated by Django 4.2.4 on 2023-08-18 13:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True, verbose_name='Имя')),
                ('phone', models.CharField(max_length=32, verbose_name='Номер телефона')),
                ('invite_code', models.CharField(max_length=6)),
                ('invited_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='referral_app.user')),
            ],
        ),
    ]
