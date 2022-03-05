
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar


Params = Optional[Dict[str, Any]]


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


class AutoParsable(Parsable):
    """ Auto Parsable base for annotated fields """

    @classmethod
    def initFields(cls) -> Dict[str, Parsable]:
        items = cls.__annotations__.items()
        return {k: v() for k, v in items if isinstance(v, type(Parsable))}

    def __init__(self) -> None:
        self._fields = self.initFields()
        for name, parsable in self.fields:
            setattr(self, name, parsable)

    @property
    def fields(self):
        return self._fields.items()

    def parse(self, data: Optional[Dict[str, Any]]):
        data = data or {}
        for name, parsable in self.fields:
            parsable.parse(data.get(name))

    def format(self, I: Indent) -> str:
        N = I.next()
        W = max(len(k) for k in self._fields) + 2
        def F(key: str):
            return (key + ":").ljust(W)
        T = (I + F(k) + v.format(N) for k, v in self.fields)
        return "".join(T)


T = TypeVar('T')


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


P = TypeVar('P', bound=Parsable)


class MapParsable(Parsable, Generic[P]):
    values: Dict[str, P]

    def __init__(self) -> None:
        base, = self.__orig_bases__  # type: ignore
        tcls, = base.__args__  # type: ignore
        self._cls: Type[P] = tcls
        self.values = {}

    def create(self) -> P: ...

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
        N = I.next()
        W = max(len(k) for k in self.values) + 2
        def F(key: str):
            return (key + ":").ljust(W)
        T = (I + F(k) + v.format(N) for k, v in self.values.items())
        return "".join(T)

class ListParsable(Parsable, Generic[P]):
    values: List[P]

    def __init__(self) -> None:
        base, = self.__orig_bases__  # type: ignore
        tcls, = base.__args__  # type: ignore
        self._cls: Type[P] = tcls
        self.values = []

    def create(self) -> P: ...

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
        N = I.next()
        W = len(str(len(self.values))) + 4
        def F(index: int):
            return (f"[{index}]:").ljust(W)
        T = (I + F(i) + v.format(N) for i, v in enumerate(self.values))
        return "".join(T)
