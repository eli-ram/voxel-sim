# pyright: reportUnknownMemberType=false
from typing import Any, Union
import numpy as np
from dataclasses import dataclass

Float = Union[float, np.float32]
Point = Any  # np.ndarray[np.float32][x,y]


@dataclass
class Line:
    a: Point
    b: Point


def point(x: Float, y: Float) -> Point:
    return np.array([x, y], dtype=np.float32)


def diff(l: Line):
    return l.a - l.b


def det(A: Point, B: Point):
    a, b = A
    c, d = B
    return a * d - b * c


def intersect(a: Line, b: Line):
    ax, ay = diff(a)
    bx, by = diff(b)

    dx = point(ax, bx)
    dy = point(ay, by)

    div = det(dx, dy)

    if div == 0:
        raise Exception("No intersection")

    d = point(det(a.a, a.b), det(b.a, b.b))
    x = det(d, dx) / div
    y = det(d, dy) / div

    return point(x, y)


if __name__ == '__main__':
    # Setup
    A = Line(point(1, 2), point(2, 1))
    B = Line(point(2, 2), point(1, 1))
    # Target
    T = np.array([1.5, 1.5], dtype=np.float32)
    # Value
    V = intersect(A, B)
    # Test
    assert np.all(V == T), "Correct Intersection not found!"
