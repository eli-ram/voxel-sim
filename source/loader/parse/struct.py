from __future__ import annotations
from typing import Any, Dict, cast

from .error import ParseError
from .indent import Fmt
from .parsable import Parsable
from .utils import formatStruct, isParsableType, safeParse, linkParse

class Struct(Parsable):
    """ Auto Parsable base for annotated fields """

    @classmethod
    def getAnnotations(cls):
        annotations = dict[str, Any]()
        for C in reversed(cls.mro()):
            if hasattr(C, '__annotations__'):
                annotations.update(C.__annotations__)
        return annotations

    def initFields(self):
        fields = dict[str, Parsable]()
        for field, type in self.getAnnotations().items():
            if isParsableType(type):
                parsable = type()
                fields[field] = parsable
                setattr(self, field, parsable)
        return fields

    def __init__(self) -> None:
        self._fields = self.initFields()

    @safeParse
    def parse(self, data: Any):
        data = data or {}
        if not isinstance(data, dict):
            raise ParseError("Expected a Map of Properties")

        map = cast(Dict[str, Any], data)

        # Baseline for Change
        self.changed = False

        # Update & Check for changes / errors
        for field, parsable in self._fields.items():
            linkParse(self, parsable, map.get(field))

    def format(self, F: Fmt) -> str:
        return formatStruct(self, self._fields, F)
