from django.urls import path

from . import views


app_name = "movies"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:movie_id>/add-to-watchlist", views.add_to_watchlist, name="add_to_watchlist"),
    path("find", views.find, name="find"),
    path("<int:movie_id>", views.detail, name="detail")
]
