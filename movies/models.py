from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Movie(models.Model):
    class MovieType(models.TextChoices):
        SHORT = 'short', _('Short')
        MOVIE = 'movie', _('Movie')
        SERIES = 'series', _('Series')
        SPECIAL = 'tvSpecial', _('TvSpecial')
        NULL = 'null', _('Null')
    
    type = models.CharField(
        max_length=10,
        choices=MovieType.choices,
        default=MovieType.NULL
    )
    title = models.CharField(max_length=500)
    original_title  = models.CharField(max_length=500)
    year = models.PositiveIntegerField()
    duration = models.PositiveIntegerField()
    director = models.CharField(max_length=100)
    avgRating = models.FloatField()

    genres = models.ManyToManyField(Genre, through='GenreToken')

    def __str__(self):
        return self.title
    
class GenreToken(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'genre')
