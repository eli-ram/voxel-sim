from typing import Any, Dict, TypeVar
from .indent import Fmt
from .parsable import Parsable
from .generic import Generic
from .error import ParseError
from . import utils

P = TypeVar('P', bound=Parsable)

class Map(Parsable, Generic[P]):
    map: Dict[str, P]

    def __init__(self) -> None:
        self.map = {}

    @utils.safeParse
    def parse(self, data: Any):
        data = data or {}

        if not utils.isMap(data):
            raise ParseError("Expected a Map")

        T = self.generic
        V = set(self.map)
        D = set(data)

        # Baseline for change
        self.changed = D != V

        # Create
        for key in D - V:
            print(f"Create: {key}")
            self.map[key] = T()

        # Delete
        for key in V - D:
            print(f"Delete: {key}")
            self.map.pop(key)

        # Parse & Check changes / errors
        for key, parsable in self.map.items():
            utils.linkParse(self, parsable, data.get(key))

    def format(self, F: Fmt) -> str:
        return utils.formatIter(self, F, "[{}]:", self.map.items()) 

    def __getitem__(self, key: str) -> P:
        return self.map[key]
