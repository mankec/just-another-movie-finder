from django.shortcuts import render
from movies.forms.movie_finder.forms import MovieFinderForm


def index(request):
    ctx = {
        "movie_finder_form": MovieFinderForm()
    }
    return render(request, "core/index.html", ctx)


def error(request):
    return render(request, "core/error.html")
