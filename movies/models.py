from django.db import models
from django.contrib.postgres.fields import ArrayField


class Genre(models.Model):
    class Meta:
        db_table = "genre"

    tvdb_id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Country(models.Model):
    class Meta:
        db_table = "country"

    name = models.CharField(max_length=50, unique=True)
    alpha_3 = models.CharField(max_length=3, unique=True)
    official_languages = ArrayField(
        models.CharField(max_length=50),
        default=list,
    )

    def __str__(self):
        return self.name


class Movie(models.Model):
    class Meta:
        db_table = "movie"

    tvdb_id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    last_updated = models.CharField(
        db_comment="Date and time when the movie was last updated from TVDB.",
    )
    poster = models.ImageField(upload_to='movie_posters/', null=True)
    runtime = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, blank=True)
    keep_updated = models.BooleanField()
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    imdb_id = models.CharField(max_length=16, null=True)
    tmdb_id = models.PositiveIntegerField(null=True)
    budget = models.PositiveBigIntegerField(null=True)
    box_office = models.PositiveBigIntegerField(null=True)
    language = models.CharField(max_length=20, blank=True)
    language_alpha_3 = models.CharField(max_length=3)
    genres = models.ManyToManyField(Genre)
    country = models.ForeignKey(Country, on_delete=models.RESTRICT)

    def __str__(self):
        return f"{self.title}  ({self.year})"

    def remote_ids(self):
        return [self.tvdb_id, self.imdb_id, str(self.tmdb_id)]
