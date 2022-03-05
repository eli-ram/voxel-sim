from typing import Any, Dict
from .parse import Indent, ValueParsable
import glm

class Int(ValueParsable[int]):
    def validate(self, data: Any):
        return int(data)

class Float(ValueParsable[float]):
    def validate(self, data: Any):
        return float(data)

class String(ValueParsable[str]):
    def validate(self, data: Any):
        return str(data)

class Data(ValueParsable[Dict[str, Any]]):
    def validate(self, data: Any):
        return data or {}

    def format(self, I: Indent) -> str:
        W = max(len(k) for k in self.value) + 2
        def F(key: str):
            return (key + ":").ljust(W)
        T = (I + F(k) + str(v) for k, v in self.value.items())
        return "".join(T)

class Vector(ValueParsable[glm.vec3]):
    default = glm.vec3()

    def validate(self, data: Any):
        if isinstance(data, (float, int)):
            return glm.vec3(data, data, data)
        if isinstance(data, list):
            return glm.vec3(*data)
        else:
            return self.default

    def format(self, I: Indent) -> str:
        x, y, z = self.value
        return f"Vector({x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"

class Quaternion(ValueParsable[glm.quat]):
    def validate(self, data: Any):
        # TODO
        return glm.quat()

    def format(self, I: Indent) -> str:
        w, x, y, z = self.value
        return f"Quaternion({w=: 6.3f}, {x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"
