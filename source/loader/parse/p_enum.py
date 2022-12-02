
from .utils import formatIter
from .indent import Fmt
from .error import ParseError
from .parsable import Parsable
from .p_types import getAnnotations, Any, isMap


class Enum(Parsable):

    _active: str
    _value: Any

    def __init__(self) -> None:
        self._enum = getAnnotations(self)

    def dataParse(self, data: Any):
        data = data or {}

        if not isMap(data):
            raise ParseError("Expected a Map for Enum option")

        if len(data) != 1:
            raise ParseError("Enum can only have one(1) value")

        key, value = next(iter(data.items()))

        if key not in self._enum:
            options = ",".join(f'"{key}"' for key in self._enum)
            raise ParseError(f"Invalid Enum option (use: {options})")

        if key != self._active:
            self._value = self._enum[key]()
            self._active = key

        yield self._value, value

    def formatValue(self, F: Fmt) -> str:
        return formatIter(self, F, "{}:", [(self._active, self._value)])
