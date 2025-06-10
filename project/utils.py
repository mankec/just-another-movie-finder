from itertools import chain


def flatten(list_of_lists):
    #    "Flatten one level of nesting."
    # Taken from https://docs.python.org/3/library/itertools.html#itertools-recipes
    return chain.from_iterable(list_of_lists)
