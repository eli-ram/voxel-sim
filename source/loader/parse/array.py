from typing import Any, Generic, List, TypeVar, cast
from .indent import Fmt
from .parsable import Parsable
from .error import ParseError
from .utils import generic, formatArray, safeParse, linkParse

P = TypeVar('P', bound=Parsable)

class Array(Parsable, Generic[P]):
    array: List[P]

    def __init__(self) -> None:
        self.array = []

    @safeParse
    def parse(self, data: Any):
        data = data or []

        if not isinstance(data, list):
            raise ParseError("Expected an Array")

        array = cast(List[Any], data)
        cls = generic(self)
        V = len(self.array)
        D = len(array)

        # Baseline for change
        self.changed = V != D

        # Create
        for index in range(V, D):
            print(f"Create: {index}")
            self.array.append(cls())

        # Delete
        for index in range(V, D, -1):
            print(f"Delete: {index}")
            self.array.pop()

        # Parse & Check for changes / errors
        for parsable, value in zip(self.array, array):
            linkParse(self, parsable, value)

    def format(self, F: Fmt) -> str:
        return formatArray(self, self.array, F)

    def __getitem__(self, index: int) -> P:
        return self.array[index]
