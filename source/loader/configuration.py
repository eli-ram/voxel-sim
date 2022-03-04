from typing import Dict, List
from .parse import Params, AutoParsable, ValueParsable
from .geometry import Geometry
from .literal import Data

class ColorMap(ValueParsable[Dict[str, List[float]]]):

    def parse(self, data: Params):
        data = data or {}
        self.value = data

    def format(self, indent: str) -> str:
        return "".join(f"\n{indent}{k}: {v}" for k, v in self.value.items())

class GeometryMap(ValueParsable[Dict[str, Geometry]]):

    def parse(self, data: Params):
        data = data or {}
        def make(data: Params):
            obj = Geometry()
            obj.parse(data)
            return obj
        self.value = {k:make(v)for k, v in data.items() }

    def format(self, indent: str) -> str:
        inner = indent + "  "
        return "".join(f"\n{indent}{k}:{v.format(inner)}" for k, v in self.value.items())

class Configuration(AutoParsable):
    config: Data
    colors: ColorMap
    geometry: GeometryMap
    parameters: Data
