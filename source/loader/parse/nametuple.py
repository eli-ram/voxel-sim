from .parse import ValueParsable
from .error import ParseError
from .utils import generic
from typing import Any, NamedTuple, TypeVar

T = TypeVar('T', bound=NamedTuple)

class ParseNamedTuple(ValueParsable[T]):

    def validate(self, data: Any) -> T:
        T = generic(self)
        if isinstance(data, dict):
            return T(**data)
        if isinstance(data, list):
            return T(*data)
        if data is None:
            return T()
        raise ParseError("Expected an Array or a Map")
