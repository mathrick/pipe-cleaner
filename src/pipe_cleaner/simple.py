"""
Simple wrappers around existing functions
"""

from functools import reduce

from pipe import Pipe

__all__ = [
    "as_list",
    "as_dict",
    "as_tuple",
    "as_sum",
    "join",
    "reduce",
]


def as_list() -> Pipe:
    """Convert pipe's iterable to {py:class}`list`. Simple shorthand for `Pipe(list)`"""
    return Pipe(list)


def as_dict() -> Pipe:
    """Convert pipe's iterable to {py:class}`dict`. Simple shorthand for `Pipe(dict)`"""
    return Pipe(dict)


def as_tuple() -> Pipe:
    """Convert pipe's iterable to {py:class}`tuple`. Simple shorthand for `Pipe(tuple)`"""
    return Pipe(tuple)


@Pipe
def as_sum(iterable, /, start=0):
    """
    Return sum of the pipe's iterable. Wraps builtin {py:func}`sum` in a {py:class}`Pipe`,
    same as `add()` from Pipe 1.x
    """
    return sum(iterable, start=start)


def join(sep: str):
    """
    Join the iterable into a string with sep. Wraps {py:meth}`str.join` in a
    {py:class}`Pipe`
    """
    return Pipe(sep.join)


@Pipe
def reduce(iterable, function, *args, **kwargs):
    """
    Reduce the pipe's iterable with function. Wraps {py:func}`functools.reduce` in a
    {py:class}`Pipe`
    """
    return reduce(function, iterable, *args, **kwargs)
