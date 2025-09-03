from http import HTTPMethod, HTTPStatus
from enum import Enum

from environs import Env
from requests import Response
from requests.exceptions import HTTPError

from project.settings import API_REDIRECT_URL
from core.wrappers import handle_exception
from core.url.utils import build_url, build_url_with_query
from core.requests.utils import send_request
from movies.models import Movie
from movie_loggers.services.base import MovieLogger, AbstractMovieLogger

env = Env()


class TMDB(AbstractMovieLogger):
    API_URL = "https://api.themoviedb.org/3/"

    def __init__(self, token):
        self.token = token
        self.name = MovieLogger.TMDB.value

    @handle_exception("Something went wrong while trying to sign you in to TMDB.")
    def fetch_request_token(self):
        url = build_url(self.API_URL, "authentication/token/new")
        headers = {
            "Authorization": f"Bearer {env.str("TMDB_TOKEN", "")}",
        }
        response = send_request(
            method=HTTPMethod.GET.value,
            url=url,
            headers=headers,
        )
        response_body = response.json()
        return response_body["request_token"]

    @handle_exception("Something went wrong while trying to sign you in to TMDB.")
    def authorize_application_url(self, request_token) -> str:
        url = build_url("https://www.themoviedb.org/authenticate/", request_token)
        query = {
            "redirect_to": API_REDIRECT_URL,
        }
        return build_url_with_query(url, query)

    @handle_exception("Something went wrong while trying to sign you in to TMDB.")
    def fetch_tokens(self, *, code) -> dict:
        url = "https://api.themoviedb.org/3/authentication/session/new"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {env.str("TMDB_TOKEN", "")}",
        }
        payload = {
            "request_token": code,
        }
        response = send_request(
            method=HTTPMethod.POST.value,
            url=url,
            headers=headers,
            payload=payload,
        )
        response_body = response.json()
        return {
            "token": response_body["session_id"],
        }

    @handle_exception("Something went wrong.")
    def add_to_watchlist(self, movie: Movie) -> bool:
        try:
            url = build_url(self.API_URL, "account/null/watchlist")
            payload = {
                "media_type": "movie",
                "media_id": movie.id,
                "watchlist": True
            }
            headers = {
                "Authorization": f"Bearer {env.str("TMDB_TOKEN", "")}",
            }
            send_request(
                method=HTTPMethod.POST.value,
                url=url,
                headers=headers,
                payload=payload,
            )
            return True
        except HTTPError:
            message = f"Something went wrong while trying to add {movie.title} to your TMDB's watchlist."
            raise HTTPError(message)

    @handle_exception
    def fetch_movie_remote_ids(self) -> dict:
        page = 1
        total_pages = 1
        remote_ids = {
            "watched": {
                "imdb_ids": [],
                "tmdb_ids": [],
            },
            "on_watchlist": {
                "imdb_ids": [],
                "tmdb_ids": [],
            },
        }
        headers = {
            "Authorization": f"Bearer {env.str("TMDB_TOKEN", "")}",
        }
        while page <= total_pages:
            url = build_url(
                self.API_URL,
                f"account/null/watchlist/movies?language=en-US&page={page}"
            )
            response =  send_request(
                method=HTTPMethod.GET.value,
                url=url,
                headers=headers,
            )
            response_body = response.json()
            if not response_body:
                return remote_ids
            movies = response_body["results"]
            for d in movies:
                remote_ids["on_watchlist"]["tmdb_ids"].append(d["id"])
            total_pages = response_body["total_pages"]
            page += 1
        return remote_ids
