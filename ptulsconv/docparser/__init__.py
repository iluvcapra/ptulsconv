from typing import Generator, Callable, Iterator


def apply_appends(source: Iterator,
                  should_append: Callable,
                  do_append: Callable) -> Generator:
    this_element = next(source)
    for element in source:
        if should_append(this_element, element):
            this_element = do_append(this_element, element)
        else:
            yield this_element
            this_element = element

    yield this_element
