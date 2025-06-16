from django.urls import path

from . import views

app_name = "movies"
urlpatterns = [
    path("<int:movie_id>/add-to-watchlist", views.add_to_watchlist, name="add_to_watchlist"),
]
