from __future__ import annotations
from typing import Any
import numpy as np

__all__ = ['Color', 'Colors']

def _attr(channel: int) -> float:
    def get(self: Any) -> float:
        return self.value[channel]
    def set(self: Any, value: float):
        self.value[channel] = value
    return property(get, set) # type: ignore

class Color:
    value: 'np.ndarray[np.float32]'

    def __init__(self, r: float, g: float, b: float, a: float = 1.0):
        self.value = np.array([r, g, b, a], dtype=np.float32) # type: ignore

    r = _attr(0)
    g = _attr(1)
    b = _attr(2)
    a = _attr(3)

    @staticmethod
    def stack(colors: list[Color]):
        return np.vstack([c.value for c in colors])

class Colors:
    WHITE = Color(1.0, 1.0, 1.0)
    GRAY = Color(0.5, 0.5, 0.5)
    BLACK = Color(0.0, 0.0, 0.0)
    RED = Color(1.0, 0.0, 0.0)
    GREEN = Color(0.0, 1.0, 0.0)
    BLUE = Color(0.0, 0.0, 1.0)
