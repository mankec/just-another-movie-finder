from django.urls import path

from . import views

app_name = "movies"
urlpatterns = [
    # path("find-movies", views.index, name="index"),
    path("sign-in", views.sign_in, name="sign_in"),
]
