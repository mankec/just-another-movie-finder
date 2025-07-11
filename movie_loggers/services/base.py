from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

from django.contrib.sessions.models import Session


class MovieLogger(Enum):
    SIMKL = "Simkl"
    TRAKT = "Trakt"
    TMDB = "TMDB"


class AbstractMovieLogger(ABC):
    def __init__(self, session: Session):
        self.session = session
        name = session["movie_logger"]

    @abstractmethod
    def authorize_application_url(self, request_token: Optional[str] = None) -> str:
        ...

    @abstractmethod
    def fetch_tokens(self, *, code) -> str:
        ...

    @abstractmethod
    def add_to_watchlist(self, movie: dict):
        ...

    @abstractmethod
    def fetch_movie_remote_ids(self) -> dict:
        ...
