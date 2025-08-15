from http import HTTPMethod, HTTPStatus

from environs import Env
from requests.exceptions import HTTPError
from requests import Response

from core.url.utils import build_url, build_url_with_query
from core.requests.utils import send_request
from core.constants import ONE_DAY_IN_SECONDS
from project.settings import API_REDIRECT_URL, USER_AGENT
from core.wrappers import handle_exception
from movie_loggers.services.base import AbstractMovieLogger, MovieLogger
from movies.models import Movie

env = Env()


class Trakt(AbstractMovieLogger):
    HTTP_STATUS_CODE_VIP_ENHANCED = 420
    VIP_UPGRADE_URL = "https://trakt.tv/vip"
    API_URL = "https://api.trakt.tv"
    CLIENT_ID = env.str("TRAKT_CLIENT_ID", "")
    CLIENT_SECRET = env.str("TRAKT_CLIENT_SECRET", "")
    REQUIRED_HEADERS = {
            "User-Agent": USER_AGENT,
            "trakt-api-key": CLIENT_ID,
            "trakt-api-version": "2",
    }
    PAGINATION_LIMIT = 100

    def __init__(self, token):
        self.token = token
        self.name = MovieLogger.TRAKT.value

    @handle_exception("Something went wrong while trying to sign you in to Trakt.")
    def authorize_application_url(self, request_token=None):
        url = "https://trakt.tv/oauth/authorize"
        query = {
            "response_type": "code",
            "client_id": self.CLIENT_ID,
            "redirect_uri": API_REDIRECT_URL,
        }
        return build_url_with_query(url, query)

    @handle_exception("Something went wrong while trying to sign you in to Trakt.")
    def fetch_tokens(self, *, code=None, refresh_token=None) -> dict:
        url = build_url(self.API_URL, "oauth/token")
        payload = {
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            "redirect_uri": API_REDIRECT_URL,
        }
        if code:
            payload["code"] = code
            payload["grant_type"] = "authorization_code"
        elif refresh_token:
            payload["refresh_token"] = refresh_token
            payload["grant_type"] = "refresh_token"
        else:
            raise ValueError("Either code or refresh token must be present")
        response = send_request(
            method=HTTPMethod.POST.value,
            url=url,
            headers=self.REQUIRED_HEADERS,
            payload=payload,
        )
        response_body = response.json()
        return {
            "token": response_body["access_token"],
            "refresh_token": response_body["refresh_token"],
            "token_expires_at": response_body["created_at"] + ONE_DAY_IN_SECONDS,
        }

    @handle_exception("Something went wrong.")
    def add_to_watchlist(self, movie: Movie) -> bool:
        try:
            url = build_url(self.API_URL, "sync/watchlist")
            payload = {
                "movies": [
                    {
                        "title": movie.title,
                        "year": movie.year,
                        "ids": {
                            "slug": movie.slug,
                            "tmdb": movie.id,
                            "imdb": movie.imdb_id,
                        },
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
            if response.status_code == HTTPStatus.NOT_FOUND.value:
                message = f"Trakt couldn't find '{movie.title}'."
            else:
                message = self._resolve_http_exception_message(response)
            if not message:
                message = f"Something went wrong while trying to add {movie.title} to your Trakt's watchlist."
            raise HTTPError(message)

    @handle_exception
    def fetch_movie_remote_ids(self) -> dict:
        watched = self._fetch_watched_movies_remote_ids()
        on_watchlist =  self._fetch_movies_on_watchlist_remote_ids()
        return {
            "watched": watched,
            "on_watchlist": on_watchlist,
        }

    @handle_exception
    def _fetch_watched_movies_remote_ids(self) -> dict:
        remote_ids = {
            "imdb_ids": [],
            "tmdb_ids": [],
        }
        url = build_url(self.API_URL, "sync/watched/movies")
        response =  send_request(
            method=HTTPMethod.GET.value,
            url=url,
            headers=self._oauth_required_headers(),
        )
        response_body = response.json()
        if not response_body:
            return remote_ids
        for d in response_body:
            if imdb_id := d["movie"]["ids"].get("imdb"):
                remote_ids["imdb_ids"].append(imdb_id)
            if tmdb_id := d["movie"]["ids"].get("tmdb"):
                remote_ids["tmdb_ids"].append(tmdb_id)
        return remote_ids

    @handle_exception
    def _fetch_movies_on_watchlist_remote_ids(self) -> dict:
        page = 1
        total_pages = 1
        remote_ids = {
            "imdb_ids": [],
            "tmdb_ids": [],
        }
        while page <= total_pages:
            url = build_url(self.API_URL, "sync/watchlist/movies")
            payload = {
                "page": page,
                "limit": self.PAGINATION_LIMIT
            }
            response =  send_request(
                method=HTTPMethod.GET.value,
                url=url,
                payload=payload,
                headers=self._oauth_required_headers(),
            )
            total_pages = int(response.headers["X-Pagination-Page-Count"])
            response_body = response.json()
            if not response_body:
                break
            for d in response_body:
                if imdb_id := d["movie"]["ids"].get("imdb"):
                    remote_ids["imdb_ids"].append(imdb_id)
                if tmdb_id := d["movie"]["ids"].get("tmdb"):
                    remote_ids["tmdb_ids"].append(tmdb_id)
            page += 1
        return remote_ids

    def _resolve_http_exception_message(self, response):
        if response.status_code == HTTPStatus.LOCKED.value:
            is_accound_locked = response.headers["X-Account-Locked"] == "true"
            is_account_deactivated = response.headers["X-Account-Deactivated"] == "true"
            if is_accound_locked:
                return "Your Trakt account is locked. Please contact their support at support@trakt.tv."
            elif is_account_deactivated:
                return "Your Trakt account is deactivated. Please contact their support at support@trakt.tv."
        elif response.status_code == self.HTTP_STATUS_CODE_VIP_ENHANCED:
            is_account_vip = response.headers["X-VIP-User"] == "true"

            if is_account_vip:
                return "You have reached limit for your Trakt account."
            else:
                return response.headers["X-Upgrade-URL"]

    def _oauth_required_headers(self):
        if not self.token:
            raise ValueError(f"{self.name} token must be present for using this action.")
        return {
            **self.REQUIRED_HEADERS,
            "Authorization": f"Bearer {self.token}",
        }
