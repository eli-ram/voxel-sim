from __future__ import annotations
from contextlib import contextmanager
from typing import Tuple, Iterator

from .indent import Format, Fmt
from . import error
from . import p_types as t


class Parsable:
    """ Abstract Parsable Definition """

    # Has this been changed during last update
    __changed = False
    # Did an error get raised during last update
    __error = False
    # What was the error message
    __what = ""

    def __init__(self) -> None: ...

    @contextmanager
    def captureErrors(self):
        try:
            yield

        except error.ParseError as e:
            self.__error = True
            self.__what = error.what(e)

        except Exception as e:
            self.__error = True
            self.__what = error.what(e) + error.trace(e)

    def getError(self):
        return self.__what

    def parse(self, data: t.Any) -> Tuple[bool, bool]:
        # Forward State
        self.__changed = self.__error
        self.__error = False
        self.__what = ""

        # Query Data
        with self.captureErrors():
            for P, D in self.dataParse(data) or []:
                changed, error = P.parse(D)
                self.__changed |= changed
                self.__error |= error

        # Post Update
        if self.__changed and not self.__error:
            with self.captureErrors():
                self.postParse()

        return self.__changed, self.__error

    def dataParse(self, data: t.Any) -> Iterator[Tuple[Parsable, t.Any]]: ...
    def postParse(self) -> None: ...
    def formatValue(self, F: Fmt) -> str: ...

    def __str__(self) -> str:
        name = self.__class__.__name__
        text = self.formatValue(Format().init())
        return f"{name}: {text}"

    def dependOn(self, state: Tuple[bool, bool]):
        changed, error = state
        self.__changed |= changed
        self.__error |= error
