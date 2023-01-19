
from typing import Optional, TypeVar, Generic
from .utils import formatIter
from .indent import Fmt
from .error import ParseError
from .parsable import Parsable
from .p_types import getAnnotations, Any, isMap

I = TypeVar('I')


class Enum(Parsable, Generic[I]):
    """ A Type <=> Value enum 

    `inspired by rust`
    """

    _active: str
    _value: Optional[Parsable] = None

    def __init__(self) -> None:
        self._enum = getAnnotations(self)

    def ok(self):
        return self._value is not None

    def get(self) -> Optional[I]:
        return self._value  # type: ignore

    def require(self) -> I:
        if self._value is None:
            raise ParseError("Enum is not set!")
        return self._value  # type: ignore

    def variant(self):
        return self._active

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
        if self.__what:
            return self.__what
        if self._value is None:
            return "Value is not set!"
        value = self._value.formatValue(F.next())
        return f"{self._active} : {value}"
