from django.db.models import Count, Q

from core.wrappers import handle_exception
from movies.models import Movie

class MovieFinder():
    def __init__(self, **kwargs):
        self.country_id = kwargs["country"]
        self.language_alpha_3 = kwargs["language"]
        self.genre_slugs = kwargs["genres"]
        self.exclude_genre_slugs = kwargs["exclude_genres"]
        self.year_from = kwargs["year_from"]
        self.year_to = kwargs["year_to"]
        self.runtime_min = kwargs["runtime_min"]
        self.runtime_max = kwargs["runtime_max"]

    @handle_exception
    def get_movie_ids(self) -> list:
        filter_query = Q()
        if self.country_id:
            filter_query &= Q(country=self.country_id)

        if self.language_alpha_3:
            filter_query &= Q(language_alpha_3=self.language_alpha_3)

        if self.year_from and self.year_to:
            filter_query &= Q(year__range=(self.year_from, self.year_to))
        elif self.year_from:
            filter_query &= Q(year__gte=self.year_from)
        elif self.year_to:
            filter_query &= Q(year__lte=self.year_to)

        if self.runtime_min and self.runtime_max:
            filter_query &= Q(runtime__range=(self.runtime_min, self.runtime_max))
        elif self.runtime_min:
            filter_query &= Q(runtime__gte=self.runtime_min)
        elif self.runtime_max:
            filter_query &= Q(runtime__lte=self.runtime_max)

        exclude_filter_query = Q()
        if self.exclude_genre_slugs:
            exclude_filter_query = Q(genres__slug__in=self.exclude_genre_slugs)

        if self.genre_slugs:
            filter_query &= Q(matched_genres=len(self.genre_slugs))
            movies = (
                Movie.objects.annotate(
                    matched_genres=Count(
                        "genres",
                        filter=Q(genres__slug__in=self.genre_slugs),
                        distinct=True
                    )
                )
            )
        else:
            movies = Movie.objects

        movies = (
            movies.filter(
                filter_query
            )
            .exclude(exclude_filter_query)
        )
        return list(movies.values_list("tvdb_id", flat=True))
