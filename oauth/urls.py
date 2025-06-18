from django.urls import path

from . import views

app_name = "oauth"
urlpatterns = [
    path("", views.index, name="index"),
    path("<str:movie_logger>/authorize-application",
        views.authorize_application,
        name="authorize_application",
    ),
]
