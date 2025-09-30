from django.db.models import Count, Q

from core.wrappers import handle_exception
from movies.models import Movie

class MovieFinder():
    def __init__(self, **kwargs):
        self.country = kwargs.get("country")
        self.language = kwargs.get("language")
        self.genres = kwargs.get("genres")
        self.exclude_genres = kwargs.get("exclude_genres")
        self.year_from = kwargs.get("year_from")
        self.year_to = kwargs.get("year_to")
        self.runtime_min = kwargs.get("runtime_min")
        self.runtime_max = kwargs.get("runtime_max")

    @handle_exception
    def get_movie_ids(self) -> list:
        filter_query = Q()
        exclude_filter_query = Q()
        if self.country:
            filter_query &= Q(origin_country__contains=[self.country])

        if self.language:
            filter_query &= Q(original_language=self.language)

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

        if self.exclude_genres:
            exclude_filter_query = Q(genres__id__in=self.exclude_genres)

        if self.genres:
            filter_query &= Q(matched_genres=len(self.genres))
            movies = (
                Movie.objects.annotate(
                    matched_genres=Count(
                        "genres",
                        filter=Q(genres__id__in=self.genres),
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
        return list(movies.values_list("id", flat=True))
