import numpy as np
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, cast

from ..utils.types import int2, float3


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


class IntSlope:

    def __init__(self, l: float, h: float, steps: int):
        self.value = l
        self.slope = (h - l) / steps

    def floor(self):
        return int(self.value)

    def step(self):
        self.value += self.slope

class IntRasterizer(Rasterizer[float3, list[IntSlope]]):

    def __init__(self, size: int2):
        sx, sy = size
        self.sx = sx
        self.sy = sy
        self.raster = np.zeros(size, np.float32)

    def text(self) -> str:
        setup = np.array(['.', *map(str, range(9)), 'x']) # type: ignore
        out = self.raster
        out[out < 0] = 0.0
        out = out * (10 / out.max())
        chars = setup[out.astype(np.uint8)]
        lines = (" ".join(line) for line in chars)
        return "\n".join(lines)

    def plot(self, x: int, y: int, z: float):
        if (self.raster[x, y] < z):
            self.raster[x, y] = z

    def y_range(self, y0: int, y1: int):
        return range(max(y0, 0), min(y1, self.sy))

    def x_range(self, x0: int, x1: int):
        return range(max(x0, 0), min(x1, self.sx))

    def xy(self, p: float3) -> int2:
        x, y, _ = p
        return int(x), int(y)

    def slope(self, p0: float3, p1: float3, steps: int) -> list[IntSlope]:
        x0, _, z0 = p0 
        x1, _, z1 = p1 
        return [
            IntSlope(x0, x1, steps),
            IntSlope(z0, z1, steps),
        ]

    def scanline(self, s0: list[IntSlope], s1: list[IntSlope], y: int) -> None:
        x0, z0 = s0
        x1, z1 = s1
        lx, hx = x0.floor(), x1.floor()
        z = IntSlope(z0.value, z1.value, hx - lx)
        for x in self.x_range(x0.floor(), x1.floor()):
            self.plot(x, y, z.value)
            z.step()
        for s in s0 + s1:
            s.step()