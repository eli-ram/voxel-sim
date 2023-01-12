from __future__ import annotations
from contextlib import contextmanager
from typing import Tuple, Iterator

from .indent import Format, Fmt
from . import error
from . import types as t


class Parsable:
    """ Abstract Parsable Definition """

    changed = False
    error = False
    what = ""

    def __init__(self) -> None: ...

    @contextmanager
    def capture(self):
        try:
            yield

        except error.ParseError as e:
            self.error = True
            self.what = error.what(e)

        except Exception as e:
            self.error = True
            self.what = error.what(e) + error.trace(e)

    def parse(self, data: t.Any) -> Tuple[bool, bool]:
        # Forward State
        self.changed = self.error
        self.error = False
        self.what = ""

        # Query Data
        with self.capture():
            for P, D in self.dataParse(data) or []:
                changed, error = P.parse(D)
                self.changed |= changed
                self.error |= error

        # Post Update
        if self.changed and not self.error:
            with self.capture():
                self.postParse()

        return self.changed, self.error

    def dataParse(self, data: t.Any) -> Iterator[Tuple[Parsable, t.Any]]: ...
    def postParse(self) -> None: ...
    def format(self, F: Fmt) -> str: ...

    def __str__(self) -> str:
        name = self.__class__.__name__
        text = self.format(Format().init())
        return f"{name}: {text}"

    def link(self, state: Tuple[bool, bool]):
        changed, error = state
        self.changed |= changed
        self.error |= error