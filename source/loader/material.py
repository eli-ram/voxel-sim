from typing import Any
from ..data import colors as c
from .parse import AutoParsable, ValueParsable, MapParsable
from .literal import Float


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

class ColorMap(MapParsable[Color]):
    def create(self):
        return Color()
