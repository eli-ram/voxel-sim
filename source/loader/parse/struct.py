from typing import Any

from .error import ParseError
from .indent import Fmt
from .parsable import Parsable
from .utils import safeParse, formatIter, isParsableType
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

    def postParse(self):
        """ Validate the struct after parsing (changed=True and error=False)"""

    @safeParse
    def parse(self, data: Any):
        data = data or {}

        # Require a map
        if not isMap(data):
            raise ParseError("Expected a Map of Properties")

        # Baseline for Change
        self.changed = False

        # Update & Check for changes / errors
        for field, parsable in self._fields.items():
            self.link(parsable.parse(data.get(field)))
            if self.error: print(field)

        # Allow Derived class to post-parse
        if self.changed:
            self.postParse()

    def format(self, F: Fmt) -> str:
        return formatIter(self, F, "{}:", self._fields.items())
