from django.contrib.sessions.models import Session

from movie_loggers.services.base import MovieLogger
from movie_loggers.services.simkl.services import Simkl
from movie_loggers.services.trakt.services import Trakt


class MovieLoggerCreator:
    def __new__(self, session: Session):
        token = session["token"]
        match session["movie_logger"]:
            case MovieLogger.SIMKL.value:
                return Simkl(token)
            case MovieLogger.TRAKT.value:
                return Trakt(token)
            case _:
                raise ValueError("Unknown movie logger.")
