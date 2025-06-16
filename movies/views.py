from environs import Env
from django.shortcuts import render, redirect
from django.contrib import messages

from project.wrappers import handle_exception
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


@handle_exception
def auth(request):
    session = request.session
    code = request.GET["code"]

    if not code:
        session.clear()
        message = f"Failed to sign you in to {session["movie_logger"].capitalize()}"
        messages.error(request, message)
        return redirect("sign_in")
    movie_logger = MovieLoggerCreator(session)
    movie_logger.obtain_token(code=code)
    message = "Successfully signed with Trakt!"
    messages.success(request, message)
    return redirect("/")


def error(request):
    ctx = {
        "headerless": True
    }
    return render(request, "error.html", ctx)
