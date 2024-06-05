from django.urls import path 
from .views import save_csv, RandomDataView, QueryByRatingView, QueryByGenre

urlpatterns = [
    path("save_csv/", save_csv, name="save_csv"),
    path('three_random/', RandomDataView.as_view(), name='random-data'),
    path('rating/', QueryByRatingView.as_view(), name= 'query-by-rating'),
    path('genre/', QueryByGenre.as_view(), name='query-by-genre')
]