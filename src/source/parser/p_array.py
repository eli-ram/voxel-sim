from typing import Any, List, TypeVar
from .indent import Fmt
from .parsable import Parsable
from .generic import Generic
from .error import ParseError
from . import p_types, utils

P = TypeVar('P', bound=Parsable)


class Array(Parsable, Generic[P]):
    _array: List[P]

    def __init__(self) -> None:
        self._array = []

    def dataParse(self, data: Any):
        data = data or []

        if not p_types.isArray(data):
            raise ParseError("Expected an Array")

        T = Generic.get(self)
        V = len(self._array)
        D = len(data)

        # Baseline for change
        self.setChanged(V != D)

        # Create
        for _ in range(V, D):
            self._array.append(T())

        # Delete
        for _ in range(V, D, -1):
            self._array.pop()

        # Parse & Check for changes / errors
        for parsable, value in zip(self._array, data):
            yield parsable, value

    def formatValue(self, F: Fmt) -> str:
        return utils.formatIter(self, F, "[{}]:", enumerate(self._array))

    def __iter__(self):
        return iter(self._array)

    def __getitem__(self, index: int) -> P:
        return self._array[index]
