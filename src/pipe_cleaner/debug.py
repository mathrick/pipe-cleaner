"""Pipe debuging utilities"""

from pipe import Pipe, batched, islice

__all__ = ["debug_eager"]


@Pipe
def debug_eager(iterable, label: str | None = None, max_count: int = 100):
    """
    Debugging helper. Prints label if given, then eagerly fetches items from iterable,
    prints them, then passes them on. This is similar to tee(), but tee() is
    completely lazy, and will print items one-by-one, whereas this function will 

    For safety, only up to max_count items will be printed, to avoid infinite loops.

    Note that although this function is eager once it starts fetching the items, it's
    still a generator and thus won't actually do anything until something starts to
    iterate the pipeline (e.g. as_list()).

    Useful for figuring out why the pipeline doesn't produce all the expected elements,
    for example with take_while().

    >>> ("Hello world!"
    ...  | as_list()
    ...  | take_while(lambda x: x != " ")
    ...  | debug_eager("Characters:")
    ...  | map(ord)
    ...  | debug_eager("Codepoints:")
    ...  | as_list())
    Characters:
    H
    e
    l
    l
    o
    Codepoints:
    72
    101
    108
    108
    111
    [72, 101, 108, 108, 111]
    """
    iterable = iter(iterable)
    items = list(iterable | islice(None, max_count))
    if label is not None:
        print(label)
    for item in items:
        print(item)
    yield from items
    yield from iterable
