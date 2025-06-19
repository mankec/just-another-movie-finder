from http import HTTPStatus

from environs import Env
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse

from project.settings import MESSAGE_TAGS
from core.wrappers import handle_exception
from movie_loggers.services.creator import MovieLoggerCreator
from movies.models import Movie

env = Env()


@handle_exception
def index(request):
    movies = Movie.objects.all()[:10]
    ctx = {
        "movie_logger": request.session["movie_logger"].capitalize(),
        "movies": movies,
        "message_tags": {
            "success": MESSAGE_TAGS[messages.SUCCESS],
            "error": MESSAGE_TAGS[messages.ERROR],
        }
    }
    return render(request, "movies/index.html", ctx)


def add_to_watchlist(request, movie_id):
    try:
        movie = Movie.objects.get(pk=movie_id)
        MovieLoggerCreator(request.session).add_to_watchlist(movie)
        return JsonResponse({"status": HTTPStatus.OK.value})
    except Exception:
        return JsonResponse({"status": HTTPStatus.INTERNAL_SERVER_ERROR.value})
