from typing import Any, Dict, Generic, TypeVar, cast
from .indent import Fmt
from .parsable import Parsable
from .error import ParseError
from .utils import generic, formatMap, safeParse, linkParse

P = TypeVar('P', bound=Parsable)

class Map(Parsable, Generic[P]):
    map: Dict[str, P]

    def __init__(self) -> None:
        self.map = {}

    @safeParse
    def parse(self, data: Any):
        data = data or {}

        if not isinstance(data, dict):
            raise ParseError("Expected a Map")

        map = cast(Dict[str, Any], data)
        cls = generic(self)
        V = set(self.map)
        D = set(map)

        # Baseline for change
        self.changed = D != V

        # Create
        for key in D - V:
            print(f"Create: {key}")
            self.map[key] = cls()

        # Delete
        for key in V - D:
            print(f"Delete: {key}")
            self.map.pop(key)

        # Parse & Check changes / errors
        for key, parsable in self.map.items():
            linkParse(self, parsable, map.get(key))

    def format(self, F: Fmt) -> str:
        return formatMap(self, self.map, F)

    def __getitem__(self, key: str) -> P:
        return self.map[key]
