from typing import Any

from .error import CastError
from .value import Value
from .utils import wrapCast


class Int(Value[int]):

    @wrapCast
    def parseValue(self, data: Any):
        return int(data)

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
        return str(data)

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
        try:
            return self.MAP[data]
        except KeyError:
            raise CastError(f"Cannot convert to Bool. ({data})")
