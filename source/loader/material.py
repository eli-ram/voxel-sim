from typing import Any
from ..data import colors as c
from .parse.auto import AutoParsable
from .parse.value import ValueParsable
from .parse.literal import Float
from .parse.nametuple import ParseNamedTuple, NamedTuple

class Locks(NamedTuple):
    x: bool = False
    y: bool = False
    z: bool = False

class Force(NamedTuple):
    x: float = 0
    y: float = 0
    z: float = 0

class Color(ValueParsable[c.Color]):
    def validate(self, data: Any):
        if isinstance(data, str):
            return c.Colors.get(data)
        if isinstance(data, list):
            return c.Color(*data) # type: ignore
        return c.Colors.WHITE

class Material(AutoParsable):
    color: Color
    strength: Float
    locks: ParseNamedTuple[Locks]
    force: ParseNamedTuple[Force]