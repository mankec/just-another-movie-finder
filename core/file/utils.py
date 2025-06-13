import os
import json
from pathlib import Path


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
