from typing import Any, Dict, cast

from .error import ParseError
from .indent import Fmt
from .parsable import Parsable
from .utils import isParsableType, formatMap, safeParse

class Struct(Parsable):
    """ Auto Parsable base for annotated fields """

    @classmethod
    def initFields(cls) -> Dict[str, Parsable]:
        items = cls.__annotations__.items()
        return {attr: type() for attr, type in items if isParsableType(type)}

    def __init__(self) -> None:
        self._fields = self.initFields()
        for field, parsable in self._fields.items():
            setattr(self, field, parsable)

    @safeParse
    def parse(self, data: Any):
        data = data or {}
        if not isinstance(data, dict):
            raise ParseError("Expected a Map of Properties")

        map = cast(Dict[str, Any], data)

        # Baseline for Change
        self.changed = False

        # Update & Check for changes
        for field, parsable in self._fields.items():
            parsable.parse(map.get(field))
            self.changed |= parsable.changed

        # Check for Errors
        if any(p.error for p in self._fields.values()):
            raise ParseError()

    def format(self, F: Fmt) -> str:
        return formatMap(self, self._fields, F)
