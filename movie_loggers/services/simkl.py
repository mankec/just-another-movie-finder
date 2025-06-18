from http import HTTPMethod, HTTPStatus

from environs import Env
from requests import Response
from requests.exceptions import HTTPError
from django.contrib.sessions.models import Session

from project.settings import API_REDIRECT_URL
from core.wrappers import handle_exception
from core.url.utils import build_url, build_url_with_query
from core.request.utils import send_request
from movies.models import Movie
from movie_loggers.services.base import MovieLogger, AbstractMovieLogger

env = Env()


class Simkl(AbstractMovieLogger):
    API_URL = "https://api.simkl.com"
    CLIENT_ID = env.str("SIMKL_CLIENT_ID", "")
    CLIENT_SECRET = env.str("SIMKL_CLIENT_SECRET", "")
    MOVIE_STATUS_PLANTOWATCH = "plantowatch"
    REQUIRED_HEADERS = {
        "simkl-api-key": CLIENT_ID,
    }

    def __init__(self, session: Session):
        self.session = session
        self.name = MovieLogger.SIMKL.value

    @handle_exception("Something went wrong while trying to sign you in to Simkl.")
    def authorize_application_url(self) -> str:
        url = "https://simkl.com/oauth/authorize"
        query = {
            "response_type": "code",
            "client_id": self.CLIENT_ID,
            "redirect_uri": API_REDIRECT_URL,
            "movie_logger": self.name
        }
        return build_url_with_query(url, query)

    @handle_exception("Something went wrong while trying to sign you in to Simkl.")
    def obtain_token(self, *, code) -> bool:
        url = build_url(self.API_URL, "oauth/token")
        payload = {
            "code": code,
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "redirect_uri": API_REDIRECT_URL,
            "grant_type": "authorization_code",
        }
        response = send_request(
            method=HTTPMethod.POST.value,
            url=url,
            payload=payload,
        )
        response_body = response.json()
        self.session["token"] = response_body["access_token"]
        return True

    @handle_exception("Something went wrong.")
    def add_to_watchlist(self, movie: Movie) -> bool:
        try:
            url = build_url(self.API_URL, "sync/add-to-list")
            payload = {
                "movies": [self._movie_data(movie)],
            }
            response = send_request(
                method=HTTPMethod.POST.value,
                url=url,
                headers=self._oauth_required_headers(),
                payload=payload,
            )
            response_body = response.json()
            if response_body["not_found"]["movies"]:
                response = Response()
                response.status_code = HTTPStatus.NOT_FOUND
                raise HTTPError(response=response)
            return True
        except HTTPError as error:
            response = error.response
            if response.status_code == HTTPStatus.NOT_FOUND:
                message = f"Simkl couldn't find '{movie.title}'."
            else:
                message = f"Someting went wrong while trying to add '{movie.title}' to your Trakt's watchlist."
            raise HTTPError(message)

    @handle_exception
    def fetch_movie_ids_in_watchlist(self) -> list:
        movie_ids = []
        url = build_url(self.API_URL, "sync/all-items")
        payload = {
            "type": "movies",
            "status": self.MOVIE_STATUS_PLANTOWATCH,
            "extended": "ids_only",
        }
        response =  send_request(
            method=HTTPMethod.GET.value,
            url=url,
            payload=payload,
            headers=self._oauth_required_headers(),
        )
        response_body = response.json()
        if not response_body:
            return []
        movies = response_body["movies"]
        movie_ids = [
            {
                "imdb_id": d["movie"]["ids"]["imdb"],
                "tmdb_id": d["movie"]["ids"]["tmdb"]
            }
            for d in movies
        ]
        return movie_ids

    def _movie_data(self, movie: Movie) -> dict:
        return {
            "to": self.MOVIE_STATUS_PLANTOWATCH,
            "title": movie.title,
            "year": movie.year,
            "ids": {
                "tvdb": movie.tvdb_id,
                "imdb": movie.imdb_id,
                "tmdb": movie.tmdb_id,
            }
        }

    def _oauth_required_headers(self):
        return {
            **self.REQUIRED_HEADERS,
            'Authorization': f"Bearer {self.session["token"]}",
        }
