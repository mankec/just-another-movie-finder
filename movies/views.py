from environs import Env
from django.shortcuts import render, redirect
from django.contrib import messages

from project.wrappers import handle_exception
from project.auth.utils import is_signed_in
from movie_loggers.services.creator import MovieLogger, MovieLoggerCreator
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
def authorize_application(request, movie_logger):
    session = request.session
    session["movie_logger"] = movie_logger
    url = MovieLoggerCreator(session).authorize_application_url()
    return redirect(url)


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


@handle_exception
def sign_in(request):
    if is_signed_in(request.session):
        messages.error(request, "Already signed in.")
        return redirect("/")
    ctx = {
        "simkl": MovieLogger.SIMKL.value,
        "trakt": MovieLogger.TRAKT.value,
    }
    return render(request, "movies/sign_in.html", ctx)


@handle_exception
def sign_out(request):
    request.session.flush()
    messages.success(request, "Signed out.")
    return redirect("/")


def error(request):
    ctx = {
        "headerless": True
    }
    return render(request, "error.html", ctx)
