from environs import Env
from django.shortcuts import render, redirect
from django.contrib import messages

from movie_loggers.services.creator import MovieLoggerCreator

env = Env()

def index(request):
    context = {
        "token": request.session.get("token", ""),
        "movie_logger_name": request.session.get("movie_logger_name", ""),
    }
    return render(request, "movies/index.html", context)


def add_to_watchlist(request, movie_id):
    request.session["movie_logger_name"] = "simkl"
    MovieLoggerCreator(request.session).add_to_watchlist(movie_id)
    return redirect("index")


def authorize_application(request, movie_logger_name):
    request.session["token"] = ""
    request.session["movie_logger_name"] = movie_logger_name
    url = MovieLoggerCreator(request.session).authorize_application_url()
    return redirect(url)


def auth(request):
    request.session["token"] = ""
    code = request.GET["code"]

    if code:
        try:
            message = MovieLoggerCreator(request.session).exchange_code_and_save_token(code)
        except Exception as error:
            messages.error(request, error)
            return redirect("sign_in")
    messages.success(request, message)
    return redirect("index")


def sign_in(request):
    return render(request, "movies/sign_in.html")


def sign_out(request):
    request.session["token"] = ""
    request.session["movie_logger_name"] = ""
    messages.success(request, "Signed out.")
    return redirect("index")
