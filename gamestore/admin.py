from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin

admin.site.register(Game)
admin.site.register(Highscores)
admin.site.register(Payment)
admin.site.register(Category)
admin.site.register(GameState)
admin.site.register(User, UserAdmin)
