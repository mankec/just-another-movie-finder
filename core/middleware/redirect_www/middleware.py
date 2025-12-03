from django.http import HttpResponsePermanentRedirect

from project.settings import PRODUCTION_URL


class RedirectWwwMiddleware:
    # This only applies for production but no need to restrict it in development
    # Redirect all requests from www subdomain to root domain

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()

        if host.startswith("www."):
            url = f"{PRODUCTION_URL}{request.get_full_path()}".rstrip("/")
            return HttpResponsePermanentRedirect(url)
        response = self.get_response(request)
        return response
