from django.contrib.sessions.models import Session

def is_signed_in(session: Session):
    return bool(session.get("token") and session.get("movie_logger"))
