from typing import Any

from .p_types import isArray, isMap
from .error import CastError
from .p_value import Value
from .utils import wrapCast

def _empty(*args, **kwgs):
    pass

class Empty(Value[None]):
    generic = _empty

class Int(Value[int]):

    @wrapCast
    def parseValue(self, data: Any):
        return None if data is None else int(data)

    def toString(self, value: int) -> str:
        return f"{value:6}"


class Float(Value[float]):

    @wrapCast
    def parseValue(self, data: Any):
        return float(data)

    def toString(self, value: float) -> str:
        return f"{value:6.3f}"


class String(Value[str]):

    @wrapCast
    def parseValue(self, data: Any):
        return str(data).strip()

    def toString(self, value: str) -> str:
        return f"'{value}'"


class Bool(Value[bool]):

    MAP = {
        # True Options
        1: True,
        True: True,
        "true": True,
        "True": True,
        # False Options
        0: False,
        False: False,
        "false": False,
        "False": False,
    }

    def parseValue(self, data: Any):
        if data is None:
            return None
        if isMap(data) or isArray(data):
            raise CastError("Expected a Value")
        try:
            return self.MAP[data]
        except KeyError:
            raise CastError(f"Cannot convert to Bool. ({data})")
