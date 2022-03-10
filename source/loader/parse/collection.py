from typing import Any, Dict, Generic, List, TypeVar, cast
from .indent import Fmt
from .parsable import Parsable
from .error import ParseError
from .utils import generic, formatMap, formatArray, safeParse

P = TypeVar('P', bound=Parsable)

class Map(Parsable, Generic[P]):
    map: Dict[str, P]

    def __init__(self) -> None:
        self.map = {}

    @safeParse
    def parse(self, data: Any):
        data = data or {}

        if not isinstance(data, dict):
            raise ParseError("Expected a Map")

        map = cast(Dict[str, Any], data)
        cls = generic(self)
        V = set(self.map)
        D = set(map)

        # Baseline for change
        self.changed = D != V

        # Create
        for key in D - V:
            print(f"Create: {key}")
            self.map[key] = cls()

        # Delete
        for key in V - D:
            print(f"Delete: {key}")
            self.map.pop(key)

        # Parse & Check changes
        for key, parsable in self.map.items():
            parsable.parse(map.get(key))
            self.changed |= parsable.changed

        # Check Errors
        if any(p.error for p in self.map.values()):
            raise ParseError()

    def format(self, F: Fmt) -> str:
        return formatMap(self, self.map, F)

    def __getitem__(self, key: str) -> P:
        return self.map[key]

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

        # Parse & Check for changes
        for parsable, value in zip(self.array, array):
            parsable.parse(value)
            self.changed |= parsable.changed

        # Check Errors
        if any(p.error for p in self.array):
            raise ParseError()


    def format(self, F: Fmt) -> str:
        return formatArray(self, self.array, F)

    def __getitem__(self, index: int) -> P:
        return self.array[index]
