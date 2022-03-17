from typing import Any, Dict, List, Optional, TypeVar

from .indent import Fmt
from .generic import Generic
from .parsable import Parsable
from . import utils

T = TypeVar('T')

class Value(Parsable, Generic[T]):
    """ Value Parsable base for literal fields """
    value: Optional[T] = None

    def fromNone(self) -> Optional[T]:
        return None

    def fromMap(self, data: Dict[str, Any]) -> Optional[T]:
        return self.generic(**data)

    def fromArray(self, data: List[Any]) -> Optional[T]:
        return self.generic(*data)

    def fromValue(self, data: Any) -> Optional[T]:
        return self.generic(data)

    @utils.wrapCast
    def parseValue(self, data: Any) -> Optional[T]:
        """ Cast data to new value """
        if data is None:
            return self.fromNone()
        elif utils.isMap(data):
            return self.fromMap(data)
        elif utils.isArray(data):
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
        if old is None:
            return not new is None

        if new is None:
            return True

        return not self.isEqual(old, new)

    @utils.safeParse
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

    def __bool__(self) -> bool:
        return self.value is not None
