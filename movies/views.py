from http import HTTPStatus

from environs import Env
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from project.settings import MESSAGE_TAGS
from core.wrappers import handle_exception
from movie_loggers.services.creator import MovieLoggerCreator
from movies.models import Movie

env = Env()


@handle_exception
def index(request):
    movies = Movie.objects.all()[:50]
    paginator = Paginator(movies, 5)
    page_number = request.GET.get("page", 4)
    page_obj = paginator.get_page(page_number)
    ctx = {
        "page_obj": page_obj,
        "movie_logger": request.session["movie_logger"].capitalize(),
        "movies": movies,
        "message_tags": {
            "success": MESSAGE_TAGS[messages.SUCCESS],
            "error": MESSAGE_TAGS[messages.ERROR],
        }
    }
    return render(request, "movies/index.html", ctx)


@handle_exception
def add_to_watchlist(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    movie_logger = request.session["movie_logger"].capitalize()
    MovieLoggerCreator(request.session).add_to_watchlist(movie)
    return JsonResponse({
        "status": HTTPStatus.OK.value,
        "message": f"'{movie.title}' has been added to {movie_logger}'s watchlist."
    })
