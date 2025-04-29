from django.contrib.sessions.models import Session

from movie_loggers.services.simkl import Simkl


class MovieLoggerCreator:
    def __new__(self, session: Session):
        match session["movie_logger_name"]:
            case "simkl":
                return Simkl(session)
