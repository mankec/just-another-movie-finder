from urllib.parse import urlencode


def build_url(*path_segments):
    return "/".join(str(path_segment).strip("/") for path_segment in path_segments)


def build_url_with_query(url, query):
    return f"{url}?{urlencode(query)}"
