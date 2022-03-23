from __future__ import annotations
from typing import Dict

import numpy as np
from .operation import Operation

class impl:
    __all__: Dict[Operation, impl] = {}
    OP: Operation

    def __init_subclass__(cls, op: Operation) -> None:
        cls.OP = op
        cls.__all__[op] = cls()

    @classmethod
    def get(cls, op: Operation) -> impl:
        if op not in cls.__all__:
            cls.__init_subclass__(op)
        return cls.__all__[op]

    def where(self, parent: np.ndarray[np.bool_], child: np.ndarray[np.bool_]) -> np.ndarray[np.bool_]:
        raise NotImplementedError(f"Missing Operation: {self.OP}")


class _(impl, op=Operation.INSIDE):
    def where(self, parent, child) -> np.ndarray[np.bool_]:
        return parent & child

class _(impl, op=Operation.OUTSIDE):
    def where(self, parent, child) -> np.ndarray[np.bool_]:
        return ~parent & child

class _(impl, op=Operation.OVERWRITE):
    def where(self, parent, child) -> np.ndarray[np.bool_]:
        return child
