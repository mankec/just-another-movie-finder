from environs import Env
from django.shortcuts import render, redirect
from django.contrib import messages

from core.wrappers import handle_exception
from movie_loggers.services.creator import MovieLoggerCreator
from movies.models import Movie

env = Env()


@handle_exception
def index(request):
    return render(request, "movies/index.html")


@handle_exception
def add_to_watchlist(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    message = MovieLoggerCreator(request.session).add_to_watchlist(movie)
    messages.success(request, message)
    return redirect("/")
