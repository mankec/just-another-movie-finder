from http import HTTPMethod, HTTPStatus

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


class Simkl(AbstractMovieLogger):
    API_URL = "https://api.simkl.com"
    CLIENT_ID = env.str("SIMKL_CLIENT_ID", "")
    CLIENT_SECRET = env.str("SIMKL_CLIENT_SECRET", "")
    MOVIE_STATUS_PLANTOWATCH = "plantowatch"
    MOVIE_STATUS_COMPLETED = "completed"
    REQUIRED_HEADERS = {
        "simkl-api-key": CLIENT_ID,
    }

    def __init__(self, token):
        self.token = token
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
    def fetch_tokens(self, *, code) -> dict:
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
        return {
            "token": response_body["access_token"],
        }

    @handle_exception("Something went wrong.")
    def add_to_watchlist(self, movie: Movie) -> bool:
        try:
            url = build_url(self.API_URL, "sync/add-to-list")
            payload = {
                "movies": [
                    {
                        "to": self.MOVIE_STATUS_PLANTOWATCH,
                        "title": movie.title,
                        "year": movie.year,
                        "ids": {
                            "tvdb": movie.tvdb_id,
                            "imdb": movie.imdb_id,
                            "tmdb": movie.tmdb_id,
                        }
                    }
                ],
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
                message = f"Something went wrong while trying to add '{movie.title}' to Trakt's watchlist."
            raise HTTPError(message)

    @handle_exception
    def fetch_movie_remote_ids(self) -> dict:
        remote_ids = {
            "watched": {
                "tvdb_ids": [],
                "imdb_ids": [],
                "tmdb_ids": [],
            },
            "on_watchlist": {
                "tvdb_ids": [],
                "imdb_ids": [],
                "tmdb_ids": [],
            },
        }
        url = build_url(self.API_URL, "sync/all-items")
        payload = {
            "type": "movies",
        }
        response =  send_request(
            method=HTTPMethod.GET.value,
            url=url,
            payload=payload,
            headers=self._oauth_required_headers(),
        )
        response_body = response.json()
        if not response_body:
            return remote_ids
        movies = response_body["movies"]
        for d in movies:
            if d["status"] == self.MOVIE_STATUS_COMPLETED:
                if tvdb_id := d["movie"]["ids"].get("tvdb"):
                    remote_ids["watched"]["tvdb_ids"].append(tvdb_id)
                if imdb_id := d["movie"]["ids"].get("imdb"):
                    remote_ids["watched"]["imdb_ids"].append(imdb_id)
                if tmdb_id := d["movie"]["ids"].get("tmdb"):
                    remote_ids["watched"]["tmdb_ids"].append(tmdb_id)
            elif d["status"] == self.MOVIE_STATUS_PLANTOWATCH:
                if tvdb_id := d["movie"]["ids"].get("tvdb"):
                    remote_ids["on_watchlist"]["tvdb_ids"].append(tvdb_id)
                if imdb_id := d["movie"]["ids"].get("imdb"):
                    remote_ids["on_watchlist"]["imdb_ids"].append(imdb_id)
                if tmdb_id := d["movie"]["ids"].get("tmdb"):
                    remote_ids["on_watchlist"]["tmdb_ids"].append(tmdb_id)
        return remote_ids

    def _oauth_required_headers(self):
        if not self.token:
            raise ValueError(f"{self.name} token must be present for using this action.")
        return {
            **self.REQUIRED_HEADERS,
            'Authorization': f"Bearer {self.token}",
        }
