"""gamestore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from gamestore import views
from gamestore import views_api as api
from gamestore.views import MyLoginView, MySignupView


urlpatterns = [
    # Admin paths
    path('admin/', admin.site.urls),
    # Account paths
    path('accounts/login/', MyLoginView.as_view(), name='account_login'),
    path('accounts/signup/', MySignupView.as_view(), name='account_signup'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('allauth.urls')),
    # Developer paths
    path('game/<int:game_id>/transactions/', views.game_transactions),
    path('game/add/', views.GameCreateView.as_view()),
    path('game/<int:pk>/edit/', views.GameUpdateView.as_view()),
    path('game/<int:pk>/delete/', views.GameDeleteView.as_view()),
    # Gamer paths
    path('bought-games/', views.bought_games),
    path('game/<int:game_id>/', views.buy_game),
    path('game/<int:game_id>/load/', views.load_game),
    path('payment-result/', views.payment_result),
    path('game/<int:game_id>/play/', views.play_id),
    path('ajax/handle_message/', views.handle_message, name='handle_message'),
    path('high-scores/', views.highscores),
    path('search/', views.search),
    # Unrestricted
    path('', views.main, name='home'),
    # API
    path('api/game/', api.game),
    path('api/game/<int:game_id>/', api.game_id),
    path('api/game/<int:game_id>/transactions/', api.game_id_transaction),
    path('api/gamer/game/', api.gamer_game),
    path('api/highscore/', api.highscore),
    path('api/highscore/<int:game_id>/', api.highscore_id),
]
