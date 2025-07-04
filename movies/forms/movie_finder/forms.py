from django import forms
from django.core.exceptions import ValidationError

from core.forms.widgets import PrettyCheckboxSelectMultiple, PrettyRadioSelect
from core.utils import intersection
from movies.models import Country, Genre
from languages.constants import TVDB_SUPPORTED_LANGUAGES

MATCH_FILTERS_SOME = "some"
MATCH_FILTERS_ALL = "all"


class MovieFinderForm(forms.Form):
    countries = forms.MultipleChoiceField(
        widget=PrettyCheckboxSelectMultiple(
            attrs={
                "placeholder": "Search countries",
            },
        ),
        label="Include countries",
        required=False,
    )
    languages = forms.MultipleChoiceField(
        widget=PrettyCheckboxSelectMultiple(
            attrs={
                "placeholder": "Search languages",
            },
        ),
        choices=[
            (k, v["name"]) for k, v
            in dict(sorted(
                TVDB_SUPPORTED_LANGUAGES.items(),
                key=lambda x: x[1]["name"],
            )).items()
        ],
        label="Include languages",
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
    exclude_countries = forms.MultipleChoiceField(
        widget=PrettyCheckboxSelectMultiple(
            attrs={
                "placeholder": "Search countries",
            },
        ),
        label="Exclude countries",
        required=False,
    )
    exclude_languages = forms.MultipleChoiceField(
        widget=PrettyCheckboxSelectMultiple(
            attrs={
                "placeholder": "Search languages",
            },
        ),
        choices=[
            (k, v["name"]) for k, v
            in dict(sorted(
                TVDB_SUPPORTED_LANGUAGES.items(),
                key=lambda x: x[1]["name"],
            )).items()
        ],
        label="Exclude languages",
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
    match_filters = forms.ChoiceField(
        widget=PrettyRadioSelect(
            attrs={
                "checked": MATCH_FILTERS_SOME,
                "helpers": {
                    MATCH_FILTERS_SOME: "Exclude filters will be applied.",
                    MATCH_FILTERS_ALL: "Exclude filters will be ignored.",
                },
            }
        ),
        choices=[
            (MATCH_FILTERS_SOME, "Match some filters"),
            (MATCH_FILTERS_ALL, "Match all filters"),
        ],
        initial=MATCH_FILTERS_SOME,
        label="",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        country_choices= [
            (c.alpha_3, c.name) for c
            in Country.objects.order_by("name")
        ]
        genre_choices = [
            (g.slug, g.name) for g
            in Genre.objects.order_by("name")
        ]
        self.fields["countries"].choices = country_choices
        self.fields["genres"].choices = genre_choices
        self.fields["exclude_countries"].choices = country_choices
        self.fields["exclude_genres"].choices = genre_choices

    def clean(self):
        cleaned_data = super().clean()
        values = [v for k, v in cleaned_data.items() if k != "match_filters"]
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

        countries = cleaned_data["countries"]
        languages = cleaned_data["languages"]
        genres = cleaned_data["genres"]
        exclude_countries = cleaned_data["exclude_countries"]
        exclude_languages = cleaned_data["exclude_languages"]
        exclude_genres = cleaned_data["exclude_genres"]

        if intersected_countries := intersection(countries, exclude_countries):
            country = Country.objects.get(alpha_3=intersected_countries[0])
            raise ValidationError(
                f"You have {country.name} in both included and excluded countries."
            )
        if intersected_languages := intersection(languages, exclude_languages):
            language = TVDB_SUPPORTED_LANGUAGES[intersected_languages[0]]
            raise ValidationError(
                f"You have {language["name"]} in both included and excluded languages."
            )
        if intersected_genres := intersection(genres, exclude_genres):
            genre = Genre.objects.get(slug=intersected_genres[0])
            raise ValidationError(
                f"You have {genre.name} in both included and excluded genres."
            )
