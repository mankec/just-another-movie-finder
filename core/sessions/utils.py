from django.contrib.sessions.models import Session

from core.sessions.constants import DEFAULT_SESSION_DATA


def initialize_session(session: Session):
    for k, v in DEFAULT_SESSION_DATA.items():
        session[k] = v


def is_signed_in(session: Session):
    return bool(session["token"] and session["movie_logger"])
