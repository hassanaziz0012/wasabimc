# Generated by Django 4.0.4 on 2022-06-18 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_xboxaccount_user_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='xboxaccount',
            name='xsts_token',
        ),
    ]
