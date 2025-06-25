from django.contrib.sessions.models import Session


def is_signed_in(session: Session):
    return bool(session["token"] and session["movie_logger"])
