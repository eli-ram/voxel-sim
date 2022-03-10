from typing import Any, Dict, Generic, List, TypeVar, cast
from .indent import Fmt
from .parsable import Parsable
from .error import ParseError
from .utils import generic, formatMap, formatArray

P = TypeVar('P', bound=Parsable)

class Map(Parsable, Generic[P]):
    values: Dict[str, P]

    def __init__(self) -> None:
        self.values = {}

    def parse(self, data: Any):
        data = data or {}

        if not isinstance(data, dict):
            raise ParseError("Expected a Map")

        map = cast(Dict[str, Any], data)
        cls = generic(self)
        V = set(self.values)
        D = set(map)

        # Baseline for change
        self.changed = D != V

        # Create
        for key in D - V:
            print(f"Create: {key}")
            self.values[key] = cls()

        # Delete
        for key in V - D:
            print(f"Delete: {key}")
            self.values.pop(key)

        # Parse & Check changes
        for key, parsable in self.values.items():
            parsable.parse(map.get(key))
            self.changed |= parsable.changed

    def format(self, F: Fmt) -> str:
        return formatMap(self.values, F)

    def __getitem__(self, key: str) -> P:
        return self.values[key]

class Array(Parsable, Generic[P]):
    values: List[P]

    def __init__(self) -> None:
        self.values = []

    def parse(self, data: Any):
        data = data or []

        if not isinstance(data, list):
            raise ParseError("Expected an Array")

        array = cast(List[Any], data)
        cls = generic(self)
        V = len(self.values)
        D = len(array)

        # Baseline for change
        self.changed = V != D

        # Create
        for index in range(V, D):
            print(f"Create: {index}")
            self.values.append(cls())

        # Delete
        for index in range(V, D, -1):
            print(f"Delete: {index}")
            self.values.pop()

        # Parse & Check for changes
        for parsable, value in zip(self.values, array):
            parsable.parse(value)
            self.changed |= parsable.changed

    def format(self, F: Fmt) -> str:
        return formatArray(self.values, F)

    def __getitem__(self, index: int) -> P:
        return self.values[index]
