from __future__ import annotations

from itertools import combinations
from typing import Iterable, Tuple

import numpy as np

__all__ = [
    "Box",
    "int3",
]

int3 = Tuple[int, int, int]

class Box:
    """ A construct to handle shifted dense arrays """

    def __init__(self, start: np.ndarray[np.int64], stop: np.ndarray[np.int64]):
        assert start.shape == stop.shape == (3,), \
            " [start] & [stop] must have a shape of (3,) "
        self.start = start
        self.stop = stop

    @staticmethod
    def StartStop(start: int3, stop: int3) -> Box:
        """ Create a box from [start] to [stop] """
        return Box(_array(start), _array(stop))

    @staticmethod
    def OffsetShape(offset: int3, shape: int3) -> Box:
        """ Create a box @ [offset] with [shape] """
        start = _array(offset)
        stop = start + _array(shape)
        return Box(start, stop)

    @staticmethod
    def Empty():
        """ Make an Empty Box """
        return Box(np.zeros(3, np.int64), np.zeros(3, np.int64))

    @staticmethod
    def Union(boxes: Iterable[Box]) -> Box:
        """ Create the union of multiple boxes """
        return _combine(boxes, np.min, np.max)

    @staticmethod
    def Intersection(boxes: Iterable[Box]) -> Box:
        """ Create the intersection of multiple boxes """
        return _combine(boxes, np.max, np.min)

    @property
    def shape(self) -> int3:
        """ Get the shape of this box """
        return tuple(self.stop - self.start)

    @property
    def is_empty(self):
        return (self.start >= self.stop).any()
        
    @property
    def has_volume(self):
        """ Check if this box has volume """
        return (self.start < self.stop).all()

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

def _combine(boxes: Iterable[Box], start, stop):
    # Discard boxes with no volume
    boxes = [b for b in boxes if b.has_volume]

    # No boxes -> empty box
    if not boxes:
        return Box.Empty()

    # Combine the boxes
    return Box(
        start(np.stack([b.start for b in boxes]), axis=0),
        stop(np.stack([b.stop for b in boxes]), axis=0),
    )


def _array(v: int3):
    # Convert int tuple to array
    return np.array(list(v), np.int64)


if __name__ == '__main__':
    A = Box.StartStop(
        (1, 4, 4),
        (4, 8, 8),
    )

    B = Box.OffsetShape(
        (4, 4, 4),
        (4, 4, 4),
    )

    C = Box.StartStop(
        (5, 2, 6),
        (9, 6, 8),
    )

    D = Box.Union([A, B, C])

    mask = np.full(A.shape, False)
    mask[2, 2, 2] = True
    E = A.crop(mask)

    assert Box.Empty().is_empty
    assert not A.overlap(B)
    assert B.overlap(C)
    assert B.slice(C) == (slice(1, 4), slice(0, 2), slice(2, 4))
    assert all(D.overlap(box) for box in [A, B, C])
    assert E.shape == (1, 1, 1)
