from django.urls import path
from core.views import (
    HomeView, HowToPlayView, PlayerUUIDView, RankingsView, RemoveWhitelistView, UserLogoutView, XBoxAuthView, XboxAuthCallbackView, 
    RegisterCharacterView, GameStatusView
    )


urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('how-to-play', HowToPlayView.as_view(), name="how-to-play"),
    path('get-player-uuids', PlayerUUIDView.as_view(), name='player-uuid'),
    path('rankings', RankingsView.as_view(), name='rankings'),
    path('microsoft/auth', XBoxAuthView.as_view(), name="xbox-auth"),
    path('microsoft/auth-callback/', XboxAuthCallbackView.as_view(), name="xbox-callback"),
    path('microsoft/signout', UserLogoutView.as_view(), name="xbox-signout"),
    path('register-character', RegisterCharacterView.as_view(), name="register-character"),
    path('update-game-status', GameStatusView.as_view(), name="update-game-status"),
    path('update-rankings', RankingsView.as_view(), name="update-rankings"),
    path('remove-whitelist', RemoveWhitelistView.as_view(), name="remove-whitelist"),
]