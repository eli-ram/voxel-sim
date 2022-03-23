from __future__ import annotations

from itertools import combinations
from typing import List, Tuple

import numpy as np

class Box:
    """ A construct to handle shifted dense arrays """

    @classmethod
    def Empty(cls):
        # Return an empty Box
        Z = np.zeros(3, np.int64)
        return cls(Z, Z)

    @classmethod
    def combine(cls, boxes: List[Box]) -> Box:
        # Filter empty boxes
        boxes = [box for box in boxes if not box.is_empty]

        # There is no boxes
        if not boxes:
            return cls.Empty()

        # Span all boxes
        start = np.min(np.stack([b.start for b in boxes]), axis=0)
        stop = np.max(np.stack([b.stop for b in boxes]), axis=0)
        return cls(start, stop)

    def __init__(self, start: np.ndarray[np.int64], stop: np.ndarray[np.int64]):
        assert start.shape == stop.shape == (3,), \
            " [start] & [stop] must have a shape of (3,) "
        assert np.all(start <= stop), \
            " [start] must be less than or equal [stop] "
        self.start = start
        self.stop = stop

    @property
    def shape(self):
        """ Get the shape of this box """
        return tuple(self.stop - self.start)

    @property
    def is_empty(self):
        """ Check if this box is empty """
        return (self.start == self.stop).any()

    def overlap(self, other: Box):
        """ Check if the boxes overlap """
        return (
            (self.start < other.stop).all()
            and
            (self.stop > other.start).all()
        )

    def slice(self, other: Box):
        """ Create slices that overlap the other Box """
        start = np.maximum(self.start, other.start) - self.start
        stop = np.minimum(self.stop, other.stop) - self.start
        return tuple(slice(l, h) for l, h in zip(start, stop))

    def crop(self, data: np.ndarray[np.bool_]):
        """ Create a Box that is as small as possible """

        assert data.shape == self.shape, \
            " Cropping [data] must be of equal shape as box "

        if not data.any():
            return Box.Empty()

        def span(axis: Tuple[int, int]):
            B = data.any(axis)
            L = int(B[::+1].argmax())
            H = int(B[::-1].argmax())
            return [L, B.size-H]

        axes = combinations(range(2, -1, -1), 2)
        start, stop = np.array([span(a) for a in axes]).T
        return Box(start + self.start, stop + self.start)


    def __str__(self) -> str:
        return f"Box({self.start} -> {self.stop})"

if __name__ == '__main__':
    def a(a, b, c):
        return np.array([a, b, c], np.int64)

    A = Box(
        a(1, 4, 4),
        a(4, 8, 8),
    )

    B = Box(
        a(4, 4, 4),
        a(8, 8, 8),
    )

    C = Box(
        a(5, 2, 6),
        a(9, 6, 8),
    )

    D = Box.combine([A, B, C])

    mask = np.full(A.shape, False)
    mask[2, 2, 2] = True
    E = A.crop(mask)

    assert not A.overlap(B)
    assert B.overlap(C)
    assert B.slice(C) == (slice(1, 4), slice(0, 2), slice(2, 4))
    assert all(D.overlap(box) for box in [A, B, C])
    assert E.shape == (1, 1, 1)
