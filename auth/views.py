from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages

from project.wrappers import handle_exception
from auth.utils import is_signed_in
from movie_loggers.services.creator import MovieLogger, MovieLoggerCreator


@handle_exception
def index(request):
    session = request.session
    code = request.GET["code"]

    if not code:
        session.clear()
        message = f"Failed to sign you in to {session["movie_logger"].capitalize()}"
        messages.error(request, message)
        url = reverse("sign_in")
        return redirect(url)
    movie_logger = MovieLoggerCreator(session)
    movie_logger.obtain_token(code=code)
    message = f"Successfully signed with {session["movie_logger"].capitalize()}!"
    messages.success(request, message)
    return redirect("/")


@handle_exception
def authorize_application(request, movie_logger):
    session = request.session
    session["movie_logger"] = movie_logger
    url = MovieLoggerCreator(session).authorize_application_url()
    return redirect(url)


@handle_exception
def sign_in(request):
    if is_signed_in(request.session):
        messages.error(request, "Already signed in.")
        return redirect("/")
    ctx = {
        "simkl": MovieLogger.SIMKL.value,
        "trakt": MovieLogger.TRAKT.value,
    }
    return render(request, "auth/sign_in.html", ctx)


@handle_exception
def sign_out(request):
    request.session.flush()
    messages.success(request, "Signed out.")
    return redirect("/")
