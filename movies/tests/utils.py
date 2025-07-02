from copy import deepcopy

from movies.models import Movie


def create_dummy_movie(original):
    num = (Movie.objects.count() + 1)
    new_movie = deepcopy(original)
    new_movie.tvdb_id = num
    new_movie.title = f"Dummy Movie {num}"
    new_movie.slug = f"dummy-movie-{num}"
    new_movie.imdb_id = f"imdb_{num}"
    new_movie.tmdb_id = num
    new_movie.save()
    return new_movie
