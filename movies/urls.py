from django.urls import path

from . import views

app_name = "movies"
urlpatterns = [
    path("auth", views.auth, name="auth"),
    path("{<str:movie_logger>/authorize-application",
        views.authorize_application,
        name="authorize_application"
    ),
    path("<int:movie_id>/add-to-watchlist", views.add_to_watchlist, name="add_to_watchlist"),
]
