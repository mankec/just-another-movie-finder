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

def create_empty_file(name):
    try:
        file = Path(name)
        file.touch()
        return file
    except (Exception, KeyboardInterrupt) as error:
        print("Error while creating empty file: %s" % error)
        raise


def append_to_json_file(new_data, file):
    try:
        with open(file, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as error:
                print(f"JSON DecodeError while safe appending JSON to '{f.name}'")
                raise
            if isinstance(new_data, list):
                data.extend(new_data)
            else:
                data.append(new_data)
            f.seek(0)
            json.dump(data, f, indent=2, ensure_ascii=False)
            os.fsync(f.fileno())
    except (Exception, KeyboardInterrupt) as error:
        if error:
           print("Error while appending JSON: %s" % error)
        raise


def write_to_json_file(data, file):
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except (Exception, KeyboardInterrupt) as error:
        print("Error while writing JSON: %s" % error)
        raise


def read_json_file(file):
    with open(file, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as error:
            print("Invalid JSON f: %s" % error)
    return data


def dir_size(fd):
    return sum(f.stat().st_size for f in fd.rglob("*") if f.is_file())


def append_to_jsonl_file(new_data, file):
    try:
        with open(file, "a", encoding="utf-8") as f:
            if isinstance(new_data, list):
                for d in new_data:
                    json.dump(d, f, ensure_ascii=False)
                    f.write("\n")
            else:
                json.dump(new_data, f, ensure_ascii=False)
                f.write("\n")
            os.fsync(f.fileno())
    except (Exception, KeyboardInterrupt) as error:
        if error:
           print("Error while appending JSON: %s" % error)
        raise


def read_jsonl_file(file):
    def _generator():
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
    return list(_generator())
