from project.utils import hyphenate

def tvdb_id(id, title):
    return f"{id}, {hyphenate(title).lower()}"
