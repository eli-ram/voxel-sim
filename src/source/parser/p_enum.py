
from typing import Optional, TypeVar, Generic
from .indent import Fmt
from .error import ParseError
from .parsable import Parsable
from .p_types import getAnnotations, Any, isMap

I = TypeVar('I')


def _fmt_keys(dct: dict[str, Any]):
    return ",".join(f'"{k}"' for k in dct)

class Enum(Parsable, Generic[I]):
    """ Externally tagged enum """

    def __init__(self) -> None:
        self.__enum = getAnnotations(self)
        self.__active: Optional[str] = None
        self.__value: Optional[Parsable] = None

    def ok(self):
        return self.__value is not None

    def get(self) -> Optional[I]:
        return self.__value  # type: ignore

    def require(self) -> I:
        if self.__value is None:
            raise ParseError("Enum is not set!")
        return self.__value  # type: ignore

    def variant(self) -> str:
        if self.__active is None:
            raise ParseError("Enum is not set!")
        return self.__active

    def dataParse(self, data: Any):
        data = data or {}

        if not isMap(data):
            raise ParseError("Expected a Map for Enum option")

        if len(data) != 1:
            keys = _fmt_keys(data)
            raise ParseError(f"Enum can only have one(1) value (found: {keys})")

        key, value = next(iter(data.items()))

        if key not in self.__enum:
            options = _fmt_keys(self.__enum)
            raise ParseError(f"Invalid Enum option (use: {options})")

        if key != self.__active:
            self.setChanged(True)
            self.__value = self.__enum[key]()
            self.__active = key

        yield self.__value, value

    def formatValue(self, F: Fmt) -> str:
        if self.getError():
            return self.getError()
        if self.__value is None:
            return "Value is not set!"
        value = self.__value.formatValue(F.next())
        return f"{self.__active} : {value}"
