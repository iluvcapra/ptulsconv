from typing import Generator, Callable, Iterator
from enum import Enum


def apply_appends(source: Iterator,
                  should_append: Callable,
                  do_append: Callable) -> Generator:
    """
    :param source:
    :param should_append: Called with two variables a and b, your
                        function should return true if b should be
                        appended to a
    :param do_append: Called with two variables a and b, your function
                        should return
    :returns: A Generator
    """
    this_element = next(source)
    for element in source:
        if should_append(this_element, element):
            this_element = do_append(this_element, element)
        else:
            yield this_element
            this_element = element

    yield this_element
