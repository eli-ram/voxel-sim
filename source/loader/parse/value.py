from typing import Optional, TypeVar

from .indent import Fmt
from .generic import Generic
from .parsable import Parsable
from .types import Any, Map, Array, isMap, isArray
from .utils import safeParse

T = TypeVar('T')

class Value(Parsable, Generic[T]):
    """ Value Parsable base for literal fields """
    value: Optional[T] = None

    def fromNone(self) -> Optional[T]:
        return None

    def fromMap(self, data: Map) -> Optional[T]:
        return self.generic(**data)

    def fromArray(self, data: Array) -> Optional[T]:
        return self.generic(*data)

    def fromValue(self, data: Any) -> Optional[T]:
        return self.generic(data)

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

    def hasChanged(self, old: Optional[T], new: Optional[T]):
        if old is None or new is None:
            return not old is new

        return not self.isEqual(old, new)

    @safeParse
    def parse(self, data: Any):
        old = self.value
        new = self.parseValue(data)
        self.value = new
        self.changed = self.hasChanged(old, new)
        
    def format(self, F: Fmt) -> str:
        E = F.format.list_errors
        if E and self.error:
            return self.what

        if self.value is None:
            return "none"

        return self.toString(self.value)

    def exists(self):
        return not self.value is None

    def getOr(self, default: T) -> T:
        if self.value is None:
            return default
        return self.value

    def get(self) -> Optional[T]:
        return self.value
