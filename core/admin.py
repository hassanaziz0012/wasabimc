from django.contrib import admin
from core.models import Variable, XBoxAccount

# Register your models here.
@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')


@admin.register(XBoxAccount)
class XBoxAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'gamertag', 'game_mode', 'character')
    search_fields = ('name', 'gamertag', 'game_mode', 'character')
    list_filter = ('game_mode', 'character')
    