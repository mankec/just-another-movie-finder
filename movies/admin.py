from django.contrib import admin
from django.db.models import Count, Q

from movies.models import Movie, Genre


class MoviesWithoutFieldFilter(admin.SimpleListFilter):
    title = "Without field"
    parameter_name = ""

    def lookups(self, _request, _model_admin):
        return [
            ("without_runtime", "Without runtime"),
            ("without_poster", "Without poster"),
            ("without_year", "Without year"),
            ("without_imdb_id", "Without IMDb ID"),
            ("without_tmdb_id", "Without TMDB ID"),
            ("without_budget", "Without budget"),
            ("without_box_office", "Without box office"),
            ("without_genre", "Without genre"),
        ]

    def queryset(self, _request, queryset):
        if self.value() == "without_runtime":
            return queryset.filter(runtime__isnull=True)
        elif self.value() == "without_poster":
            return queryset.filter(poster__isnull=True)
        elif self.value() == "without_year":
            return queryset.filter(year__isnull=True)
        elif self.value() == "without_imdb_id":
            return queryset.filter(imdb_id__isnull=True)
        elif self.value() == "without_tmdb_id":
            return queryset.filter(tmdb_id__isnull=True)
        elif self.value() == "without_budget":
            return queryset.filter(
                Q(budget__isnull=True) |
                Q(budget=0)
            )
        elif self.value() == "without_box_office":
            return queryset.filter(
                Q(box_office__isnull=True) |
                Q(box_office=0)
            )
        elif self.value() == "without_genre":
            return (queryset.annotate(genres_count=Count('genres'))
                .filter(genres_count=0)
            )
        return queryset


class MovieAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    filter_horizontal = ('genres',)
    list_filter = [MoviesWithoutFieldFilter]


admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre)
