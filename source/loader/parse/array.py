from typing import Any, List, TypeVar
from .indent import Fmt
from .parsable import Parsable
from .generic import Generic
from .error import ParseError
from . import utils, types

P = TypeVar('P', bound=Parsable)

class Array(Parsable, Generic[P]):
    _array: List[P]

    def __init__(self) -> None:
        self._array = []

    @utils.safeParse
    def parse(self, data: Any):
        data = data or []

        if not types.isArray(data):
            raise ParseError("Expected an Array")

        T = self.generic
        V = len(self._array)
        D = len(data)

        # Baseline for change
        self.changed = V != D

        # Create
        for index in range(V, D):
            print(f"Create: {index}")
            self._array.append(T())

        # Delete
        for index in range(V, D, -1):
            print(f"Delete: {index}")
            self._array.pop()

        # Parse & Check for changes / errors
        for parsable, value in zip(self._array, data):
            self.link(parsable, value)

    def format(self, F: Fmt) -> str:
        return utils.formatIter(self, F, "[{}]:", enumerate(self._array))

    def __iter__(self):
        return iter(self._array)

    def __getitem__(self, index: int) -> P:
        return self._array[index]
