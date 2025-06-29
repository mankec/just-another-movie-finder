import inspect
from unittest.mock import Mock, patch
from http import HTTPStatus
from typing import Literal
from copy import deepcopy

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from django.contrib.sessions.models import Session
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.test import TestCase

from movie_loggers.tests.services.constants import DEFAULT_TEST_MOVIE_LOGGER
from movies.forms.movie_finder.forms import MATCH_FILTERS_SOME
from movies.models import Movie


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


def create_dummy_movie(original: Movie):
    num = Movie.objects.count() + 1
    new_movie = deepcopy(original)
    new_movie.tvdb_id = num
    new_movie.title = f"Dummy Movie {num}"
    new_movie.slug = f"dummy-movie-{num}"
    new_movie.save()
    return new_movie


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
    def _search_and_click(name, text):
        search_input = browser.find_element(By.ID, f"search_{name}")
        search_input.clear()
        search_input.send_keys(text)
        label = browser.find_element(
            By.XPATH, f"//ul[@id='{name}_list']/li[not(contains(@class, 'hidden'))]/div/label"
        )
        input_id = label.get_attribute("for")
        browser.find_element(By.ID, input_id).click()

    for country in countries:
        _search_and_click("countries", country)
    for country in exclude_countries:
        _search_and_click("exclude_countries", country)
    for language in languages:
        _search_and_click("languages", language)
    for language in exclude_languages:
        _search_and_click("exclude_languages", language)
    for genre in genres:
        _search_and_click("genres", genre)
    for genre in exclude_genres:
        _search_and_click("exclude_genres", genre)

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
