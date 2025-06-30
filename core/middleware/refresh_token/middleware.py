from time import time as unix_time
from movie_loggers.services.creator import MovieLoggerCreator

class RefreshTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session = request.session
        refresh_token = session["refresh_token"]
        if refresh_token and session["token_expires_at"] <= int(unix_time()):
            result = MovieLoggerCreator(session).fetch_tokens(refresh_token=refresh_token)
            session["token"] = result["token"]
            session["refresh_token"] = result["refresh_token"]
            session["token_expires_at"] = result["token_expires_at"]
        response = self.get_response(request)
        return response
