from django.db import models
from django.contrib.postgres.fields import ArrayField


class Genre(models.Model):
    class Meta:
        db_table = "genre"

    # Assign genre's ID from TMDB
    id = models.PositiveIntegerField(primary_key=True)
    name = models.CharField(max_length=255, unique=True, null=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    class Meta:
        db_table = "movie"

    # Assign movie's ID from TMDB
    id = models.PositiveIntegerField(primary_key=True)
    backdrop_path = models.CharField(max_length=255, blank=True, null=True)
    budget = models.PositiveBigIntegerField(null=True)
    imdb_id = models.CharField(max_length=255, null=True)
    origin_country = ArrayField(
        models.CharField(max_length=255),
        default=list,
    )
    original_language = models.CharField(max_length=255, blank=True)
    original_title = models.CharField(max_length=255, blank=True)
    overview = models.TextField(blank=True)
    popularity = models.FloatField(blank=True, null=True)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    release_date = models.CharField(max_length=255, blank=True)
    revenue = models.PositiveBigIntegerField(null=True)
    runtime = models.PositiveIntegerField(null=True, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    spoken_languages = ArrayField(
        models.CharField(max_length=255),
        default=list,
    )
    status = models.CharField(max_length=255, blank=True)
    tagline = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    slug = models.CharField(max_length=255, blank=True)
    vote_average = models.FloatField(blank=True)
    vote_count = models.IntegerField(blank=True)
    backdrops = ArrayField(
        models.CharField(max_length=255),
        default=list,
    )
    logos = ArrayField(
        models.CharField(max_length=255),
        default=list,
    )
    posters = ArrayField(
        models.CharField(max_length=255),
        default=list,
    )
    keywords = ArrayField(
        models.CharField(max_length=255),
        default=list,
    )
    recommendations = ArrayField(
        models.CharField(max_length=255),
        default=list,
    )
    similar = ArrayField(
        models.CharField(max_length=255),
        default=list,
    )
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        # TODO: This makes tests fail
        if self.title == self.original_title:
            return f"{self.title} ({self.year})"
        else:
            return f"{self.title} ({self.year}), '{self.original_title}'"


class Person(models.Model):
    DEFAULTS = ["known_for_department", "name", "original_name", "profile_path"]

    class Meta:
        db_table = "person"

    # Assign person's ID from TMDB
    id = models.PositiveIntegerField(primary_key=True)
    known_for_department = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    original_name = models.CharField(max_length=255, blank=True)
    profile_path = models.CharField(max_length=255, blank=True, null=True)


class Cast(models.Model):
    class Meta:
        db_table = "cast"

    credit_id = models.CharField(max_length=255, blank=True)
    character = models.TextField(blank=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)


class Crew(models.Model):
    class Meta:
        db_table = "crew"

    credit_id = models.CharField(max_length=255, blank=True)
    department = models.CharField(max_length=255, blank=True)
    job = models.CharField(max_length=255, blank=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
