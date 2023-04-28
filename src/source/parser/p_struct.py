from typing import Any

from .error import ParseError
from .indent import Fmt
from .parsable import Parsable
from .utils import formatIter, isParsableType
from .p_types import isMap, getAnnotations

class Struct(Parsable):
    """ Auto Parsable base for annotated fields """

    def initFields(self):
        fields = dict[str, Parsable]()
        for field, type in getAnnotations(self).items():
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
            yield parsable, data.pop(field, None)

        # Report unused fields
        if data:
            wrong = ",".join(f'"{k}"' for k in data)
            valid = ",".join(f'"{k}"' for k in self._fields)
            raise ParseError(f"Bad fields found! \n\t(wrong: {wrong})\n\t(valid: {valid})")


    def formatValue(self, F: Fmt) -> str:
        return formatIter(self, F, "{}:", self._fields.items())
