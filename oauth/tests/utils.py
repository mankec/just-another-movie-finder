from django.contrib.sessions.models import Session
from django.urls import reverse
from django.test import TestCase

from movie_loggers.tests.services.constants import DEFAULT_TEST_MOVIE_LOGGER


def sign_in_user(session: Session):
    session["movie_logger"] = DEFAULT_TEST_MOVIE_LOGGER
    session["token"] = "token"
    session.save()


# TODO: Perhaps change this to mixin? If you do, add also selenium_url that will prepend live_server_url to target url.
def selenium_sign_in_user(test_case: TestCase, movie_logger):
    url = reverse("oauth:selenium_sign_in", kwargs={
        "movie_logger": movie_logger,
    })
    test_case.selenium.get(f"{test_case.live_server_url}/{url}")
