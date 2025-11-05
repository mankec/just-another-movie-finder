import inspect
from unittest.mock import Mock, patch
from http import HTTPStatus
from typing import Literal
from copy import deepcopy

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from django.contrib.sessions.models import Session

from movie_loggers.tests.services.constants import DEFAULT_TEST_MOVIE_LOGGER
from movies.models import Movie


def sign_in_user(session: Session):
    session["movie_logger"] = DEFAULT_TEST_MOVIE_LOGGER
    session["token"] = "token"
    session.save()


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


def stub_requests(klass_or_instance, *, responses: list):
    if inspect.isclass(klass_or_instance):
        klass = klass_or_instance
    else:
        klass = klass_or_instance.__class__
    return patch(
        f"{klass.__module__}.send_request",
        side_effect=map(mock_response, responses)
    )


def create_dummy_movie():
    original = Movie.objects.get(id=1)
    num = Movie.objects.count() + 1
    new_movie = deepcopy(original)
    new_movie.id = num
    new_movie.original_title = f"Dummy Movie {num}"
    new_movie.title = f"Dummy Movie {num}"
    new_movie.slug = f"dummy-movie-{num}"
    new_movie.imdb_id = f"imdb{num}"
    new_movie.save()
    return new_movie


# TODO: Perhaps move to core/tests/system/utils.py
def fill_and_submit_movie_finder_form(
    browser: WebDriver,
    *,
    country="",
    language="",
    genres=[],
    exclude_genres=[],
    year_from="",
    year_to="",
    runtime_min="",
    runtime_max="",
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

    if country:
        country_select = Select(browser.find_element(By.NAME, 'country'))
        country_select.select_by_visible_text(country)
    if language:
        language_select = Select(browser.find_element(By.NAME, 'language'))
        language_select.select_by_visible_text(language)
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

    browser.find_element(By.XPATH, '//button[@type="submit"]').click()
