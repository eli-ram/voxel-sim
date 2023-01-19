from typing import Callable, Optional, TypeVar

from .error import ParseError
from .indent import Fmt
from .generic import Generic
from .parsable import Parsable
from .p_types import Any, Map, Array, isMap, isArray

T = TypeVar('T')


class Value(Parsable, Generic[T]):
    """ Value Parsable base for literal fields """
    __value: Optional[T] = None

    def maybe(self) -> Optional[T]:
        return self.__value

    def require(self) -> T:
        if self.__value is None:
            type = Generic.name(self)
            err = f"Value[{type}] is missing!"
            raise ParseError(err)
        return self.__value

    def fromNone(self) -> Optional[T]:
        return None

    def fromMap(self, data: Map) -> Optional[T]:
        return Generic.get(self)(**data)

    def fromArray(self, data: Array) -> Optional[T]:
        return Generic.get(self)(*data)

    def fromValue(self, data: Any) -> Optional[T]:
        return Generic.get(self)(data)

    def parseValue(self, data: Any) -> Optional[T]:
        """ Cast data to new value """
        if data is None:
            return self.fromNone()
        elif isMap(data):
            return self.fromMap(data)
        elif isArray(data):
            return self.fromArray(data)
        else:
            return self.fromValue(data)

    def isEqual(self, old: T, new: T) -> bool:
        """ Compare old and new value """
        return old == new

    def toString(self, value: T) -> str:
        """ Convert value to string """
        return str(value)

    def checkChange(self, old: Optional[T], new: Optional[T]):
        print(old, "=>", new)
        if old is None or new is None:
            return not (old is new)

        return not self.isEqual(old, new)

    def dataParse(self, data: Any):
        print("[VALUE]", self.__class__.__name__)
        print("[ENTER]", self.hasChanged())
        old = self.__value
        new = self.parseValue(data)
        self.__value = new
        # Bypass name-wrangling
        self._Parsable__changed = self.checkChange(old, new)
        print("[EXIT]", self.hasChanged())

    def formatValue(self, F: Fmt) -> str:
        E = F.format.list_errors
        if E and self.hasError():
            return self.getError()

        if self.__value is None:
            return "none"

        return self.toString(self.__value)

    def exists(self):
        return not self.__value is None

    def getOr(self, default: T) -> T:
        if self.__value is None:
            return default
        return self.__value

    def get(self) -> Optional[T]:
        return self.__value
