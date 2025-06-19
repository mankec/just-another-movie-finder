from django.shortcuts import render


def index(request):
    return render(request, "core/index.html")


def error(request):
    ctx = {
        "headerless": True
    }
    return render(request, "core/error.html", ctx)
