from __future__ import annotations
import numpy as np

__all__ = [
    "Box",
    "int3",
    "float3",
]

int2 = tuple[int, int]
int3 = tuple[int, int, int]
float3 = tuple[float, float, float]

vector = np.ndarray[np.int64]
vec3 = int3 | vector


def _vec(*v: int):
    # Convert int tuple to array
    return np.array(v, np.int64)  # type: ignore


class Box:
    """ A construct to handle shifted dense arrays

        from {start} until {stop}

    """

    def __init__(self, start: vector, stop: vector):
        assert start.shape == stop.shape == (3,), \
            " [start] & [stop] must have a shape of (3,) "
        self.start = start
        self.stop = stop

    @staticmethod
    def StartStop(start: vec3, stop: vec3) -> Box:
        """ Create a box from [start] to [stop] """
        return Box(_vec(*start), _vec(*stop))

    @staticmethod
    def OffsetShape(offset: vec3, shape: vec3) -> Box:
        """ Create a box @ [offset] with [shape] """
        start = _vec(*offset)
        stop = start + _vec(*shape)
        return Box(start, stop)

    @staticmethod
    def Empty():
        """ Make an Empty Box """
        return Box(_vec(0, 0, 0), _vec(0, 0, 0))

    @staticmethod
    def Union(boxes: list[Box]) -> Box:
        """ Create the union of multiple boxes """
        return _combine(boxes, np.min, np.max)

    @staticmethod
    def Intersection(boxes: list[Box]) -> Box:
        """ Create the intersection of multiple boxes """
        return _combine(boxes, np.max, np.min)

    @property
    def size(self):
        """ Get the size of this box as a numpy array """
        return self.stop - self.start

    @property
    def center(self) -> float3:
        """ Get the center of this box (float3) """
        return tuple((self.start + self.stop) * 0.5)

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

        def span(*axes: int):
            B = data.any(axes)
            L = int(B[::+1].argmax())
            H = int(B[::-1].argmax())
            return L, B.size-H

        O = self.start
        lx, hx = span(1, 2)
        ly, hy = span(2, 0)
        lz, hz = span(0, 1)
        return Box(O + _vec(lx, ly, lz), O + _vec(hx, hy, hz))

    def offset(self, amount: vec3):
        O = _vec(*amount)
        return Box(O + self.start, O + self.stop)

    def __str__(self) -> str:
        return f"Box({self.start} -> {self.stop})"

    def __eq__(self, o: object) -> bool:
        return (
            isinstance(o, Box) and
            np.array_equal(self.start, o.start) and
            np.array_equal(self.stop, o.stop)
        )


def _combine(boxes: list[Box], start, stop):
    if not boxes:
        return Box.Empty()
    return Box(
        start(np.stack([b.start for b in boxes]), axis=0),
        stop(np.stack([b.stop for b in boxes]), axis=0),
    )


if __name__ == '__main__':
    # Test data
    A = Box.StartStop(
        (0, 4, 4),
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
    mask[2, 1:3, 0:3] = True
    E = A.crop(mask)
    # print(mask)
    # print(E, E.shape)

    F = E.offset((2, 4, 3))

    # Tests
    assert Box.Empty().is_empty
    assert not A.is_empty
    assert A.shape == (4, 4, 4)
    assert np.array_equal(B.stop, _vec(8, 8, 8))
    assert not A.overlap(B)
    assert B.overlap(C)
    assert B.slice(C) == (slice(1, 4), slice(0, 2), slice(2, 4))
    assert all(D.overlap(box) for box in [A, B, C])
    assert E.shape == (1, 2, 3)
    assert np.array_equal(E.start, _vec(2, 5, 4))
    assert F.shape == (1, 2, 3)
    assert np.array_equal(F.start, _vec(4, 9, 7))
