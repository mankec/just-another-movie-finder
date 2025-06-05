import os
import re
import json
from urllib.parse import urlencode
from pathlib import Path
from itertools import chain

from requests import get, post, RequestException

from project.constants import (
    TOO_MANY_REQUESTS_STATUS_CODE,
    NOT_FOUND_STATUS_CODE,
    TOO_MANY_REQUESTS_MESSAGE,
    NOT_FOUND_MESSAGE
)

#TODO: Create separate files for these methods. Call them in this format: utilrequests, utilurls etc.

def build_url(*path_segments):
    return "/".join(str(path_segment).strip("/") for path_segment in path_segments)


def build_url_with_query(url, query):
    return f"{url}?{urlencode(query)}"


def send_request(*, method, url, headers={}, payload={}):
    response = None
    try:
        match method:
            case "GET":
                response = get(url, params=payload, headers=headers)
            case "POST":
                response = post(url, json=payload, headers=headers)
            case _:
                raise ValueError(
                    f"Hey it's {method} method and I am not supported!" \
                    "Please update me at movies/services/apis/loggers/helpers.py."
                )
        return response
    except RequestException as error:
        if response is not None:
            print("RequestException in send_request: %s" % error)
        else:
            print("Response doesn't exist: %s" % error)
            raise
    except Exception as error:
        print("Error while sending request: %s" % error)
        raise


def hyphenate(text):
    return re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-")


def create_empty_json_file(name, *, json_type):
    if json_type not in ("arr", "obj"):
        raise ValueError("Valid JSON types are 'arr' and 'obj'")
    try:
        data = [] if json_type == "arr" else {}
        file = Path(name)
        file.touch()
        file.write_text(json.dumps(data))
        return file
    except (Exception, KeyboardInterrupt) as error:
        print("Error while creating empty JSON file: %s" % error)
        raise


def append_to_json_file(new_data, file):
    try:
        with open(file, "r+") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError as error:
                print(f"JSON DecodeError while safe appending JSON to '{file.name}'")
                raise
            if isinstance(new_data, list):
                data.extend(new_data)
            else:
                data.append(new_data)
            file.seek(0)
            json.dump(data, file, indent=2)
            os.fsync(file.fileno())
    except (Exception, KeyboardInterrupt) as error:
        if error:
           print("Error while appending JSON: %s" % error)
        raise


def write_to_json_file(data, file):
    try:
        with open(file, "w") as file:
            json.dump(data, file, indent=2)
    except (Exception, KeyboardInterrupt) as error:
        print("Error while writing JSON: %s" % error)
        raise


def read_file(file):
    with open(file, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as error:
            print("Invalid JSON file: %s" % error)
    return data


def flatten(list_of_lists):
    #    "Flatten one level of nesting."
    # Taken from https://docs.python.org/3/library/itertools.html#itertools-recipes
    return chain.from_iterable(list_of_lists)
