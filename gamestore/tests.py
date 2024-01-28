import random
import string

from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase, Client
from django.contrib.auth.models import Group

from gamestore.models import *

class SimpleTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.randstr = ''.join(random.sample(string.ascii_letters, 5))
        self.randint = random.randint(5,50)

    def test_admin(self):
        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 301)

    def test_models(self):

        # create test db
        user1 = User.objects.create_user(username='user1', password='top_secret')
        user2 = User.objects.create_user(username='user2', password='top_secret')
        user3 = User.objects.create_user(username='user3', password='top_secret')

        category1 = Category.objects.create(name='cat1')
        category2 = Category.objects.create(name='cat2')
        game1 = Game.objects.create(developer=user1, category=category1, price=0)
        game2 = Game.objects.create(developer=user1, category=category1, price=1)
        game3 = Game.objects.create(developer=user1, category=category2, price=2.2)
        Highscores.objects.create(game=game1, user=user2, score=1.0)
        Highscores.objects.create(game=game2, user=user2, score=2.0)
        Highscores.objects.create(game=game3, user=user2, score=3.0)
        Highscores.objects.create(game=game2, user=user3, score=3.0)
        Payment.objects.create(user=user2, game=game1, price=1)
        Payment.objects.create(user=user2, game=game2, price=1)
        Payment.objects.create(user=user3, game=game1, price=1)

        # check categories
        self.assertEqual(category1.games.all().__len__(), 2)
        self.assertEqual(category2.games.all().__len__(), 1)

        # check developer
        self.assertEqual(user1.published_games.all().__len__(), 3)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                # should throw error, because gamer1 already has a highscore for game1
                Highscores.objects.create(game=game1, user=user2, score=3.0)

        # update score
        Highscores.objects.update_or_create(game=game1, user=user2, defaults={'score': 3.0})

        # check if score was updated
        self.assertEqual(game1.highscores.get(user=user2).score, 3.0)

        # check that old highscore was deleted
        self.assertEqual(game1.highscores.all().__len__(), 1)

        # check highscores
        self.assertEqual(game2.highscores.all().__len__(), 2)
        self.assertEqual(game3.highscores.all().__len__(), 1)
        self.assertEqual(user2.highscores.all().__len__(), 3)
        self.assertEqual(user3.highscores.all().__len__(), 1)

        # check payments
        self.assertEqual(user2.purchases.all().__len__(), 2)
        self.assertEqual(user3.purchases.all().__len__(), 1)
        self.assertEqual(game1.sales.all().__len__(), 2)
        self.assertEqual(game2.sales.all().__len__(), 1)

    def test_frontend_notauth(self):

        user1 = User.objects.create_user(username='user1', password='top_secret')
        category1 = Category.objects.create(name='cat1')
        game1 = Game.objects.create(developer=user1, category=category1, price=0)

        response = self.client.get(path='/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/accounts/login/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/accounts/signup/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/accounts/logout/')
        self.assertEqual(response.status_code, 302)

        response = self.client.get(path=f'/game/{game1.id}/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/game/999/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game1.id}/edit/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/game/999/edit/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game1.id}/load/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], f'/accounts/login/?next=/game/{game1.id}/load/')

        response = self.client.get(path='/game/999/load/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], f'/accounts/login/?next=/game/999/load/')

        response = self.client.get(path=f'/game/{game1.id}/delete/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/game/999/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game1.id}/play/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], f'/accounts/login/?next=/game/{game1.id}/play/')

        response = self.client.get(path='/game/999/play/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/accounts/login/?next=/game/999/play/')

        response = self.client.get(path='/bought-games/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/accounts/login/?next=/bought-games/')

        response = self.client.get(path='/high-scores/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/search/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/')

        response = self.client.get(path='/search/?s=test')
        self.assertEqual(response.status_code, 200)

    def test_frontend_gamer(self):

        user1 = User.objects.create_user(username='user1', password='top_secret')
        group_gamer, _ = Group.objects.get_or_create(name='Gamer')
        group_gamer.user_set.add(user1)

        user2 = User.objects.create_user(username='user2', password='top_secret')
        group_developer, _ = Group.objects.get_or_create(name='Developer')
        group_developer.user_set.add(user2)

        category1 = Category.objects.create(name='cat1')
        game1 = Game.objects.create(developer=user2, category=category1, price=1)
        game2 = Game.objects.create(developer=user2, category=category1, price=1)

        Payment.objects.create(user=user1, game=game1, price=1)

        self.client.login(username='user1', password='top_secret')

        response = self.client.get(path='/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/accounts/login/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/')

        response = self.client.get(path='/accounts/signup/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/')

        response = self.client.get(path=f'/game/{game1.id}/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/game/999/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game1.id}/edit/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/game/999/edit/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game2.id}/load/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path='/game/999/load/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game1.id}/delete/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/game/999/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game1.id}/play/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path=f'/game/{game2.id}/play/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path='/game/999/play/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path='/bought-games/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/high-scores/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/accounts/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/accounts/login/')

    def test_frontend_developer(self):

        user1 = User.objects.create_user(username='user1', password='top_secret')
        group_gamer, _ = Group.objects.get_or_create(name='Gamer')
        group_gamer.user_set.add(user1)

        user2 = User.objects.create_user(username='user2', password='top_secret')
        group_gamer, _ = Group.objects.get_or_create(name='Developer')
        group_gamer.user_set.add(user2)

        user3 = User.objects.create_user(username='user3', password='top_secret')
        group_gamer.user_set.add(user3)

        category1 = Category.objects.create(name='cat1')
        game1 = Game.objects.create(developer=user2, category=category1, price=1)
        game2 = Game.objects.create(developer=user3, category=category1, price=1)

        Payment.objects.create(user=user1, game=game1, price=1)

        self.client.login(username='user2', password='top_secret')

        response = self.client.get(path='/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/accounts/login/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/')

        response = self.client.get(path='/accounts/signup/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/')

        response = self.client.get(path='/accounts/login/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/')

        response = self.client.get(path=f'/game/{game1.id}/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/game/999/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game1.id}/edit/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path=f'/game/{game2.id}/edit/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/game/999/edit/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game1.id}/load/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path=f'/game/{game2.id}/load/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/game/999/load/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path=f'/game/{game1.id}/delete/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path=f'/game/{game2.id}/delete/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/game/999/delete/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(path=f'/game/{game1.id}/play/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path=f'/game/{game2.id}/play/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/game/999/play/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/bought-games/')
        self.assertEqual(response.status_code, 403)

        response = self.client.get(path='/high-scores/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get(path='/accounts/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/accounts/login/')