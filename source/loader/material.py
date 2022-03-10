from typing import Any, NamedTuple
from ..data import colors as c
from .parse import all as p

class Locks(NamedTuple):
    x: bool = False
    y: bool = False
    z: bool = False

class Force(NamedTuple):
    x: float = 0
    y: float = 0
    z: float = 0

class Color(p.Value[c.Color]):
    def validate(self, data: Any):
        if isinstance(data, str):
            return c.Colors.get(data)
        if isinstance(data, list):
            return c.Color(*data) # type: ignore
        return c.Colors.WHITE
        
class Material(p.Struct):
    color: Color
    strength: p.Float
    locks: p.NamedTuple[Locks]
    force: p.NamedTuple[Force]