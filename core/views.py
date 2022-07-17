from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, reverse
from django.views import View
from django.conf import settings
from core.models import Variable, XBoxAccount
from core.xbox import XBoxAuth


class HomeView(View):
    def get(self, request):
        registered = True if request.GET.get('registered') == 'true' else False
        auth_failed = True if request.GET.get('auth_failed') == 'true' else False

        allowPlayers = True if Variable.objects.get(name='allowPlayers').value == 'true' else False
        gameRunning = True if Variable.objects.get(name='gameRunning').value == 'true' else False

        return render(request, 'index.html', context={
            'auth_failed': auth_failed, 
            'registered': registered, 
            'allowPlayers': allowPlayers,
            'gameRunning': gameRunning
            })


class HowToPlayView(View):
    def get(self, request):
        return render(request, 'how_to_play.html')


class PlayerUUIDView(View):
    def get(self, request):
        gamertag = request.GET.get('gamertag')
        if gamertag:
            try:
                xbox = XBoxAccount.objects.get(gamertag=gamertag)
                return JsonResponse({'gamertag': xbox.gamertag, 'uuid': xbox.mojang_id})

            except XBoxAccount.DoesNotExist:
                return JsonResponse({'error': 'Invalid gamertag specified.'})

        xboxes = list(XBoxAccount.objects.all().values('gamertag', 'mojang_id', 'character', 'game_mode'))
        return JsonResponse(xboxes, safe=False)


class XBoxAuthView(View):
    def get(self, request):
        print("Redirecting to OAuth Consent Screen...")
        xbox = XBoxAuth()
        return redirect(xbox.auth_url)


class XboxAuthCallbackView(View):
    def get(self, request):
        print("Verifying OAuth Code...")
        code = request.GET.get('code')
        
        try:
            xbox = XBoxAuth()
            xbox_acct = xbox.authenticate(code)
            login(request, xbox_acct.xbox_user)
        except ValueError as e:
            return redirect(reverse('home') + '?auth_failed=true')

        return redirect('home')


class UserLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')
        

@method_decorator(csrf_exempt, name='dispatch')
class RegisterCharacterView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False})

        game_mode = request.POST.get('game_mode')
        character = request.POST.get('character')

        xbox: XBoxAccount = XBoxAccount.objects.get(xbox_user=request.user)
        xbox.game_mode = game_mode
        xbox.character = character
        xbox.save()

        return JsonResponse({'success': True})


class GameStatusView(View):
    def post(self, request):
        gameRunning = request.POST.get('gameRunning')
        allowPlayers = request.POST.get('allowPlayers')

        var_game = Variable.objects.get(name='gameRunning')
        if gameRunning:
            var_game.value = gameRunning
            var_game.save()

        var_allow = Variable.objects.get(name='allowPlayers')
        if allowPlayers:
            var_allow.value = allowPlayers
            var_allow.save()

        return JsonResponse({'data': {
            'gameRunning': var_game.value,
            'allowPlayers': var_allow.value,
        }})


@method_decorator(csrf_exempt, name='dispatch')
class RankingsView(View):
    def post(self, request):
        print(request.POST)
        return JsonResponse({'success': True})
