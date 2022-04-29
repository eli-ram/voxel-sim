from typing import Tuple
from .indent import Format, Fmt
from . import types as t

Changed = bool
Error = bool

class Parsable:
    """ Abstract Parsable Definition """

    changed = False
    error = False
    what = ""

    def __init__(self) -> None: ...
    def parse(self, data: t.Any) -> Tuple[Changed, Error]: ...
    def format(self, F: Fmt) -> str: ...

    def __str__(self) -> str:
        name = self.__class__.__name__
        text = self.format(Format().init())
        return f"{name}: {text}"

    def link(self, state: Tuple[Changed, Error]):
        changed, error = state
        self.changed |= changed
        self.error |= error