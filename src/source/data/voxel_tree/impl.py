from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

from .box import Box
from .data import Data
from .operation import Operation

Boxed = Tuple[Data, Box]


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

    def apply(self, parent: Data, child: Data):
        # Find intersection
        B = Box.Intersection([parent.box, child.box])
        if B.is_empty:
            return

        # Slice
        P = parent[B]
        C = child[B]

        # Where
        M = self.where(P, C)

        # Apply
        for p, c in zip(P.arrays(), C.arrays()):
            p[M] = c[M]

    def where(self, parent: Data, child: Data) -> np.ndarray[np.bool_]:
        raise NotImplementedError(f"Missing Operation: {self.OP}")


class _(impl, op=Operation.INSIDE):
    """Place the child inside the parent"""

    def where(self, parent, child) -> np.ndarray[np.bool_]:
        return parent.mask & child.mask


class _(impl, op=Operation.OUTSIDE):
    """Place the child outside the parent"""

    def where(self, parent, child) -> np.ndarray[np.bool_]:
        return ~parent.mask & child.mask


class _(impl, op=Operation.OVERWRITE):
    """Place the child regardless of parent"""

    def where(self, parent, child) -> np.ndarray[np.bool_]:
        return child.mask


class _(impl, op=Operation.CUTOUT):
    """Remove the child from the parent"""

    def apply(self, parent: Data, child: Data):
        # Find intersection
        B = Box.Intersection([parent.box, child.box])

        # Get mask
        M = ~(child[B].mask)

        # Copy intersection data
        D = [a[M] for a in parent[B].arrays()]

        # Zero out parent
        for a in parent.arrays():
            a[...] = 0

        # Fill in intersection
        for a, d in zip(parent[B].arrays(), D):
            a[M] = d


class _(impl, op=Operation.INTERSECT):
    """Keep only overlapping regions of parent"""

    def apply(self, parent: Data, child: Data):
        # Find intersection
        B = Box.Intersection([parent.box, child.box])

        # Get mask
        M = child[B].mask

        # Copy intersection data
        D = [a[M] for a in parent[B].arrays()]

        # Zero out parent
        for a in parent.arrays():
            a[...] = 0

        # Fill in intersection
        for a, d in zip(parent[B].arrays(), D):
            a[M] = d
