from django.test import TestCase, Client
from django.urls import reverse

from core.tests.mixins import CustomAssertionsMixin
from core.constants import DEFAULT_YEAR
from movies.models import Genre


class MovieFinderFormIntegrationTestCase(TestCase, CustomAssertionsMixin):
    fixtures = ["genres.json"]

    def setUp(self):
        self.client = Client()
        self.find_url = reverse("movies:find")
        self.movies_url = reverse("movies:index")
        self.params = {
            "country": "",
            "language": "",
            "genres": [],
            "exclude_genres": [],
            "year_from": "",
            "year_to": "",
            "runtime_min": "",
            "runtime_max": "",
        }


    def test_validation_at_least_one_filter_must_be_used(self):
        message = "You must use at least one filter."
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertFlashMessage(response, message)

        self.params["year_from"] = DEFAULT_YEAR
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertRedirects(response, self.movies_url)

    def test_validation_max_runtime_cannot_be_lower_than_min_runtime(self):
        message = "Maximum runtime cannot be lower than minimum runtime."
        runtime_min= 90
        runtime_max= runtime_min - 1
        self.params["runtime_min"] = runtime_min
        self.params["runtime_max"] = runtime_max
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertFlashMessage(response, message)

        self.params["runtime_min"] = ""
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertRedirects(response, self.movies_url)

        self.params["runtime_min"] = runtime_min
        self.params["runtime_max"] = ""
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertRedirects(response, self.movies_url)


    def test_validation_invalid_order_of_year_from_and_year_to(self):
        message = "Invalid order of year from and year to."
        self.params["year_from"] = DEFAULT_YEAR
        self.params["year_to"] = DEFAULT_YEAR - 1
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertFlashMessage(response, message)

        self.params["year_from"] = ""
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertRedirects(response, self.movies_url)

        self.params["year_from"] = DEFAULT_YEAR
        self.params["year_to"] = ""
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertRedirects(response, self.movies_url)

    def test_validation_invalid_order_of_year_from_and_year_to(self):
        message = "Invalid order of year from and year to."
        self.params["year_from"] = DEFAULT_YEAR
        self.params["year_to"] = DEFAULT_YEAR - 1
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertFlashMessage(response, message)

        self.params["year_to"] = ""
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertRedirects(response, self.movies_url)

    def test_validation_same_genre_in_include_and_exclude_filters(self):
        genre = Genre.objects.get(name="Drama")
        message = f"You have {genre.name} in both included and excluded genres."
        self.params["genres"].append(genre.id)
        self.params["exclude_genres"].append(genre.id)
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertFlashMessage(response, message)

        self.params["genres"] = []
        response = self.client.get(self.find_url, query_params=self.params, follow=True)
        self.assertRedirects(response, self.movies_url)
