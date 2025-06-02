from abc import ABC, abstractmethod
from enum import Enum

from django.contrib.sessions.models import Session


class MovieLogger(Enum):
    SIMKL = "simkl"
    TRAKT = "trakt"


class AbstractMovieLogger(ABC):
    def __init__(self, session: Session):
        self.session = session
        name = session["movie_logger"]

    @abstractmethod
    def authorize_application_url(self) -> str:
        ...

    @abstractmethod
    def obtain_token(self, *, code) -> str:
        ...

    @abstractmethod
    def add_to_watchlist(self, movie: dict):
        ...
