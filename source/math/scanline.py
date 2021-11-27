import numpy as np
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, cast

from ..utils.types import int2


Point = TypeVar('Point')
Slope = TypeVar('Slope')


class Rasterizer(Generic[Point, Slope], ABC):

    @abstractmethod
    def xy(self, p: Point) -> int2:
        raise NotImplementedError()

    @abstractmethod
    def slope(self, p0: Point, p1: Point, steps: int) -> Slope:
        raise NotImplementedError()

    @abstractmethod
    def scanline(self, s0: Slope, s1: Slope, y: int) -> None:
        raise NotImplementedError()

    def y_range(self, y0: int, y1: int):
        return range(y0, y1)

    def x_range(self, x0: int, x1: int):
        return range(x0, x1)

    def rasterize(self, p0: Point, p1: Point, p2: Point):
        # Unpack values
        x0, y0 = self.xy(p0)
        x1, y1 = self.xy(p1)
        x2, y2 = self.xy(p2)

        # Order Points based on [Y, X]
        if (y1, x1) < (y0, x0):
            x0, x1 = x1, x0
            y0, y1 = y1, y0
            p0, p1 = p1, p0

        if (y2, x2) < (y0, x0):
            x0, x2 = x2, x0
            y0, y2 = y2, y0
            p0, p2 = p2, p0

        if (y2, x2) < (y1, x1):
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            p1, p2 = p2, p1

        # Return if area is zero
        if (y0 == y2):
            return

        # Determine the short side
        short = (y1 - y0) * (x2 - x0) < (x1 - x0) * (y2 - y0)

        # Slope storage
        slopes = cast(list[Slope], [None, None])

        # Set the long side
        slopes[not short] = self.slope(p0, p2, y2 - y0)

        # Draw top Triangle
        if (y0 < y1):
            slopes[short] = self.slope(p0, p1, y1 - y0)
            s1, s2 = slopes
            for y in self.y_range(y0, y1):
                self.scanline(s1, s2, y)

        # Draw bottom Triangle
        if (y1 < y2):
            slopes[short] = self.slope(p1, p2, y2 - y1)
            s1, s2 = slopes
            for y in self.y_range(y1, y2):
                self.scanline(s1, s2, y)


class IntRasterizer(Rasterizer[int2, list[float]]):

    def __init__(self, size: int2):
        sx, sy = size
        self.sx = sx
        self.sy = sy
        self.raster = np.zeros(size, np.uint8)

    def text(self) -> str:
        setup = np.array(['.', *map(str, range(9)), 'x']) # type: ignore
        self.raster[self.raster > 10] = 10
        chars = setup[self.raster]
        lines = (" ".join(line) for line in chars)
        return "\n".join(lines)

    def plot(self, x: int, y: int):
        self.raster[x, y] += 1

    def y_range(self, y0: int, y1: int):
        return range(max(y0, 0), min(y1, self.sy))

    def x_range(self, x0: int, x1: int):
        return range(max(x0, 0), min(x1, self.sx))

    def xy(self, p: int2) -> int2:
        return p

    def slope(self, p0: int2, p1: int2, steps: int) -> list[float]:
        begin, end = p0[0], p1[0]
        return [begin, (end - begin) / steps]

    def scanline(self, s0: list[float], s1: list[float], y: int) -> None:
        for x in self.x_range(int(s0[0]), int(s1[0])):
            self.plot(x, y)
        s0[0] += s0[1]
        s1[0] += s1[1]
