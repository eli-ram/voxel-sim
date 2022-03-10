from typing import Any, Dict, cast

from source.loader.parse.error import ParseError
from .utils import Indent
from .base import Parsable
from .fmt import Fmt

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

    def parse(self, data: Any):
        data = data or {}
        if not isinstance(data, dict):
            raise ParseError("Expected a Map of Properties")

        map = cast(Dict[str, Any], data)
        for name, parsable in self._fields.items():
            parsable.parse(map.get(name))

    def format(self, I: Indent) -> str:
        return Fmt.ParsableDict(self._fields, I)
