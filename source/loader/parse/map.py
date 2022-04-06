from typing import Any, Dict, TypeVar
from .indent import Fmt
from .parsable import Parsable
from .generic import Generic
from .error import ParseError
from . import utils, types

P = TypeVar('P', bound=Parsable)

class Map(Parsable, Generic[P]):
    _map: Dict[str, P]

    def __init__(self) -> None:
        self._map = {}

    @utils.safeParse
    def parse(self, data: Any):
        data = data or {}

        if not types.isMap(data):
            raise ParseError("Expected a Map")

        T = self.generic
        V = set(self._map)
        D = set(data)

        # Baseline for change
        self.changed = D != V

        # Create
        for key in D - V:
            print(f"Create: {key}")
            self._map[key] = T()

        # Delete
        for key in V - D:
            print(f"Delete: {key}")
            self._map.pop(key)

        # Parse & Check changes / errors
        for key, parsable in self._map.items():
            self.link(parsable, data.get(key))

        # Use Values if all ok
        if self.changed and not self.error:
            self.post_validate()

    def post_validate(self):
        """ Validate values if needed """


    def format(self, F: Fmt) -> str:
        return utils.formatIter(self, F, "[{}]:", self._map.items()) 

    def __iter__(self):
        return iter(self._map.items())

    def __getitem__(self, key: str) -> P:
        return self._map[key]
