# TODO: Make a new app called auth and put this file there
from django.contrib.sessions.models import Session

def is_signed_in(session):
    return bool(session.get("token") and session.get("movie_logger"))
