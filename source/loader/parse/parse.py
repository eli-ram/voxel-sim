
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from .utils import Indent
from .base import Parsable
from .fmt import Fmt


T = TypeVar('T')
P = TypeVar('P', bound=Parsable)


class ValueParsable(Parsable, Generic[T]):
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


class MapParsable(Parsable, Generic[P]):
    child: Type[P]
    values: Dict[str, P]

    def __init__(self) -> None:
        self.values = {}

    def create(self) -> P:
        return self.child()

    def parse(self, data: Optional[Dict[str, Any]]):
        data = data or {}
        V = set(self.values)
        D = set(data)

        # Create
        for key in D - V:
            print(f"Create: {key}")
            self.values[key] = self.create()

        # Delete
        for key in V - D:
            print(f"Delete: {key}")
            self.values.pop(key)

        # Parse
        for key, parsable in self.values.items():
            parsable.parse(data.get(key))

    def format(self, I: Indent) -> str:
        return Fmt.ParsableDict(self.values, I)

    def __getitem__(self, key: str) -> P:
        return self.values[key]


class ListParsable(Parsable, Generic[P]):
    child: Type[P]
    values: List[P]

    def __init__(self) -> None:
        self.values = []

    def create(self) -> P:
        return self.child()

    def parse(self, data: Optional[List[Any]]):
        data = data or []
        V = len(self.values)
        D = len(data)

        # Create
        for index in range(V, D):
            print(f"Create: {index}")
            self.values.append(self.create())

        # Delete
        for index in range(V, D, -1):
            print(f"Delete: {index}")
            self.values.pop()

        # Parse
        for parsable, value in zip(self.values, data):
            parsable.parse(value)

    def format(self, I: Indent) -> str:
        return Fmt.ParsableList(self.values, I)

    def __getitem__(self, index: int) -> P:
        return self.values[index]
