from typing import Any, Generic, TypeVar
from .indent import Indent
from .parsable import Parsable

T = TypeVar('T')

class Value(Parsable, Generic[T]):
    """ Value Parsable base for literal fields """
    value: T

    def validate(self, data: Any) -> T:
        raise NotImplementedError()

    def parse(self, data: Any):
        self.value = self.validate(data)

    def format(self, I: Indent) -> str:
        return str(self.value)

    def __bool__(self) -> bool:
        return self.value is None
