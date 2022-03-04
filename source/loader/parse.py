
from typing import Any, Dict, Generic, Optional, Type, TypeVar


Params = Optional[Dict[str, Any]]
T = TypeVar('T')


class Parsable:
    def parse(self, data: Params): ...
    def format(self, indent: str) -> str: ...
    def __str__(self) -> str:
        return self.format("")

class AutoParsable(Parsable):

    @classmethod
    def fields(cls) -> Dict[str, Type[Parsable]]:
        return cls.__annotations__

    def __init__(self) -> None:
        map = self.fields()
        self._attrs = {k: p() for k, p in map.items()}
        for name, parsable in self._attrs.items():
            setattr(self, name, parsable)

    def parse(self, data: Params):
        data = data or {}
        for name, parsable in self._attrs.items():
            parsable.parse(data.get(name))

    def format(self, indent: str) -> str:
        inner = indent + "  "
        return "".join(f"\n{indent}{k}: {v.format(inner)}" for k, v in self._attrs.items())

class ValueParsable(Parsable, Generic[T]):
    value: T

    def parse(self, data: Any): ...

    def format(self, indent: str) -> str:
        return str(self.value)