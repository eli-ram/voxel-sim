from typing import Any
from .value import Value
from .error import CastError

class Int(Value[int]):
    def validate(self, data: Any):
        if not isinstance(data, int):
            raise CastError("Expected an Integer")
        return data

class Float(Value[float]):
    def validate(self, data: Any):
        if not isinstance(data, (int, float)):
            raise CastError("Expected a Float")
        return float(data)

class String(Value[str]):
    def validate(self, data: Any):
        if not isinstance(data, str):
            raise CastError("Expected a String")
        return data