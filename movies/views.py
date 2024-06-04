from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from io import StringIO
from django.db import transaction
import pandas as pd
from movies.models import Movie, Genre, GenreToken
from rest_framework import generics
from rest_framework.response import Response
from .serializers import MovieSerializer
from random import sample

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the movies index.")

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
                        genre, created = Genre.objects.get_or_create(name= genre_name)
                        GenreToken.objects.get_or_create(movie=movie, genre = genre)

            return JsonResponse({"message": "CSV file successfully uploaded and processed"}, status = 200)

        except Exception as e:

            print(f"Error: {e}")

            return JsonResponse({"message": "There's been an error saving data."}, status= 500)
        
class RandomDataView(generics.GenericAPIView):
    serializer_class = MovieSerializer

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        total_count = Movie.objects.count()
        random_ids = sample(range(1,total_count+1), min(3, total_count))
        random_data = Movie.objects.filter(id__in = random_ids)
        serializer = self.get_serializer(random_data, many=True)

        return Response(serializer.data)