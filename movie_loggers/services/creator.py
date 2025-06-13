from django.contrib.sessions.models import Session

from movie_loggers.services.base import MovieLogger
from movie_loggers.services.simkl import Simkl


class MovieLoggerCreator:
    def __new__(self, session: Session):
        match session["movie_logger"]:
            case MovieLogger.SIMKL.value:
                return Simkl(session)
