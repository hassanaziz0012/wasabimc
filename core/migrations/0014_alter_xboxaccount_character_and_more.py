# Generated by Django 4.0.4 on 2022-07-02 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_xboxaccount_character_xboxaccount_game_mode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='xboxaccount',
            name='character',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='xboxaccount',
            name='game_mode',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
