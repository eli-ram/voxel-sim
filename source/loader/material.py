from typing import Any
from ..data import colors as c
from .parse import AutoParsable, ValueParsable, MapParsable
from .literal import Float, Array


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
    locks: Array[bool]
    force: Array[float]

class MaterialMap(MapParsable[Material]):
    child = Material
