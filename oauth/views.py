from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages

from core.wrappers import handle_exception
from core.environments.utils import is_test
from core.sessions.utils import is_signed_in
from movie_loggers.services.creator import MovieLogger, MovieLoggerCreator


@handle_exception
def index(request):
    session = request.session
    code = request.GET.get("code") or request.GET.get("request_token")

    if not code:
        session.clear()
        message = f"Failed to sign you in to {session["movie_logger"]}"
        messages.error(request, message)
        url = reverse("sign_in")
        return redirect(url)
    movie_logger = MovieLoggerCreator(session)
    result = movie_logger.fetch_tokens(code=code)
    session["token"] = result["token"]
    session["refresh_token"] = result.get("refresh_token", "")
    session["token_expires_at"] = result.get("token_expires_at", "")
    message = f"Successfully signed with {session["movie_logger"]}!"
    messages.success(request, message)
    return redirect("/")


@handle_exception
def authorize_application(request, movie_logger):
    session = request.session
    # TODO: Perhaps change to movie_logger_name. And change token back to access_token?
    session["movie_logger"] = movie_logger
    fetch_request_token = getattr(MovieLoggerCreator(session), "fetch_request_token", None)
    if callable(fetch_request_token):
        session["request_token"] = fetch_request_token()
    url = (
        MovieLoggerCreator(session)
            .authorize_application_url(session["request_token"])
    )
    return redirect(url)


@handle_exception
def sign_in(request):
    if is_signed_in(request.session):
        messages.error(request, "Already signed in.")
        return redirect("/")
    ctx = {
        "simkl": MovieLogger.SIMKL.value,
        "trakt": MovieLogger.TRAKT.value,
        "tmdb": MovieLogger.TMDB.value,
    }
    return render(request, "oauth/sign_in.html", ctx)


@handle_exception
def sign_out(request):
    request.session.flush()
    messages.success(request, "Signed out.")
    return redirect("/")


@handle_exception
def selenium_sign_in(request, movie_logger):
    # Session is already initialized here because of initialize_session middleware
    if not is_test():
        return redirect("/")
    session = request.session
    session["movie_logger"] = movie_logger
    session["token"] = "token"
    return redirect("/")
