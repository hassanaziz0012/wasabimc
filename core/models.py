from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Variable(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f'{self.name} = {self.value}'

    def __repr__(self) -> str:
        return f'<Variable: {self.name}={self.value}>'


class XBoxAccount(models.Model):
    name = models.CharField(max_length=100)
    gamertag = models.CharField(max_length=100)
    xbox_user = models.ForeignKey(User, on_delete=models.CASCADE)

    access_token = models.TextField()
    refresh_token = models.TextField()
    user_id = models.TextField()

    usertoken = models.TextField()
    xsts_token = models.TextField()
    xuid = models.TextField()

    mojang_id = models.TextField()
    mojang_name = models.TextField()

    game_mode = models.CharField(max_length=100, null=True, blank=True)
    character = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name}'

    def __repr__(self) -> str:
        return f'<XBoxAccount: {self.name}>'


class Rankings(models.Model):
    server = models.CharField(max_length=100)
    data = models.JSONField(default=dict, blank=True)

    def __str__(self) -> str:
        return f'{self.server}'
        
    def __repr__(self) -> str:
        return f'<Rankings: {self.server}>'
