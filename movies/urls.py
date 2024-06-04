from django.urls import path 
from .views import save_csv, RandomDataView

urlpatterns = [
    path("save_csv", save_csv, name="save_csv"),
    path('three_random', RandomDataView.as_view(), name='random-data')
]