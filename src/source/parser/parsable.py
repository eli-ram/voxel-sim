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
    # Source File
    __file = ""

    def __init__(self) -> None: ...

    @contextmanager
    def captureErrors(self, throw=True):
        try:
            yield

        except error.ChainError as e:
            self.__error = True
            # There is no message when chaining

        except error.ParseError as e:
            self.__error = True
            self.__what = error.what(e)

        except Exception as e:
            self.__error = True
            self.__what = error.what(e) + error.trace(e)

        if throw and self.__error:
            raise error.ChainError()


    def hasChanged(self):
        return self.__changed
    
    def setChanged(self, changed: bool):
        self.__changed |= changed
    
    def hasError(self):
        return self.__error

    def setError(self, error: bool) -> bool:
        self.__error |= error
        return self.__error

    def getError(self):
        return self.__what    

    def getFile(self):
        return self.__file

    def parse(self, data: t.Any, file: str) -> Tuple[bool, bool]:
        # Forward State
        self.__changed = self.__error
        self.__error = False
        self.__what = ""
        self.__file = file

        L = []

        # Query Data
        with self.captureErrors(throw=False):
            if I := self.dataParse(data):
                L = list(I)


        # Parse Children
        for P, D in L:
            # print(self.__class__.__name__, "->", P.__class__.__name__, D)            
            changed, error = P.parse(D, file)
            self.__changed |= changed
            self.__error |= error

        # Post Update
        if self.__changed and not self.__error:
            with self.captureErrors(throw=False):
                self.postParse()

        # print(self.__class__.__name__, self.__changed, self.__error, self.__what)
        return self.__changed, self.__error

    def dataParse(self, data: t.Any) -> Iterator[Tuple[Parsable, t.Any]]: ...
    def postParse(self) -> None: ...
    def formatValue(self, F: Fmt) -> str: ...

    def __str__(self) -> str:
        name = self.__class__.__name__
        text = self.formatValue(Format().init())
        return f"{name}: {text}"
