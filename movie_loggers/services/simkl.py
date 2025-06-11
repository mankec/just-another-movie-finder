from http import HTTPMethod

from environs import Env
from django.contrib.sessions.models import Session

from project.utils.url_utils import build_url, build_url_with_query
from project.utils.request_utils import send_request
from movie_loggers.services.base import MovieLoggerProtocol

env = Env()


class Simkl(MovieLoggerProtocol):
    def __init__(self, session: Session):
        self.session = session
        self.name = session["movie_logger"]
        self.api_url = "https://api.simkl.com"
        self.client_id = env.str("SIMKL_CLIENT_ID", "")
        self.client_secret = env.str("SIMKL_CLIENT_SECRET", "")
        self.redirect_uri = "http://localhost:8000/movies/auth"

    def authorize_application_url(self):
        url = "https://simkl.com/oauth/authorize"
        query = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "movie_logger": self.name
        }
        return build_url_with_query(url, query)

    def exchange_code_and_save_token(self, code):
        url = build_url(self.api_url, "oauth/token")
        payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        try:
            response = send_request(
                method=HTTPMethod.POST.name,
                url=url,
                payload=payload,
            )
            response_body = response.json()
        except Exception:
            raise Exception("Something went wrong while trying to sign you in.")
        self.session["token"] = response_body["access_token"]
        return "Successfully signed to Simkl!"

    def add_to_watchlist(self, movie):
        movie_data = self._fetch_movie(movie)

        if not movie_data: return

        movie_data["to"] = "plantowatch"
        movie_data["ids"]["tvdb"] = movie["id"]

        url = build_url(self.api_url, "sync/add-to-list")
        headers = {
            'Authorization': f"Bearer {self.session["token"]}",
            'simkl-api-key': self.client_id
        }
        payload = {
            "movies": [movie_data],
        }
        response = send_request(
            method=HTTPMethod.POST.name,
            url=url,
            headers=headers,
            payload=payload,
        )

    def _fetch_movie(self, movie: dict) -> dict:
        url = build_url(self.api_url, "search/id")
        payload = {
            # "tvdb": tvdb_id(movie["id"], movie["title"]),
            "title": movie["title"],
            "year": movie["year"],
            "client_id": self.client_id,
        }
        response = send_request(
            method=HTTPMethod.GET.name,
            url=url,
            payload=payload,
        )
        data = response.json()

        if not data: return

        if len(data) > 1:
            # TODO:
            # This should never happen but if it does we must catch it and then fix it.
            # Set up email service that will notify us in case this happens.
            raise RuntimeError(
                "Only one movie must be retrieved: Simkl API, search/id"
            )
        return data.pop()
