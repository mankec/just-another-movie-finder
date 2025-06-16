from django.shortcuts import redirect, render
from django.contrib import messages

from project.wrappers import handle_exception
from movie_loggers.services.creator import MovieLoggerCreator


@handle_exception
def authorize_application(request, movie_logger):
    session = request.session
    session["movie_logger"] = movie_logger
    url = MovieLoggerCreator(session).authorize_application_url()
    return redirect(url)


@handle_exception
def index(request):
    session = request.session
    code = request.GET["code"]

    if not code:
        session.clear()
        message = f"Failed to sign you in to {session["movie_logger"].capitalize()}"
        messages.error(request, message)
        return redirect("sign_in")
    movie_logger = MovieLoggerCreator(session)
    movie_logger.obtain_token(code=code)
    message = f"Successfully signed with {session["movie_logger"].capitalize()}!"
    messages.success(request, message)
    return redirect("/")
