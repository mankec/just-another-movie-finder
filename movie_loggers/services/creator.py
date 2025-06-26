from django.contrib.sessions.models import Session

from movie_loggers.services.base import MovieLogger
from movie_loggers.services.simkl.services import Simkl
from movie_loggers.services.trakt.services import Trakt


class MovieLoggerCreator:
    def __new__(self, session: Session):
        match session["movie_logger"]:
            case MovieLogger.SIMKL.value:
                return Simkl(session)
            case MovieLogger.TRAKT.value:
                return Trakt(session)
            case _:
                raise ValueError("Unknown movie logger.")
