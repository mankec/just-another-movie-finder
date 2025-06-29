from django.db.models import Count, Q

from core.wrappers import handle_exception
from movies.models import Movie, Country, Genre
from movies.forms.movie_finder.forms import MATCH_FILTERS_SOME
from languages.constants import TVDB_SUPPORTED_LANGUAGES

class MovieFinder():
    def __init__(self, **kwargs):
        self.countries = Country.objects.filter(
            alpha_3__in=kwargs["countries"]
        ).values_list("name", flat=True)
        self.exclude_countries = Country.objects.filter(
            alpha_3__in=kwargs["exclude_countries"]
        ).values_list("name", flat=True)
        self.languages = [
            v["name"] for k,v in TVDB_SUPPORTED_LANGUAGES.items()
            if k in kwargs["languages"]
        ]
        self.exclude_languages = [
            v["name"] for k,v in TVDB_SUPPORTED_LANGUAGES.items()
            if k in kwargs["exclude_languages"]
        ]
        self.genres = Genre.objects.filter(
            slug__in=kwargs["genres"]
        ).values_list("name", flat=True)
        self.exclude_genres = Genre.objects.filter(
            slug__in=kwargs["exclude_genres"]
        ).values_list("name", flat=True)
        self.year_from = kwargs["year_from"]
        self.year_to = kwargs["year_to"]
        self.runtime_min = kwargs["runtime_min"]
        self.runtime_max = kwargs["runtime_max"]
        self.match_some_filters = kwargs["match_filters"] == MATCH_FILTERS_SOME

    @handle_exception
    def perform(self) -> list:
        if self.match_some_filters:
            include_filter_query = Q()
            if self.countries:
                include_filter_query |= Q(country__name__in=self.countries)

            if self.languages:
                include_filter_query |= Q(language__in=self.languages)

            if self.year_from and self.year_to:
                include_filter_query |= Q(year__range=(self.year_from, self.year_to))
            elif self.year_from:
                include_filter_query |= Q(year__gte=self.year_from)
            elif self.year_to:
                include_filter_query |= Q(year__lte=self.year_to)

            if self.runtime_min and self.runtime_max:
                include_filter_query |= Q(runtime__range=(self.runtime_min, self.runtime_max))
            elif self.runtime_min:
                include_filter_query |= Q(runtime__gte=self.runtime_min)
            elif self.runtime_max:
                include_filter_query |= Q(runtime__lte=self.runtime_max)

            exclude_filter_query = Q()
            if self.exclude_countries:
                exclude_filter_query |= Q(country__name__in=self.exclude_countries)

            if self.exclude_languages:
                exclude_filter_query != Q(language__in=self.exclude_languages)

            if self.exclude_genres:
                exclude_filter_query |= Q(genres__name__in=self.exclude_genres)

            movies = (
                Movie.objects.filter(
                    include_filter_query
                )
                .exclude(exclude_filter_query)
            )

            if self.genres:
                movies_with_genres = (
                    Movie.objects.filter(
                        Q(genres__name__in=self.genres)
                    )
                )

                if exclude_filter_query:
                    movies_with_genres = movies_with_genres.exclude(exclude_filter_query)

                movies = movies_with_genres.union(movies)
        else:
            include_filter_kwargs = {}
            if self.countries:
                include_filter_kwargs["country__name__in"] = self.countries

            if self.languages:
                include_filter_kwargs["language__in"] = self.languages

            if self.year_from and self.year_to:
                include_filter_kwargs["year__range"] = (self.year_from, self.year_to)
            elif self.year_from:
                include_filter_kwargs["year__gte"] = self.year_from
            elif self.year_to:
                include_filter_kwargs["year__lte"] = self.year_to

            if self.runtime_min and self.runtime_max:
                include_filter_kwargs["runtime__range"] = (self.runtime_min, self.runtime_max)
            elif self.runtime_min:
                include_filter_kwargs["runtime__gte"] = self.runtime_min
            elif self.runtime_max:
                include_filter_kwargs["runtime__lte"] = self.runtime_max

            if self.genres:
                # TODO: Check if total_genres is redundant
                include_filter_kwargs["total_genres"] = len(self.genres)
                include_filter_kwargs["matched_genres"] = len(self.genres)
                movies = (
                    Movie.objects.annotate(
                        total_genres=Count("genres", distinct=True),
                        matched_genres=Count(
                            "genres",
                            filter=Q(genres__name__in=self.genres),
                            distinct=True
                        )
                    )
                )
            else:
                movies = Movie.objects

            if include_filter_kwargs:
                movies = movies.filter(**include_filter_kwargs)

        return list(movies.values_list("tvdb_id", flat=True))
