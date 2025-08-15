from django.contrib import admin
from django.db.models import Count, Q

from movies.models import Movie, Genre


class MoviesMissingFieldFilter(admin.SimpleListFilter):
    title = "missing field"
    parameter_name = "missing_field"

    def lookups(self, _request, _model_admin):
        return [
            ("runtime", "Missing runtime"),
            ("poster", "Missing poster"),
            ("year", "Missing year"),
            ("imdb_id", "Missing IMDb ID"),
            ("tmdb_id", "Missing TMDB ID"),
            ("budget", "Missing budget"),
            ("box_office", "Missing box office"),
            ("genre", "Missing genre"),
        ]

    def queryset(self, _request, queryset):
        if self.value() == "runtime":
            return queryset.filter(runtime__isnull=True)
        elif self.value() == "poster":
            return queryset.filter(poster__isnull=True)
        elif self.value() == "year":
            return queryset.filter(year__isnull=True)
        elif self.value() == "imdb_id":
            return queryset.filter(imdb_id__isnull=True)
        elif self.value() == "tmdb_id":
            return queryset.filter(tmdb_id__isnull=True)
        elif self.value() == "budget":
            return queryset.filter(
                Q(budget__isnull=True) |
                Q(budget=0)
            )
        elif self.value() == "box_office":
            return queryset.filter(
                Q(box_office__isnull=True) |
                Q(box_office=0)
            )
        elif self.value() == "genre":
            return (queryset.annotate(genres_count=Count('genres'))
                .filter(genres_count=0)
            )
        return queryset


class MovieAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    filter_horizontal = ('genres',)
    list_filter = [
        MoviesMissingFieldFilter,
    ]


admin.site.register(Movie, MovieAdmin)
admin.site.register(Genre)
