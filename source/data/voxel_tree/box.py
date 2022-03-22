from __future__ import annotations
from typing import List
import numpy as np


class Box:
    """ A construct to handle shifted dense arrays """

    def __init__(self, start: np.ndarray[np.int64], stop: np.ndarray[np.int64]):
        assert start.shape == stop.shape == (3,), \
            " [start] & [stop] must have a shape of (3,) "
        assert np.all(start < stop), \
            " [start] must be less than [stop] "
        self.start = start
        self.stop = stop

    @property
    def shape(self):
        return tuple(self.stop - self.start)

    def overlap(self, other: Box):
        return (
            (self.start < other.stop).all()
            and
            (self.stop > other.start).all()
        )

    def slice(self, other: Box):
        start = np.maximum(self.start, other.start) - self.start
        stop = np.minimum(self.stop, other.stop) - self.start
        return tuple(slice(l, h) for l, h in zip(start, stop))

    @classmethod
    def combine(cls, boxes: List[Box]) -> Box:
        start = np.min(np.stack([b.start for b in boxes]), axis=0)
        stop = np.max(np.stack([b.stop for b in boxes]), axis=0)
        return cls(start, stop)

    @staticmethod
    def vec(a: int, b: int, c: int) -> np.ndarray[np.int64]:
        A = np.empty(3, np.int64)
        A[:] = a, b, c
        return A

    def __str__(self) -> str:
        return f"Box({self.start} -> {self.stop})"


if __name__ == '__main__':

    A = Box(
        Box.vec(1, 4, 4),
        Box.vec(4, 8, 8),
    )

    B = Box(
        Box.vec(4, 4, 4),
        Box.vec(8, 8, 8),
    )

    C = Box(
        Box.vec(5, 2, 6),
        Box.vec(9, 6, 8),
    )

    D = Box.combine([A, B, C])

    assert not A.overlap(B)
    assert B.overlap(C)
    assert B.slice(C) == (slice(1, 4), slice(0, 2), slice(2, 4))
    assert all(D.overlap(box) for box in [A, B, C])

