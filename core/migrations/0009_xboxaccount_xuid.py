# Generated by Django 4.0.4 on 2022-06-18 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_remove_xboxaccount_xuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='xboxaccount',
            name='xuid',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
