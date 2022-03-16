from typing import Any
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