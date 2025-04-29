from django.shortcuts import render

def index(request):
    return render(request, "movies/index.html")

def sign_in(request):
    return render(request, "movies/sign_in.html")
