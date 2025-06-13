from urllib.parse import urlencode, urlparse


def build_url(*path_segments):
    return "/".join(str(path_segment).strip("/") for path_segment in path_segments)


def build_url_with_query(url, query):
    return f"{url}?{urlencode(query)}"


def is_url(string):
    parsed = urlparse(string)
    return bool(parsed.scheme and parsed.netloc)
