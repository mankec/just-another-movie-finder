import inspect
from unittest.mock import Mock, patch
from http import HTTPStatus
from typing import Literal

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from django.contrib.sessions.models import Session
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.test import TestCase

from movie_loggers.tests.services.constants import DEFAULT_TEST_MOVIE_LOGGER
from movies.forms.movie_finder.forms import MATCH_FILTERS_SOME
from movies.models import Country, Genre
from languages.constants import TVDB_SUPPORTED_LANGUAGES


def sign_in_user(session: Session):
    session["movie_logger"] = DEFAULT_TEST_MOVIE_LOGGER
    session["token"] = "token"
    session.save()


# TODO: Perhaps change this to mixin? If you do, add also selenium_url that will prepend live_server_url to target url.
def selenium_sign_in_user(test_case: TestCase, movie_logger):
    try:
        url = reverse("oauth:selenium_sign_in", kwargs={
            "movie_logger": movie_logger,
        })
        test_case.browser.get(f"{test_case.live_server_url}/{url}")
    except NoReverseMatch:
        test_case.fail("This URL is only available in test environment. Run `DJANGO_ENV=test python manage.py test` to be able to access it.")


def mock_response(response):
    if not isinstance(response, dict):
        # Response can be an exception
        return response
    mock_response = Mock()
    if status_code := response.get("status_code"):
        mock_response.status_code = status_code
    else:
        mock_response.status_code = HTTPStatus.OK.value
    if headers := response.get("headers"):
        mock_response.headers = headers
    mock_response.json.return_value = response["body"]
    return mock_response


def stub_request(klass_or_instance, *, response):
    if inspect.isclass(klass_or_instance):
        klass = klass_or_instance
    else:
        klass = klass_or_instance.__class__
    return patch(
        f"{klass.__module__}.send_request",
        return_value=mock_response(response),
    )


def stub_multiple_requests(klass_or_instance, *, responses: list):
    if inspect.isclass(klass_or_instance):
        klass = klass_or_instance
    else:
        klass = klass_or_instance.__class__
    return patch(
        f"{klass.__module__}.send_request",
        side_effect=map(mock_response, responses)
    )


def stub_request_exception(klass_or_instance, *, exception):
    if inspect.isclass(klass_or_instance):
        klass = klass_or_instance
    else:
        klass = klass_or_instance.__class__
    return patch(
        f"{klass.__module__}.send_request",
        side_effect=exception,
    )


def fill_and_submit_movie_finder_form(
    browser: WebDriver,
    *,
    countries=[],
    exclude_countries=[],
    languages=[],
    exclude_languages=[],
    genres=[],
    exclude_genres=[],
    year_from="",
    year_to="",
    runtime_min="",
    runtime_max="",
    match_filters: Literal["some", "all"] = MATCH_FILTERS_SOME,
):
    for c in countries:
        country = Country.objects.get(name=c)
        browser.find_element(By.ID, f"countries_{country.alpha_3}").click()
    for c in exclude_countries:
        country = Country.objects.get(name=c)
        browser.find_element(By.ID, f"exclude_countries_{country.alpha_3}").click()
    for l in languages:
        alpha_3 = next(
            k for k, v in TVDB_SUPPORTED_LANGUAGES.items()
            if v["name"] == l
        )
        browser.find_element(By.ID, f"languages_{alpha_3}").click()
    for l in exclude_languages:
        alpha_3 = next(
            k for k, v in TVDB_SUPPORTED_LANGUAGES.items()
            if v["name"] == l
        )
        browser.find_element(By.ID, f"exclude_languages_{alpha_3}").click()
    for g in genres:
        genre = Genre.objects.get(name=genre)
        browser.find_element(By.ID, f"genres_{genre.slug}").click()
    for g in exclude_genres:
        genre = Genre.objects.get(name=genre)
        browser.find_element(By.ID, f"exclude_genres_{genre.slug}").click()

    year_from_input = browser.find_element(By.NAME, "year_from")
    year_from_input.send_keys(year_from)
    year_to_input = browser.find_element(By.NAME, "year_to")
    year_to_input.send_keys(year_to)
    runtime_min_input = browser.find_element(By.NAME, "runtime_min")
    runtime_min_input.send_keys(runtime_min)
    runtime_max_input = browser.find_element(By.NAME, "runtime_max")
    runtime_max_input.send_keys(runtime_max)

    browser.find_element(By.ID, f"radio_button_{match_filters}").click()

    browser.find_element(By.XPATH, '//button[@type="submit"]').click()
