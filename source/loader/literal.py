from typing import Any, Dict
from .parse import Params, ValueParsable

class Int(ValueParsable[int]):
    def parse(self, data: Any):
        self.value = data

class String(ValueParsable[str]):
    def parse(self, data: Any):
        self.value = data

class Data(ValueParsable[Dict[str, Any]]):
    def parse(self, data: Params):
        self.value = data or {}

    def format(self, indent: str) -> str:
        return "".join(f"\n{indent}{k}: {v}" for k, v in self.value.items())
