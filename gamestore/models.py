from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    token = models.CharField(max_length=255, unique=False)


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    url = models.URLField(null=False, blank=False)
    name = models.CharField(max_length=255, default='', unique=False)
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='published_games')
    price = models.FloatField(validators=[MinValueValidator(0)])
    description = models.CharField(max_length=511, default='', unique=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='games')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sales')
    timestamp = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(validators=[MinValueValidator(0)])
    ref = models.CharField(max_length=511, unique=True, null=True)

    class Meta:
        unique_together = (("user", "game"),)


class GameState(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='state')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='state')
    state = models.CharField(max_length=511, default='', unique=False)


class Highscores(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='highscores')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highscores')
    score = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("game", "user")
