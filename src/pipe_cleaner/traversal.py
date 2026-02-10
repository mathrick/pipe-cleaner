"""
Utilities for traversing and consuming inside pipes
"""
from collections.abc import Iterator
from contextlib import contextmanager

from pipe import chain_with, islice, Pipe

__all__ = ["LookaheadError", "with_lookahead"]


class LookaheadError(RuntimeError):
    """Exception signalling errors in usage of streams created by with_lookahead()"""


@contextmanager
def stop_iteration_handler():
    """Silently catch StopIteration inside the managed block"""
    try:
        yield
    except StopIteration:
        pass


class LookaheadIterable:
    def __init__(self, iterable):
        # Ensure consistent iteration behaviour
        self.iterable = iter(iterable)
        self._peeking = None
        self.peeked = []
        self.unpeeked = []
        self.iterator = None

    def _iterate(self):
        with stop_iteration_handler():
            while True:
                if self._peeking:
                    raise LookaheadError("Cannot iterate after a peek(). Call rewind() first")
                yield self.unpeeked.pop(0) if self.unpeeked else next(self.iterable)

    def __iter__(self):
        return self._iterate()

    def peek(self):
        """
        Return a new stream which looks ahead at the future elements of the underlying
        iterable
        """
        if self._peeking:
            raise LookaheadError("peek() called multiple times without rewind()")

        def _peek():
            with stop_iteration_handler():
                while True:
                    item = self.unpeeked.pop(0) if self.unpeeked else next(self.iterable)
                    self.peeked.append(item)
                    yield item

        self._peeking = _peek()
        return self._peeking

    def rewind(self, n: int = -1):
        """
        Finish a peek, rewinding the underlying iterable and returning previously peeked
        elements to it
        """
        if not self._peeking:
            raise LookaheadError("rewind() called without peek()")

        if n < 0:
            self.unpeeked = self.peeked[:]
        if n > 0:
            self.unpeeked = self.peeked[-n:]

        self.peeked.clear()
        self._peeking.close()
        self._peeking = None


def with_lookahead(iterable):
    """
    Return a new iterable which allows looking ahead. This is not a pipe element itself,
    but can be used to allow pipe element to make decisions about handling the current
    item based on the following ones.

    More specifically, the return value is a generator which can be iterated normally, but
    it also has two extra methods:

    - peek(): Create a new stream which peeks into the future values of the
      generator. Peeking must be finished by calling rewind() before iteration on the
      generator is resumed
    - rewind(n=-1): Finish peeking and return n most recently yielded values to the
      generator so they will be yielded again. -1 means "all values", and 0 will return
      none, effectively dropping them from the stream

    Peeking and iteration of the underlying generator must not be mixed. Once peek() is
    called, it _must_ be finished rewind() before iteration is resumed. Similarly, calling
    peek() multiple times in a row is an error, rewind() must be called before a next
    peek() is allowed.

    As a simple example, let's say we have a log of tests being executed. Each execution
    begins with the name of a test, then has some number of log lines for that test,
    before an outcome is printed. We want to filter the logs so that only the ones for
    failing tests are included:

    logs = []
    for i in range(8):
        logs.append(f"Test name: test {i}")
        logs.extend(("Log line",) * random.randint(0, 3))
        logs.append(f"Outcome: {'FAIL' if i % 3 == 0 else 'PASS'}")

    @Pipe
    def filter_by_outcome(iterable, outcome: str):
        pattern = "Outcome:"
        iterable = with_lookahead(iterable)

        while True:
            log_lines = (iterable.peek()
                         | take_while(lambda x: not x.startswith(pattern))
                         | as_list())

            # Rewind one line. This restores the last line consumed by take_while() so we can
            # actually see the outcome and parse it
            iterable.rewind(1)

            parsed_outcome = (iterable.peek()
                              | take_while(lambda x: x.startswith(pattern))
                              | map(lambda x: x.removeprefix(pattern).strip())
                              | take(1)
                              | as_list())


            if not (log_lines and parsed_outcome):
                break

            if parsed_outcome == [outcome]:
                # Rewind again, so we can emit the unparsed outcome line together with the rest of
                # the lines
                iterable.rewind()
                yield from log_lines | chain_with(iterable | take(1))
                continue

            # Not the outcome we were looking for, skip these lines completely
            iterable.rewind(0)

    failed_only = logs | filter_by_outcome("FAIL") | as_list()

    >>> failed_only
    ['Test name: test 0', 'Outcome: FAIL', 'Test name: test 3', 'Log line', 'Outcome: FAIL']
    """
    if isinstance(iterable, LookaheadIterable):
        return iterable

    return LookaheadIterable(iterable)
