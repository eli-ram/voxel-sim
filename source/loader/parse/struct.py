from typing import Any

from .error import ParseError
from .indent import Fmt
from .parsable import Parsable
from .utils import formatIter, isParsableType
from .types import isMap


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

    def dataParse(self, data: Any):
        data = data or {}

        # Require a map
        if not isMap(data):
            raise ParseError("Expected a Map of Properties")

        # Update & Check for changes / errors
        for field, parsable in self._fields.items():
            yield parsable, data.get(field)

    def format(self, F: Fmt) -> str:
        return formatIter(self, F, "{}:", self._fields.items())
