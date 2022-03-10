from typing import Any
from .indent import Format, Fmt

class Parsable:
    """ Abstract Parsable Definition """
    changed: bool = False

    def parse(self, data: Any): ...
    def format(self, F: Fmt) -> str: ...

    def __bool__(self) -> bool:
        return self.changed

    def __str__(self) -> str:
        T = self.format(Format().init())
        return f"\nv{T}\n^"
