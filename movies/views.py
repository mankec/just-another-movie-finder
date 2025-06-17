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
    movie_logger = request.session["movie_logger"].capitalize()
    MovieLoggerCreator(request.session).add_to_watchlist(movie)
    message = f"'{movie.title}' has been added to your {movie_logger}'s watchlist."
    messages.success(request, message)
    return redirect("/")
