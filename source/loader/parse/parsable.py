from typing import Any
from .indent import Format, Fmt

class Parsable:
    """ Abstract Parsable Definition """
    changed = False
    error = False
    what = ""
    
    def parse(self, data: Any): ...
    def format(self, F: Fmt) -> str: ...

    def __str__(self) -> str:
        name = self.__class__.__name__
        text = self.format(Format().init())
        return f"{name}:{text}"
