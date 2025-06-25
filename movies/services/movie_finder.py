from django.db.models import Count, Q

from movies.models import Movie, Genre


class MovieFinder():

    def __init__(self, match_some_criteria=True, **kwargs):
        self.match_some_criteria = match_some_criteria
        self.countries = kwargs.get("countries", [])
        self.languages = kwargs.get("languages", [])
        self.years = kwargs.get("years", [])
        self.genres = kwargs.get("genres", [])
        self.runtime_min = kwargs.get("runtime_min", None)
        self.runtime_max = kwargs.get("runtime_max", None)

    def perform(self):
        if self.match_some_criteria:
            filter_query = Q()
            if self.countries:
                filter_query |= Q(country__in=self.countries)

            if self.languages:
                filter_query |= Q(language__in=self.languages)

            if self.years:
                filter_query |= Q(year__in=self.years)

            if self.runtime_min and self.runtime_max:
                filter_query |= Q(runtime__range=(self.runtime_min, self.runtime_max))
            elif self.runtime_min:
                filter_query |= Q(runtime__gte=self.runtime_min)
            elif self.runtime_max:
                filter_query |= Q(runtime__lte=self.runtime_max)

            movies = Movie.objects.filter(filter_query)

            if self.genres:
                movies_with_genres = (
                    Movie.objects.filter(
                        Q(genres__name__in=self.genres)
                    )
                    .prefetch_related("genres")
                )
                movies = movies_with_genres.union(movies)
        else:
            filter_kwargs = {}
            if self.countries:
                filter_kwargs["country__in"] = self.countries

            if self.languages:
                filter_kwargs["language__in"] = self.languages

            if self.years:
                filter_kwargs["year__in"] = self.years

            if self.runtime_min and self.runtime_max:
                filter_kwargs["runtime__range"] = (self.runtime_min, self.runtime_max)
            elif self.runtime_min:
                filter_kwargs["runtime__gte"] = self.runtime_min
            elif self.runtime_max:
                filter_kwargs["runtime__lte"] = self.runtime_max

            if self.genres:
                # TODO: Check if total_genres is redundant
                filter_kwargs["total_genres"] = len(self.genres)
                filter_kwargs["matched_genres"] = len(self.genres)
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

            movies = (
                movies.filter(
                    **filter_kwargs,
                )
                .prefetch_related("genres")
                .distinct()
            )
        return movies
