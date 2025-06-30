from http import HTTPStatus

from environs import Env
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from project.settings import MESSAGE_TAGS
from core.wrappers import handle_exception
from core.utils import flatten
from movie_loggers.services.creator import MovieLoggerCreator
from movies.models import Movie
from movies.forms.movie_finder.forms import MovieFinderForm
from movies.services.movie_finder.services import MovieFinder

env = Env()


@handle_exception
def index(request):
    session = request.session
    page_number = request.GET.get("page", 1)
    paginator = Paginator(session["movie_ids"], 5)
    page_obj = paginator.get_page(page_number)
    movie_ids = paginator.page(page_number).object_list
    movies = Movie.objects.filter(tvdb_id__in=movie_ids)
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


def find(request):
    form = MovieFinderForm(request.GET)
    if form.is_valid():
        request.session["movie_ids"] = MovieFinder(**form.cleaned_data).perform()
        url = reverse("movies:index")
        return redirect(url)
    message = list(flatten(form.errors.values())).pop(0)
    messages.error(request, message)
    return redirect("/")


@handle_exception
def add_to_watchlist(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    session = request.session
    movie_logger = session["movie_logger"]
    MovieLoggerCreator(session).add_to_watchlist(movie)
    return JsonResponse({
        "status": HTTPStatus.OK.value,
        "message": f"'{movie.title}' has been added to {movie_logger}'s watchlist."
    })
