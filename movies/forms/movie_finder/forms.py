from django import forms
from django.core.exceptions import ValidationError

from core.forms.widgets import PrettyCheckboxSelectMultiple, PrettyRadioSelect
from core.utils import intersection
from movies.models import Genre
from movies.countries.constants import COUNTRIES
from movies.languages.constants import LANGUAGES


class MovieFinderForm(forms.Form):
    country_choices = [("", "Choose a country")]
    country_choices += sorted(
        [
            (k, v["english_name"]) for k, v
            in COUNTRIES.items()
        ],
        key=lambda country: country[1],
    )
    language_choices = [("", "Choose a language")]
    language_choices += [
        (k, v["english_name"]) for k, v
        in LANGUAGES.items()
    ]
    country = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": """
                bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500
                """
            }
        ),
        choices=country_choices,
        required=False,
    )
    language = forms.ChoiceField(
        widget=forms.Select(
            attrs={
                "class": """
                bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500
                """
            }
        ),
        choices=language_choices,
        required=False,
    )
    genres = forms.MultipleChoiceField(
        widget=PrettyCheckboxSelectMultiple(
            attrs={
                "placeholder": "Search genres",
            },
        ),
        label="Include genres",
        required=False,
    )
    exclude_genres = forms.MultipleChoiceField(
        widget=PrettyCheckboxSelectMultiple(
            attrs={
                "placeholder": "Search genres",
            },
        ),
        label="Exclude genres",
        required=False,
    )
    year_from = forms.CharField(
        label="Year",
        widget=forms.TextInput(
            attrs={
                "class": """
                bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500
                """,
                "placeholder": "From",
            }
        ),
        max_length=4,
        required=False,
    )
    year_to = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": """
                bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500
                """,
                "placeholder": "To",
            }
        ),
        max_length=4,
        required=False,
    )
    runtime_min = forms.CharField(
        label="Runtime",
        widget=forms.TextInput(
            attrs={
                "class": """
                bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500
                """,
                "placeholder": "Min",
            }
        ),
        max_length=6,
        required=False,
    )
    runtime_max = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": """
                bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500
                """,
                "placeholder": "Max",
            }
        ),
        max_length=6,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        genre_choices = [
            (g.id, g.name) for g
            in Genre.objects.order_by("name")
        ]
        self.fields["genres"].choices = genre_choices
        self.fields["exclude_genres"].choices = genre_choices

    def clean(self):
        cleaned_data = super().clean()
        values = [v for _, v in cleaned_data.items()]
        if not any(values):
            raise ValidationError("You must use at least one filter.")

        runtime_min = cleaned_data["runtime_min"]
        runtime_max = cleaned_data["runtime_max"]
        if runtime_min and runtime_max and int(runtime_min) > int(runtime_max):
            raise ValidationError("Maximum runtime cannot be lower than minimum runtime.")

        year_from = cleaned_data["year_from"]
        year_to = cleaned_data["year_to"]
        if year_from and year_to and int(year_from) > int(year_to):
            raise ValidationError("Invalid order of year from and year to.")

        genres = cleaned_data["genres"]
        exclude_genres = cleaned_data["exclude_genres"]

        if intersected_genres := intersection(genres, exclude_genres):
            genre = Genre.objects.get(pk=intersected_genres[0])
            raise ValidationError(
                f"You have {genre.name} in both included and excluded genres."
            )
