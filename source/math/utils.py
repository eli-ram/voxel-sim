from itertools import combinations
from typing import Tuple
import numpy as np

def crop(data: 'np.ndarray[np.bool_]'):
    """ Get the offset for the minimal slice of the data """
    def span(axis: Tuple[int, ...]):
        B = data.any(axis)
        L = int(B[::+1].argmax())
        H = int(B[::-1].argmax())
        return L, -H

    N = data.ndim - 1
    axes = combinations(range(N, -1, -1), N)
    spans = [span(a) for a in axes]
    offset = tuple(l for l, _ in spans)
    slices = tuple(slice(l, h) for l, h in spans)

    return offset, slices
    
def remove_padding_strength(strength: np.ndarray[np.float32]):
    offset, slices = crop(strength > 0.0)
    return offset, strength[slices]

def remove_padding_grid(grid: np.ndarray[np.bool_]):
    offset, slices = crop(grid)
    return offset, grid[slices]
