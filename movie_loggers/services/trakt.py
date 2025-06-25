from http import HTTPMethod, HTTPStatus

from environs import Env
from requests.exceptions import HTTPError
from requests import Response
from django.contrib.sessions.models import Session

from core.url.utils import build_url, build_url_with_query
from core.request.utils import send_request
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

    def __init__(self, session: Session):
        self.session = session
        self.name = MovieLogger.TRAKT.value

    @handle_exception("Something went wrong while trying to sign you in to Trakt.")
    def authorize_application_url(self):
        url = "https://trakt.tv/oauth/authorize"
        query = {
            "response_type": "code",
            "client_id": self.CLIENT_ID,
            "redirect_uri": API_REDIRECT_URL,
        }
        return build_url_with_query(url, query)

    @handle_exception("Something went wrong while trying to sign you in to Trakt.")
    def obtain_token(self, *, code=None, refresh_token=None):
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
        self.session["token"] = response_body["access_token"]
        self.session["refresh_token"] = response_body["refresh_token"]
        self.session["token_expires_at"] = response_body["created_at"] + ONE_DAY_IN_SECONDS
        return True

    @handle_exception("Something went wrong.")
    def add_to_watchlist(self, movie: Movie) -> bool:
        try:
            url = build_url(self.API_URL, "sync/watchlist")
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
            if response.status_code == HTTPStatus.NOT_FOUND.value:
                message = f"Trakt couldn't find '{movie.title}'."
            else:
                message = self._resolve_http_exception_message(response)
            if not message:
                message = f"Something went wrong while trying to add {movie.title} to your Trakt's watchlist."
            raise HTTPError(message)

    @handle_exception
    def fetch_movie_ids_in_watchlist(self) -> list:
        page = 1
        limit = self.PAGINATION_LIMIT
        total_pages = 1
        movie_ids = []
        while page <= total_pages:
            url = build_url(self.API_URL, "sync/watchlist/movies")
            payload = {
                "type": "movies",
                "page": page,
                "limit": limit
            }
            response =  send_request(
                method=HTTPMethod.GET.value,
                url=url,
                payload=payload,
                headers=self._oauth_required_headers(),
            )
            total_pages = int(response.headers["X-Pagination-Page-Count"])
            response_body = response.json()
            ids = [
                {
                    "imdb_id": d["movie"]["ids"]["imdb"],
                    "tmdb_id": d["movie"]["ids"]["tmdb"]
                }
                for d in response_body
            ]
            movie_ids.extend(ids)
            page += 1
        return movie_ids

    def _movie_data(self, movie: Movie) -> dict:
        return {
            "title": movie.title,
            "year": movie.year,
            "ids": {
                "slug": movie.slug,
                "imdb": movie.imdb_id,
                "tmdb": movie.tmdb_id
            },
            # TODO: This could be a neat feature. It's only allowed for VIPs
            # "notes": "One of Chritian Bale's most iconic roles."
        }

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
        if not (token := self.session["token"]):
            raise ValueError("Token must be present for using this action.")
        return {
            **self.REQUIRED_HEADERS,
            "Authorization": f"Bearer {token}",
        }
