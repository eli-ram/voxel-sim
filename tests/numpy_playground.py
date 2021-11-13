import __init__
from inspect import getmembers, isfunction
from typing import Any
import numpy as np
import sys

from source.math.vox2mesh18 import vox2mesh18

rng = np.random.default_rng()


def random_grid(size: int) -> 'np.ndarray[np.uint8]':
    shape = (size, size, size)
    return rng.choice([0, 1], size=shape)  # type: ignore


def grid_coords(grid: 'np.ndarray[Any]'):
    voxels = np.nonzero(grid)  # type: ignore
    coords = np.vstack(voxels).T
    return coords, voxels


def test_1():
    grid = random_grid(3)
    _, v = grid_coords(grid)
    test = np.zeros(grid.shape)
    test[v] = 1
    assert np.array_equal(grid, test), " Grid & Test-Grid differ"

def test_2():
    grid = random_grid(4)
    v, e, l = vox2mesh18(grid)
    assert all(q is not None for q in (v, e, l))

def test_3():
    a = np.zeros(10)
    b = np.zeros(10)
    a[2:5] = 1.0
    b[3:8] = 0.2
    m = a & b
    print(m)


# Run all Test functions
if __name__ == '__main__':
    for name, func in getmembers(sys.modules[__name__], isfunction):
        if name.startswith('test'):
            func()
