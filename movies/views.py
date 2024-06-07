from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import pandas as pd
from movies.models import Movie, Genre, GenreToken
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.request import Request
from .serializers import MovieSerializer
from random import sample

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the movies index.")

# This save_csv function is used at the save_csv endpoint to save information into mysql database.
@csrf_exempt
def save_csv(request):
    
    if request.method == "POST":

        print("Starting save_csv process...")

        csv_file = request.FILES.get('csv_file')

        if not csv_file:
            return JsonResponse({"error": "No file uploaded"}, status=400)
        if not csv_file.name.endswith('.csv'):
            return JsonResponse({"error": "This is not a CSV file."}, status=400)

        try:

            reader = pd.read_csv(csv_file)

            for i in range(len(reader)):

                genres = reader.iloc[i,:]['genres'].split(',')
                row = reader.iloc[i,:]

                with transaction.atomic():

                    # Create or get the movie object
                    movie, created = Movie.objects.get_or_create(
                        type = row['titleType'],
                        title = row['primaryTitle'],
                        original_title = row['originalTitle'],
                        year = row['startYear'],
                        duration = row['runtimeMinutes'],
                        director = row['director'],
                        avgRating = row['averageRating'],
                    )

                    # Saving genres:
                    for genre_name in genres:
                        genre_name = genre_name.strip()
                        genre, created = Genre.objects.get_or_create(name=genre_name)
                        GenreToken.objects.get_or_create(movie=movie, genre=genre)

            return JsonResponse({"message": "CSV file successfully uploaded and processed"}, status=200)

        except Exception as e:

            print(f"Error: {e}")

            return JsonResponse({"message": "There's been an error saving data."}, status=500)
        
#   This function was a first aproximation to the queries procedure to ger 3 random values.
class RandomDataView(generics.GenericAPIView):
    serializer_class = MovieSerializer

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        total_count = Movie.objects.count()
        random_ids = sample(range(1, total_count+1), min(3, total_count))
        random_data = Movie.objects.filter(id__in=random_ids)
        serializer = self.get_serializer(random_data, many=True)

        return Response(serializer.data)
    
#   This is another query using a rating range
class QueryByRatingView(generics.GenericAPIView):
    serializer_class = MovieSerializer

    @csrf_exempt
    def get(self,request):
        min_value = request.data.get('min')
        max_value = request.data.get('max')

        parsed_min = min_value if min_value else 0
        parsed_max = max_value if max_value else 10

        movies_filtered = Movie.objects.filter(avgRating__gte=parsed_min, avgRating__lte=parsed_max)
        random_movies = movies_filtered.order_by('?')[:min(3, movies_filtered.count())]

        serializer = self.get_serializer(random_movies, many=True)

        return Response(serializer.data)

#   This function returns 3 random values queried by Genre
class QueryByGenre(generics.GenericAPIView):
    serializer_class = MovieSerializer

    @csrf_exempt
    def get(self, request):

        genreRequestList = request.data.get('genres', [])

        genreListName = Genre.objects.filter(name__in=genreRequestList)
        tokenId = GenreToken.objects.filter(genre__in=genreListName).values_list('movie_id', flat=True).distinct()
        movies_filtered = Movie.objects.filter(id__in=tokenId)
        movies = movies_filtered.order_by('?')[:min(3, movies_filtered.count())]

        serializer = self.get_serializer(movies, many=True)

        return Response(serializer.data)
        
#   This is the final function, the Front End project will make this request every time.
#   This function considers diferent filters and the cases where some of them are missing.
class GeneralQuery(generics.GenericAPIView):
    serializer_class= MovieSerializer

    @csrf_exempt
    def get(self, request,):

        #   First we get the request information. If some data are missing 
        # we used the ternary operator to give a default value.
        year_min = request.data.get('year_min') if request.data.get('year_min') else 1950
        year_max = request.data.get('year_max') if request.data.get('year_max') else 2024
        rate_min = request.data.get('rate_min') if request.data.get('rate_min') else 6.8
        rate_max = request.data.get('rate_max') if request.data.get('rate_max') else 9
        requestGenres = request.data.get('genres', [])
        requestTypes = request.data.get('type', []) 

        #   First filter: using the default values to reduce the length of the total data.
        movies_filtered = Movie.objects.filter(avgRating__gte=rate_min, 
                                                      avgRating__lte=rate_max,
                                                      year__gte=year_min, 
                                                      year__lte=year_max)
        #   Second filter: it's done if the request has any 'type' to filter with.
        if ( len(requestTypes) > 0):
            movies_filtered = movies_filtered.filter(type__in=requestTypes)

        #   Third filter: if the request has any 'genre', we filter the 
        # genre data and then the movies_filtered using the genres id.
        if( len(requestGenres)>0):
            genreListName = Genre.objects.filter(name__in=requestGenres)
            tokenId = GenreToken.objects.filter(genre__in=genreListName).values_list('movie_id', flat=True).distinct()
            movies_filtered = movies_filtered.filter(id__in=tokenId)

        movies = movies_filtered.order_by('?')[:min(3, movies_filtered.count())]

        serializer = self.get_serializer(movies, many=True)

        if(len(serializer.data)== 0):
            return Response("There's no matches for that search.", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer,status=status.HTTP_200_OK)

