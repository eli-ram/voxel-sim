
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar


class Indent:
    def __init__(self, value: str, step: str, pad: str) -> None:
        self.value = value
        self.step = step
        self.pad = pad
        self.string = "\n" + self.value + self.pad

    def next(self):
        return Indent(self.value + self.step, self.step, self.pad)

    def __str__(self) -> str:
        return self.string

    def __add__(self, other: str) -> str:
        return self.string + other

    def __radd__(self, other: str) -> str:
        return other + self.string


class Parsable:
    """ Abstract Parsable Definition """

    def parse(self, data: Any): ...
    def format(self, I: Indent) -> str: ...

    def __str__(self) -> str:
        T = self.format(Indent("| ", "  ", ""))
        return f"\nv{T}\n^"


T = TypeVar('T')
P = TypeVar('P', bound=Parsable)


class Formatter:

    @staticmethod
    def fmt(V: Dict[str, str], I: Indent) -> str:
        W = len(V) and max(len(k) for k in V) + 1
        return "".join(I + k.ljust(W) + v for k, v in V.items())

    @classmethod
    def LiteralDict(cls, V: Dict[str, Any], I: Indent) -> str:
        return cls.fmt({f"{k}:": str(v) for k, v in V.items()}, I)

    @classmethod
    def LiteralList(cls, V: List[Any], I: Indent) -> str:
        return cls.fmt({f"[{i}]:": str(v) for i, v in enumerate(V)}, I)

    @classmethod
    def ParsableDict(cls, V: Dict[str, P], I: Indent) -> str:
        N = I.next()
        return cls.fmt({f"{k}:": v.format(N) for k, v in V.items()}, I)

    @classmethod
    def ParsableList(cls, V: List[P], I: Indent) -> str:
        N = I.next()
        return cls.fmt({f"[{i}]:": v.format(N) for i, v in enumerate(V)}, I)


def isParsable(T: Any) -> bool:
    P = type(Parsable)
    I = isinstance
    return I(T, P) or I(getattr(T, '__origin__'), P)

class AutoParsable(Parsable):
    """ Auto Parsable base for annotated fields """

    @classmethod
    def initFields(cls) -> Dict[str, Parsable]:
        items = cls.__annotations__.items()
        return {attr: type() for attr, type in items if isParsable(type)}

    def __init__(self) -> None:
        self._fields = self.initFields()
        for name, parsable in self._fields.items():
            setattr(self, name, parsable)

    def parse(self, data: Optional[Dict[str, Any]]):
        data = data or {}
        for name, parsable in self._fields.items():
            parsable.parse(data.get(name))

    def format(self, I: Indent) -> str:
        return Formatter.ParsableDict(self._fields, I)


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
        return Formatter.ParsableDict(self.values, I)

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
        return Formatter.ParsableList(self.values, I)

    def __getitem__(self, index: int) -> P:
        return self.values[index]
