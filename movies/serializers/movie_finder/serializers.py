# serializers.py
from rest_framework import serializers
from django.core.exceptions import ValidationError

from core.utils import intersection
from movies.models import Genre
from movies.countries.constants import COUNTRIES
from movies.languages.constants import LANGUAGES


class MovieFinderFormSerializer(serializers.Serializer):
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

    country = serializers.ChoiceField(
        choices=country_choices,
        required=False,
    )
    language = serializers.ChoiceField(
        choices=language_choices,
        required=False,
    )
    genres = serializers.MultipleChoiceField(
        choices=[],
        label="Include genres",
        required=False,
    )
    exclude_genres = serializers.MultipleChoiceField(
        choices=[],
        label="Include genres",
        required=False,
    )
    year_from = serializers.CharField(
        required=False,
    )
    year_to = serializers.CharField(
        required=False,
    )
    runtime_min = serializers.CharField(
        required=False,
    )
    runtime_max = serializers.CharField(
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

    def validate(self, attrs):
        if not any(attrs.values()):
            raise ValidationError("You must use at least one filter.")

        runtime_min = attrs.get("runtime_min")
        runtime_max = attrs.get("runtime_max")
        if runtime_min and runtime_max and int(runtime_min) > int(runtime_max):
            raise ValidationError("Maximum runtime cannot be lower than minimum runtime.")

        year_from = attrs.get("year_from")
        year_to = attrs.get("year_to")
        if year_from and year_to and int(year_from) > int(year_to):
            raise ValidationError("Invalid order of year from and year to.")

        genres = attrs.get("genres", [])
        exclude_genres = attrs.get("exclude_genres", [])

        if intersected_genres := intersection(genres, exclude_genres):
            genre = Genre.objects.get(pk=intersected_genres[0])
            raise ValidationError(
                f"You have {genre.name} in both included and excluded genres."
            )
        return attrs
