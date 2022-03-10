from typing import Any, Generic, Optional, TypeVar

from source.loader.parse.utils import formatValue, safeParse
from .indent import Fmt
from .parsable import Parsable

T = TypeVar('T')

class Value(Parsable, Generic[T]):
    """ Value Parsable base for literal fields """
    value: Optional[T] = None

    def validate(self, data: Any) -> Optional[T]:
        """ Validate and return new value """
        raise NotImplementedError()

    def compare(self, old: T, new: T) -> bool:
        """ Compare old and new value """
        return old == new

    def string(self, value: T) -> str:
        """ Convert value to string """
        return str(value)

    def hasChanged(self, old: Optional[T], new: Optional[T]):
        if old is None:
            return not new is None

        if new is None:
            return True

        return not self.compare(old, new)

    @safeParse
    def parse(self, data: Any):
        old = self.value
        new = self.validate(data)
        self.value = new
        self.changed = self.hasChanged(old, new)
        
    def format(self, F: Fmt) -> str:
        if self.value is None:
            string = ''
        else:
            string = self.string(self.value)
        return formatValue(self, string, F)
