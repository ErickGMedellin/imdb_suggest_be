from rest_framework import serializers
from .models import Movie, Genre, GenreToken

class GenreSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Genre
        fields = ['name']

class MovieSerializer(serializers.ModelSerializer):

    genres = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = '__all__'

    def get_genres(self, obj):
        genre_tokens = GenreToken.objects.filter(movie=obj)
        genres = [genre_token.genre.name for genre_token in genre_tokens]
        return genres