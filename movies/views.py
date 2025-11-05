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
from core.url.utils import build_url_with_query
from movie_loggers.services.creator import MovieLoggerCreator
from movies.models import Movie
from movies.forms.movie_sort.forms import MovieSortForm
from movies.forms.movie_finder.forms import MovieFinderForm
from movies.services.movie_finder.services import MovieFinder
from core.sessions.utils import is_signed_in

env = Env()


@handle_exception
def index(request):
    order_by_map = {
        "oldest": "year",
        "newest": "-year",
        "most_popular": "-vote_average",
        "least_popular": "vote_average",
        "most_voted": "-vote_count",
        "least_voted": "vote_count",
        "longest": "-runtime",
        "shortest": "runtime",
    }
    session = request.session
    page_number = request.GET.get("page", 1)
    paginator = Paginator(session["filtered_movie_ids"], 24)
    page_obj = paginator.get_page(page_number)
    movie_ids = page_obj.object_list
    movie_sort_form = MovieSortForm()
    sorting_key = request.GET.get("sorting_key", movie_sort_form.DEFAULT_SORTING_KEY)
    movie_sort_form.initial["sorting_key"] = sorting_key
    movies = (
        Movie.objects
            .filter(id__in=movie_ids)
            .order_by(order_by_map[sorting_key])
    )
    watched_tmdb_ids = set(session["movie_remote_ids"]["watched"]["tmdb_ids"])
    watched_imdb_ids = set(session["movie_remote_ids"]["watched"]["imdb_ids"])
    on_watchlist_tmdb_ids = set(session["movie_remote_ids"]["on_watchlist"]["tmdb_ids"])
    on_watchlist_imdb_ids = set(session["movie_remote_ids"]["on_watchlist"]["imdb_ids"])
    movies_added_to_watchlist_ids = set(session["movies_added_to_watchlist_ids"])
    results = [
        {
            "movie": m,
            "watched": (
                m.id in watched_tmdb_ids or
                m.imdb_id in watched_imdb_ids
                if is_signed_in(session) else False
            ),
            "on_watchlist": (
                m.id in on_watchlist_tmdb_ids or
                m.imdb_id in on_watchlist_imdb_ids
                if is_signed_in(session) else False
            ),
            "added_to_watchlist": m.id in movies_added_to_watchlist_ids
        }
        for m in movies
    ]
    ctx = {
        "page_obj": page_obj,
        "movie_sort_form": MovieSortForm(initial={"sorting_key": sorting_key}),
        "movie_logger": session["movie_logger"].capitalize(),
        "results": results,
        "message_tags": {
            "success": MESSAGE_TAGS[messages.SUCCESS],
            "error": MESSAGE_TAGS[messages.ERROR],
        }
    }
    return render(request, "movies/index.html", ctx)


@handle_exception
def find(request):
    form = MovieFinderForm(request.GET)
    if form.is_valid():
        session = request.session
        session["filtered_movie_ids"] = MovieFinder(**form.cleaned_data).get_movie_ids()
        if is_signed_in(session):
            session["movie_remote_ids"] = MovieLoggerCreator(
                session
            ).fetch_movie_remote_ids()
        url = reverse("movies:index")
        return redirect(url)
    message = list(flatten(form.errors.values())).pop(0)
    messages.error(request, message)
    return redirect("/")


@handle_exception
def sort_by(request):
    form = MovieSortForm(request.GET)
    url = reverse("movies:index")
    if form.is_valid():
        url = build_url_with_query(url, {"sorting_key": form.cleaned_data["sorting_key"]})
        return redirect(url)
    message = list(flatten(form.errors.values())).pop(0)
    messages.error(request, message)
    return redirect(url)


@handle_exception
def add_to_watchlist(request, movie_id):
    movie = Movie.objects.get(pk=movie_id)
    session = request.session
    movie_logger = session["movie_logger"]
    MovieLoggerCreator(session).add_to_watchlist(movie)
    ids = session["movies_added_to_watchlist_ids"]
    ids.append(movie_id)
    session["movies_added_to_watchlist_ids"] = ids
    return JsonResponse({
        "status": HTTPStatus.OK.value,
        "message": f"'{movie.title}' has been added to {movie_logger}'s watchlist."
    })
