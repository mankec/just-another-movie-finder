from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.shortcuts import render

from movies.serializers.movie_finder.serializers import MovieFinderFormSerializer
from core.wrappers import handle_exception

@handle_exception
@api_view()
@renderer_classes([TemplateHTMLRenderer])
def index(request):
    serializer = MovieFinderFormSerializer()
    return Response(
        {
            "serializer": serializer,
        },
        template_name="core/index.html",
    )


def error(request):
    return render(request, "core/error.html")
