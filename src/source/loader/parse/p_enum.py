
from typing import Optional, TypeVar, Generic
from .utils import formatIter
from .indent import Fmt
from .error import ParseError
from .parsable import Parsable
from .p_types import getAnnotations, Any, isMap

I = TypeVar('I')


class Enum(Parsable, Generic[I]):

    __active: str
    __value: Optional[Parsable] = None

    def __init__(self) -> None:
        self.__enum = getAnnotations(self)

    def ok(self):
        return self.__value is not None

    def get(self) -> Optional[I]:
        return self.__value  # type: ignore

    def require(self) -> I:
        if self.__value is None:
            raise ParseError("Enum is not set!")
        return self.__value  # type: ignore

    def variant(self):
        return self.__active

    def dataParse(self, data: Any):
        data = data or {}

        if not isMap(data):
            raise ParseError("Expected a Map for Enum option")

        if len(data) != 1:
            raise ParseError("Enum can only have one(1) value")

        key, value = next(iter(data.items()))

        if key not in self.__enum:
            options = ",".join(f'"{key}"' for key in self.__enum)
            raise ParseError(f"Invalid Enum option (use: {options})")

        if key != self.__active:
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
