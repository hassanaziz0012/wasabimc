# Generated by Django 4.0.4 on 2022-06-20 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_xboxaccount_mojang_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='xboxaccount',
            name='mojang_name',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
