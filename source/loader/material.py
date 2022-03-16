from typing import Any, Dict, List, NamedTuple
from ..data import colors as c
from .parse import all as p
from .vector import Vector

class Locks(NamedTuple):
    x: bool = False
    y: bool = False
    z: bool = False

class Color(p.Value[c.Color]):
    def fromNone(self):
        return c.Colors.WHITE

    def fromMap(self, data: Dict[str, Any]):
        return c.Color(**data)

    def fromArray(self, data: List[Any]):
        return c.Color(*data)

    def fromValue(self, data: Any):
        return c.Colors.get(data)
        
class Material(p.Struct):
    color: Color
    strength: p.Float
    locks: p.Value[Locks]
    force: Vector