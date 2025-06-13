from environs import Env
from django.shortcuts import render, redirect
from django.contrib import messages

from project.utils.session_utils import is_signed_in
from movie_loggers.services.creator import MovieLogger, MovieLoggerCreator

env = Env()

def index(request):
    context = {
        "token": request.session.get("token", ""),
        "movie_logger": request.session.get("movie_logger", ""),
    }
    return render(request, "movies/index.html", context)


def add_to_watchlist(request, movie_id):
    request.session["movie_logger"] = "simkl"
    MovieLoggerCreator(request.session).add_to_watchlist(movie_id)
    return redirect("index")


def authorize_application(request, movie_logger):
    request.session["token"] = ""
    request.session["movie_logger"] = movie_logger
    url = MovieLoggerCreator(request.session).authorize_application_url()
    return redirect(url)


def auth(request):
    request.session["token"] = ""
    code = request.GET["code"]

    if code:
        try:
            message = MovieLoggerCreator(request.session).obtain_token(code=code)
        except Exception as error:
            messages.error(request, error)
            return redirect("sign_in")
    messages.success(request, message)
    return redirect("index")


def sign_in(request):
    if is_signed_in(request.session):
        messages.error(request, "Already signed in.")
        return redirect("/")
    ctx = {
        "simkl": MovieLogger.SIMKL.value,
    }
    return render(request, "movies/sign_in.html", ctx)


def sign_out(request):
    request.session["token"] = ""
    request.session["movie_logger"] = ""
    messages.success(request, "Signed out.")
    return redirect("index")


def error(request):
    ctx = {
        "headerless": True
    }
    return render(request, "error.html", ctx)
