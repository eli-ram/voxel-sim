from ..utils.types import Array, B, T, int3
import numpy as np

def _slice(grid: 'Array[B]'):
    def span(a: int, b: int):
        B = np.any(grid, axis=(a, b)) # type: ignore
        l = np.argmax(B[::+1])  # type: ignore
        h = np.argmax(B[::-1])  # type: ignore
        return slice(l, -h)
    
    slices = (span(1, 2), span(0, 2), span(0, 1))
    offset: int3 = tuple(s.start for s in slices)
    return slices, offset

def remove_padding_strength(strength: 'Array[T]'):
    slices, offset = _slice(strength > 0.0)
    return offset, strength[slices]

def remove_padding_grid(grid: 'Array[B]'):
    slices, offset = _slice(grid)
    return offset, grid[slices]
