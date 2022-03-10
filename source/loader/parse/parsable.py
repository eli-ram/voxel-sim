from typing import Any
from .indent import Indent

class Parsable:
    """ Abstract Parsable Definition """

    def parse(self, data: Any): ...
    def format(self, I: Indent) -> str: ...

    def __str__(self) -> str:
        T = self.format(Indent("| ", "  ", ""))
        return f"\nv{T}\n^"
