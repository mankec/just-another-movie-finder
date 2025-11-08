from django.test import TestCase, Client
from django.urls import reverse

from core.tests.mixins import CustomAssertionsMixin
from core.tests.utils import create_dummy_movie
from core.url.utils import build_url_with_query
from core.sessions.utils import initialize_session
from core.constants import DEFAULT_YEAR
from movies.models import Movie


class MovieSortFormIntegrationTestCase(TestCase, CustomAssertionsMixin):
    fixtures = ["movies.json", "genres.json"]

    def setUp(self):
        self.client = Client()
        self.sort_by_url = reverse("movies:sort_by")
        self.movies_url = reverse("movies:index")
        self.movie_1 = Movie.objects.get(pk=1)
        self.movie_2 = create_dummy_movie()
        self.movie_3 = create_dummy_movie()
        self.expected = [self.movie_1, self.movie_2, self.movie_3]

        session = self.client.session
        initialize_session(session)
        session["filtered_movie_ids"] = [self.movie_1.id, self.movie_2.id, self.movie_3.id]
        session.save()

    def _send_request_and_assert_redirect(self: TestCase, *, sorting_key):
        params = {"sorting_key": sorting_key}
        response = self.client.get(self.sort_by_url, data=params, follow=True)
        url = build_url_with_query(self.movies_url, {"sorting_key": sorting_key})
        self.assertRedirects(response, url)
        return response

    def test_sort_by_oldest(self):
        self.movie_1.year = DEFAULT_YEAR
        self.movie_2.year = DEFAULT_YEAR + 1
        self.movie_3.year = DEFAULT_YEAR + 2
        Movie.objects.bulk_update(Movie.objects.all(), ["year"])

        response = self._send_request_and_assert_redirect(sorting_key="oldest")
        movies = [r["movie"] for r in response.context["results"]]
        self.assertEqual(movies, self.expected)

    def test_sort_by_newest(self):
        self.movie_1.year = DEFAULT_YEAR
        self.movie_2.year = DEFAULT_YEAR - 1
        self.movie_3.year = DEFAULT_YEAR - 2
        Movie.objects.bulk_update(Movie.objects.all(), ["year"])

        response = self._send_request_and_assert_redirect(sorting_key="newest")
        movies = [r["movie"] for r in response.context["results"]]
        self.assertEqual(movies, self.expected)

    def test_sort_by_most_popular(self):
        self.movie_1.vote_average = 3
        self.movie_2.vote_average = 2
        self.movie_3.vote_average = 1
        Movie.objects.bulk_update(Movie.objects.all(), ["vote_average"])

        response = self._send_request_and_assert_redirect(sorting_key="most_popular")
        movies = [r["movie"] for r in response.context["results"]]
        self.assertEqual(movies, self.expected)

    def test_sort_by_least_popular(self):
        self.movie_1.vote_average = 1
        self.movie_2.vote_average = 2
        self.movie_3.vote_average = 3
        Movie.objects.bulk_update(Movie.objects.all(), ["vote_average"])

        response = self._send_request_and_assert_redirect(sorting_key="least_popular")
        movies = [r["movie"] for r in response.context["results"]]
        self.assertEqual(movies, self.expected)

    def test_sort_by_most_voted(self):
        self.movie_1.vote_count = 3
        self.movie_2.vote_count = 2
        self.movie_3.vote_count = 1
        Movie.objects.bulk_update(Movie.objects.all(), ["vote_count"])

        response = self._send_request_and_assert_redirect(sorting_key="most_voted")
        movies = [r["movie"] for r in response.context["results"]]
        self.assertEqual(movies, self.expected)

    def test_sort_by_least_voted(self):
        self.movie_1.vote_count = 1
        self.movie_2.vote_count = 2
        self.movie_3.vote_count = 3
        Movie.objects.bulk_update(Movie.objects.all(), ["vote_count"])

        response = self._send_request_and_assert_redirect(sorting_key="least_voted")
        movies = [r["movie"] for r in response.context["results"]]
        self.assertEqual(movies, self.expected)

    def test_sort_by_longest(self):
        self.movie_1.runtime = 3
        self.movie_2.runtime = 2
        self.movie_3.runtime = 1
        Movie.objects.bulk_update(Movie.objects.all(), ["runtime"])

        response = self._send_request_and_assert_redirect(sorting_key="longest")
        movies = [r["movie"] for r in response.context["results"]]
        self.assertEqual(movies, self.expected)

    def test_sort_by_shortest(self):
        self.movie_1.runtime = 1
        self.movie_2.runtime = 2
        self.movie_3.runtime = 3
        Movie.objects.bulk_update(Movie.objects.all(), ["runtime"])

        response = self._send_request_and_assert_redirect(sorting_key="shortest")
        movies = [r["movie"] for r in response.context["results"]]
        self.assertEqual(movies, self.expected)
