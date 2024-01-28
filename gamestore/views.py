import json
import os
import re
from hashlib import md5

import requests
from allauth.account.views import SignupView, LoginView
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.db.models.aggregates import Max
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.generic.edit import UpdateView, CreateView, DeleteView

from gamestore.forms import *
from gamestore.models import *


def is_gamer(user):
    return user.groups.filter(name='Gamer').exists()


def is_developer(user):
    return user.groups.filter(name='Developer').exists()


@login_required
@xframe_options_sameorigin
def load_game(request, game_id):
    # Only allow gamers to access this view
    if not is_gamer(request.user):
        raise PermissionDenied
    # Load game and show it to the user
    game = get_object_or_404(Payment, user=request.user, game=game_id).game
    return HttpResponse(requests.get(game.url))


@login_required
def play_id(request, game_id):
    # Only allow gamers to access this view
    if not is_gamer(request.user):
        raise PermissionDenied
    # get the transaction of the game purchase to ensure the user owns the game
    game = get_object_or_404(Payment, user=request.user, game=game_id).game
    # retrieve highscore for that specific game
    highscores_list = Highscores.objects.filter(game=game).order_by('-score')[:5]
    # show game view with high scores
    return render(request, 'gamestore/game_play.html', {'highscores_list': highscores_list, 'game': game})


def highscores(request):
    highscores_list_max = Highscores.objects.all().values('game').annotate(highscore=Max('score'))
    highscores_list = []
    for h in highscores_list_max:
        highscores_list.append(Highscores.objects.all().filter(game_id=h['game'], score=h['highscore']).order_by('timestamp').first())
    return render(request, 'gamestore/highscores.html', {'highscores_list': highscores_list})


@login_required
def handle_message(request):
    # Only allow gamers to access this view
    if not is_gamer(request.user):
        raise PermissionDenied

    # ignore messages that don't follow scheme
    if 'messageType' not in request.POST['message']:
        return

    # Process ajax post requests. Ignore messages that don't follow specified scheme
    if request.is_ajax() and request.method == 'POST':

        # deny access with 404 if user does not own the game
        game = get_object_or_404(Payment, user=request.user, game=request.POST['game_id']).game

        # parse message and message type
        message = json.loads(request.POST['message'])
        msg_type = message['messageType']

        # set default values in case of unknown command
        data = {'messageType': "UNKNOWN", 'message': request.POST['message']}

        if msg_type == "SCORE":
            new_score = message['score']
            # Get current highscore or create one if none exists
            highscore, _ = Highscores.objects.get_or_create(
                user=request.user,
                game=game,
                defaults={'score': new_score}
            )
            # Update score if the new score is higher
            if new_score > highscore.score:
                Highscores.objects.filter(pk=highscore.id).update(score=new_score)
            # Create new highscore html table
            hs_html = "<tr><th>User</th><th>Score</th></tr>"
            for hs_entry in Highscores.objects.filter(game=game).order_by('-score')[:5]:
                hs_html += "<tr><td>" + hs_entry.user.username + "</td><td>" + str(hs_entry.score) + "</td></tr>"
            # send the highscore html table
            data = {'messageType': "SCORE", 'highscores': hs_html}

        elif msg_type == "SAVE":
            # Remove all previous game saves from database
            GameState.objects.filter(user=request.user, game=game).delete()
            # Save game state to database
            GameState(user=request.user, game=game, state=message['gameState']).save()
            # return success
            data = {'messageType': "SAVE", 'gameState': message['gameState']}

        elif msg_type == "LOAD_REQUEST":
            # query last saved game state
            last_save = GameState.objects.filter(user=request.user, game=game).values('state').last()
            # return last game save
            data = {'messageType': "LOAD", 'gameState': last_save['state']}

        elif msg_type == "LOAD":
            # do nothing, it's from service to game
            data = {'messageType': "LOAD_REQUEST"}

        elif msg_type == "ERROR":
            # maybe log, otherwise display on client side only
            data = {'messageType': "ERROR", 'info': "Something went wrong"}

        elif msg_type == "SETTING":
            # do nothing, client side update size
            data = {'messageType': "SETTING"}

    # return message
    return JsonResponse(data)


def store(request):
    categories = Category.objects.filter(games__gt=0).distinct().order_by('-name')

    # get all games a gamer bought if logged in
    games = []
    if request.user.is_authenticated and is_gamer(request.user):
        games = [payment.game for payment in request.user.purchases.all()]
    # render store page
    return render(request, 'gamestore/store.html', {'categories': categories, 'bought_games': games})


def search(request):
    # redirect to store page if search string is empty
    if not request.GET.get('s'):
        return redirect('/')

    games = Game.objects.filter(name__icontains=request.GET['s'])

    # get all games a gamer bought if logged in
    bought_games = []
    if request.user.is_authenticated and is_gamer(request.user):
        bought_games = [payment.game for payment in request.user.purchases.all()]

    return render(request, 'gamestore/search.html', {'games': games, 'bought_games': bought_games})


@login_required
def bought_games(request):
    # Only allow gamers to access this view
    if not is_gamer(request.user):
        raise PermissionDenied
    # get all games a gamer bought
    games = [payment.game for payment in request.user.purchases.all()]
    # render game library
    return render(request, 'gamestore/bought_games.html', {'bought_games': games})


@login_required
def published_games(request):
    # Only allow gamers to access this view
    if not is_developer(request.user):
        raise PermissionDenied
    # get all games a developer has published
    games = request.user.published_games.all()
    # render library of published games
    return render(request, 'gamestore/published_games.html', {'published_games': games})


def main(request):
    if is_gamer(request.user):
        return store(request)
    elif is_developer(request.user):
        return published_games(request)
    else:
        return store(request)


@login_required
def game_transactions(request, game_id):
    # Only allow gamers to access this view
    if not is_developer(request.user):
        raise PermissionDenied
    game = get_object_or_404(Game, pk=game_id)
    # only grant access to developer of a game
    if game.developer != request.user:
        raise PermissionDenied
    return render(request, 'gamestore/game_transactions.html', {'game': game})


def buy_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)

    # Don't allow accessing the buy page if game is already owned
    if not is_gamer(request.user) or Payment.objects.filter(user=request.user, game=game_id).exists():
        return render(request, 'gamestore/game.html', {'game': game})

    # get parameters for buy game form
    pid = f"U{request.user.id}G{game.id}"
    amount = str(game.price)

    # Query environment variables to get seller configuration
    SELLER_ID = os.environ.get('SELLER_ID')
    SELLER_SECRET = os.environ.get('SELLER_SECRET')
    # Ensure that configuration exists
    if not SELLER_ID or not SELLER_SECRET:
        raise ImproperlyConfigured('Seller configuration not set!')

    # create checksum for payment
    checksumstr = f"pid={pid}&sid={SELLER_ID}&amount={amount}&token={SELLER_SECRET}"
    m = md5(checksumstr.encode("ascii"))
    checksum = m.hexdigest()

    # url that processes the payment result
    result_url = request.scheme + '://' + request.get_host() + '/payment-result/'

    # create form
    form = PaymentForm(initial={'pid': pid,
                                'sid': SELLER_ID,
                                'amount': amount,
                                'checksum': checksum,
                                'success_url': result_url,
                                'error_url': result_url,
                                'cancel_url': result_url})

    return render(request, 'gamestore/game.html', {'game': game, 'form': form})


def payment_result(request):
    # get GET parameters
    pid = request.GET["pid"]
    ref = request.GET["ref"]
    result = request.GET["result"]
    checksum_req = request.GET["checksum"]

    # Query environment variables to get seller configuration
    SELLER_SECRET = os.environ.get('SELLER_SECRET')
    # Ensure that configuration exists
    if not SELLER_SECRET:
        raise ImproperlyConfigured('Seller configuration not set!')

    # verify checksum
    checksumstr = f"pid={pid}&ref={ref}&result={result}&token={SELLER_SECRET}"
    m = md5(checksumstr.encode("ascii"))
    checksum = m.hexdigest()
    if checksum_req != checksum:
        raise PermissionDenied

    # raise PermissionDenied if invalid pid has been used
    pid_match = re.match(r'^U(\d+)G(\d+)$', pid)
    if not pid_match:
        raise PermissionDenied
    # get game and user from pid := U<user_id>G<game_id>
    user = get_object_or_404(User, pk=int(pid_match.group(1)))
    game = get_object_or_404(Game, pk=int(pid_match.group(2)))

    # redirect if transaction was not successful
    if result != "success":
        return redirect(f'/game/{game.id}/')

    # create payment in DB
    payment = Payment(user=user, game=game, price=game.price)
    payment.ref = ref
    payment.save()

    # redirect to play game page
    return redirect(f'/game/{payment.game.id}/play/')


class GameUpdateView(UpdateView):
    model = Game
    fields = ['price', 'name', 'url', 'description', 'category']
    success_url = "/"
    template_name = "gamestore/game_edit.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().developer != self.request.user:
            raise PermissionDenied
        return super(GameUpdateView, self).dispatch(request, *args, **kwargs)


class GameCreateView(CreateView):
    model = Game
    fields = ['price', 'name', 'url', 'description', 'category']
    success_url = "/"
    template_name = "gamestore/game_edit.html"

    def form_valid(self, form):
        form.instance.developer = self.request.user
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if not is_developer(request.user):
            raise PermissionDenied
        return super(GameCreateView, self).dispatch(request, *args, **kwargs)


class GameDeleteView(DeleteView):
    model = Game
    success_url = "/"
    template_name = "gamestore/game_delete.html"

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().developer != self.request.user:
            raise PermissionDenied
        return super(GameDeleteView, self).dispatch(request, *args, **kwargs)


class MySignupView(SignupView):
    template_name = 'gamestore/register.html'
    form_class = RegistrationForm


class MyLoginView(LoginView):
    template_name = 'gamestore/login.html'
