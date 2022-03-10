from typing import Any, TypeVar, NamedTuple as __namedtuple__
from .value import Value
from .error import CastError
from .utils import generic

T = TypeVar('T', bound=__namedtuple__)

class NamedTuple(Value[T]):

    def validate(self, data: Any) -> T:
        T = generic(self)
        if isinstance(data, dict):
            return T(**data)
        if isinstance(data, list):
            return T(*data)
        if data is None:
            return T()
        raise CastError("Expected an Array or a Map")
