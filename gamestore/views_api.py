from django.db.models import Max
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

from gamestore.models import Game, Highscores, Payment
from gamestore.views import is_developer, is_gamer


def game_id(request, game_id):
    if request.method == 'GET':
        game = get_object_or_404(Game, id=game_id)
        if game.developer == request.user:
            return JsonResponse(
                {'name': game.name,
                 'price': game.price,
                 'description': game.description,
                 'category': game.category.name,
                 'url': game.url}, safe=False)
        else:
            return JsonResponse(
                {'name': game.name,
                 'price': game.price,
                 'description': game.description,
                 'category': game.category.name}, safe=False)
    elif request.method == 'POST':
        game = get_object_or_404(Game, id=game_id)
        if game.developer == request.user:
            game.name = request.POST['name']
            game.price = request.POST['price']
            game.description = request.POST['description']
            game.category = request.POST['category']
            game.url = request.POST['url']
            game.save()
            return JsonResponse(
                {'name': game.name,
                 'price': game.price,
                 'description': game.description,
                 'category': game.category.name,
                 'url': game.url}, safe=False)
        else:
            return HttpResponse(status=403)
    elif request.method == 'DELETE':
        game = get_object_or_404(Game, id=game_id)
        if game.developer == request.user:
            game.delete()
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def game(request):
    if request.method == 'GET':
        games = Game.objects.all()
        res = []
        for game in games:
            res.append({'name': game.name,
                        'price': game.price,
                        'description': game.description,
                        'category': game.category.name})
        return JsonResponse(res, safe=False)
    elif request.method == 'PUT':
        if is_developer(request.user):
            game = Game(name=request.POST['name'],
                        price=request.POST['price'],
                        description=request.POST['description'],
                        category=request.POST['category'],
                        url=request.POST['url'],
                        developer=request.user)
            game.save()
            return JsonResponse(
                {'name': game.name,
                 'price': game.price,
                 'description': game.description,
                 'category': game.category.name,
                 'url': game.url}, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def game_id_transaction(request, game_id):
    if request.method == 'GET':
        game = get_object_or_404(Game, id=game_id)
        if game.developer == request.user:
            res = []
            for sale in game.sales:
                res.append({'user': sale.user.username,
                            'timestamp': sale.timestamp,
                            'price': sale.price,
                            'ref': sale.ref})
            return JsonResponse(res, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)


def highscore(request):
    if request.method == 'GET':
        highscores_list_max = Highscores.objects.all().values('game').annotate(highscore=Max('score'))
        highscores_list = Highscores.objects.filter(score__in=highscores_list_max.values('highscore'))
        res = []
        for highscore in highscores_list:
            res.append({'game': highscore.game.name,
                        'user': highscore.user.username,
                        'score': highscore.score,
                        'timestamp': highscore.timestamp})
        return JsonResponse(res, safe=False)
    else:
        return HttpResponse(status=405)


def highscore_id(request, game_id):
    if request.method == 'GET':
        game = get_object_or_404(Payment, user=request.user, game=game_id).game
        highscores_list = Highscores.objects.filter(game=game).order_by('-score')[:5]
        res = []
        for highscore in highscores_list:
            res.append({'game': highscore.game.name,
                        'user': highscore.user.username,
                        'score': highscore.score,
                        'timestamp': highscore.timestamp})
        return JsonResponse(res, safe=False)
    else:
        return HttpResponse(status=405)


def gamer_game(request):
    if request.method == 'GET':
        if is_gamer(request.user):
            games = [payment.game for payment in request.user.purchases.all()]
            res = []
            for game in games:
                res.append({'name': game.name,
                            'price': game.price,
                            'description': game.description,
                            'category': game.category.name})
            return JsonResponse(res, safe=False)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=405)
