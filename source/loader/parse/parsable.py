from .indent import Format, Fmt
from . import types as t

class Parsable:
    """ Abstract Parsable Definition """

    changed = False
    error = False
    what = ""

    def __init__(self) -> None: ...
    def parse(self, data: t.Any): ...
    def format(self, F: Fmt) -> str: ...

    def __str__(self) -> str:
        name = self.__class__.__name__
        text = self.format(Format().init())
        return f"{name}: {text}"

    def link(self, parsable: 'Parsable', data: t.Any):
        parsable.parse(data)
        self.changed |= parsable.changed
        self.error |= parsable.error
