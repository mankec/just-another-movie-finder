import re
from urllib.parse import urlencode

from django.contrib.sessions.models import Session


def build_url(url, query=None):
    if query:
        return f"{url}?{urlencode(query)}"
    return url

def hyphenate(text):
    return re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-")
