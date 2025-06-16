from django.shortcuts import render


def error(request):
    ctx = {
        "headerless": True
    }
    return render(request, "core/error.html", ctx)
