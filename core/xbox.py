"""
Example scripts that performs XBL authentication
"""
import os
from typing import Tuple
import os
import requests
import json

from django.conf import settings
from django.contrib.auth.models import User
from pathlib import Path
from yarl import URL
from core.models import XBoxAccount


class XBoxAuth:
    def __init__(self) -> None:
        self.client_id = settings.MICROSOFT_AUTH_CLIENT_ID
        self.client_secret = settings.MICROSOFT_AUTH_CLIENT_SECRET
        self.redirect_uri = settings.MICROSOFT_AUTH_REDIRECT_URI

        self.TOKEN_FILEPATH = Path.joinpath(settings.BASE_DIR, Path("tokens/tokens.json"))

        self._scopes = ['XboxLive.signin', 'XboxLive.offline_access']

        self.GRAPH_API_URL = "https://graph.microsoft.com/v1.0"
        self.OAUTH_URL = "https://login.live.com/oauth20_token.srf"

    @property
    def auth_url(self):
        query_string = {
            "client_id": self.client_id,
            "response_type": "code",
            "approval_prompt": "auto",
            "scope": " ".join(self._scopes),
            "redirect_uri": self.redirect_uri,
        }

        return str(
            URL("https://login.live.com/oauth20_authorize.srf").with_query(query_string)
        )

    def authenticate(self, code: str, save: bool = False):
        data = self._request_tokens(code)

        access_token = data['access_token']
        refresh_token = data['refresh_token']
        user_id = data['user_id']

        usertoken = self._get_user_token(access_token)
        xsts_token, xuid, userhash = self._get_xsts_token(usertoken)
        account_name, gamertag = self.get_profile(xuid, xsts_token, userhash)
        mojang_id, mojang_name = self._get_mojang_id_and_name(gamertag)

        if User.objects.filter(username=account_name).exists():
            # If user already exists, simply update its values with the latest ones.
            user: User = User.objects.get(username=account_name)
            user.username = account_name
            user.save()
        else:
            # If user doesn't exist, create a new one.
            user = User.objects.create_user(username=account_name)
            user.save()

        if XBoxAccount.objects.filter(user_id=user_id).exists():
            # If account already exists, simply update its values with the latest ones.
            xbox: XBoxAccount = XBoxAccount.objects.get(user_id=user_id)
            xbox.access_token = access_token
            xbox.refresh_token = refresh_token
            xbox.user_id = user_id
            xbox.usertoken = usertoken
            xbox.xsts_token = xsts_token
            xbox.xuid = xuid
            xbox.name = account_name
            xbox.gamertag = gamertag
            xbox.mojang_id = mojang_id
            xbox.mojang_name = mojang_name
            xbox.save()

        else:
            # If account doesn't exist, create a new one.
            xbox = XBoxAccount.objects.create(
                access_token=access_token, refresh_token=refresh_token, user_id=user_id, usertoken=usertoken, 
                xsts_token=xsts_token, xuid=xuid, name=account_name, gamertag=gamertag, mojang_id=mojang_id,
                mojang_name=mojang_name, xbox_user=user
                )
            xbox.save()

        return xbox

    def _parse_tokenfile(self):
        if not os.path.exists(self.TOKEN_FILEPATH):
            raise FileNotFoundError("Token file does not exist. Please request a new access token from the API.")

        with open(self.TOKEN_FILEPATH, 'r') as file:
            data = file.read()
            parsed = json.loads(data)

            xbox = XBoxAccount.objects.get(usertoken=parsed['user_id'])
            return xbox

    def _request_tokens(self, code):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri,
            'scope': " ".join(self._scopes)
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        resp = requests.post(self.OAUTH_URL, data=data, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        print(f"Requesting tokens for code: {code} --- Output:")
        print(resp.json())
        if resp.status_code == 200:
            return data
        else:
            return False
        
    def _refresh_tokens(self, xbox_acct: XBoxAccount):
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': xbox_acct.refresh_token,
            'scope': " ".join(self._scopes)
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        resp = requests.post(self.OAUTH_URL, data=data, headers=headers)
        print(resp.json())
        if resp.status_code == 200:
            return True
        else:
            return False

    def _get_user_token(self, access_token) -> str:
        """Authenticate via access token and receive user token."""
        url = "https://user.auth.xboxlive.com/user/authenticate"
        headers = {"x-xbl-contract-version": "1"}
        data = {
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f'd={access_token}'
            },
        }

        resp = requests.post(url, json=data, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        token = data['Token']
        return token

    def _get_xsts_token(self, usertoken):
        """Authorize via user token and receive final X token."""
        url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        headers = {"x-xbl-contract-version": "1"}
        data = {
            "RelyingParty":  "http://xboxlive.com",
            "TokenType": "JWT",
            "Properties": {
                "UserTokens": [usertoken],
                "SandboxId": "RETAIL",
            },
        }

        resp = requests.post(url, json=data, headers=headers)
        if(resp.status_code == 401): # if unauthorized
            print('Failed to authorize you! Your password or username may be wrong or you are trying to use child account (< 18 years old)')
            raise ValueError()
        resp.raise_for_status()
        data = resp.json()
        token = data['Token']
        xuid = data['DisplayClaims']['xui'][0]['xid']
        userhash = data['DisplayClaims']['xui'][0]['uhs']
        return (token, xuid, userhash)

    def _get_mojang_id_and_name(self, username) -> Tuple[int, str]:
        try:
            url = f'https://api.mojang.com/users/profiles/minecraft/{username}'
            resp = requests.get(url)
            
            print(username)
            print(resp)
            data = resp.json()
            print(data)
            mojang_id, mojang_name  = data['id'], data['name']
            return (mojang_id, mojang_name)
        except requests.exceptions.JSONDecodeError:
            raise ValueError("This account does not own Minecraft!")

    def get_profile(self, xuid, xsts_token, userhash):
        headers = {"x-xbl-contract-version": "3", 'Authorization': f"XBL3.0 x={userhash};{xsts_token}"}
        params = {
            "settings": ','.join(
                [
                    "Gamertag",
                    "ModernGamertag",
                    "ModernGamertagSuffix",
                    "UniqueModernGamertag",
                    "RealNameOverride",
                    "Bio",
                    "Location",
                    "Gamerscore",
                    "GameDisplayPicRaw",
                    "TenureLevel",
                    "AccountTier",
                    "XboxOneRep",
                    "PreferredColor",
                    "Watermarks",
                    "IsQuarantined",
                ]
            )
        }
        url = f"https://profile.xboxlive.com/users/xuid({xuid})/profile/settings"

        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()['profileUsers'][0]['settings']

        account_name = [item for item in data if item['id'] == 'RealNameOverride'][0]['value']
        gamertag = [item for item in data if item['id'] == 'Gamertag'][0]['value']
        return (account_name, gamertag)


    class Exceptions:
        pass
