import __init__
from inspect import getmembers, isfunction
from typing import Any
import numpy as np
import sys
from source.data.voxels import Voxels

from source.math.voxels2truss import voxels2truss

rng = np.random.default_rng()


def random_voxels(size: int):
    shape = (size, size, size)
    voxels = Voxels(shape)
    voxels.grid = rng.choice([0, 1], size=shape)  # type: ignore
    voxels.strength = voxels.grid * 0.03
    return voxels


def grid_coords(grid: 'np.ndarray[Any]'):
    voxels = np.nonzero(grid)  # type: ignore
    coords = np.vstack(voxels).T
    return coords, voxels


def test_1():
    grid = random_voxels(3)
    _, v = grid_coords(grid.grid)
    test = np.zeros(grid.shape)
    test[v] = grid.grid[v]
    assert np.array_equal(grid.grid, test), " Grid & Test-Grid differ"

def test_2():
    grid = random_voxels(4)
    truss = voxels2truss(grid)
    print(f"{truss.nodes.shape=}")
    print(f"{truss.forces.shape=}")
    print(f"{truss.static.shape=}")
    print(f"{truss.edges.shape=}")
    print(f"{truss.areas.shape=}")

# Run all Test functions
if __name__ == '__main__':
    for name, func in getmembers(sys.modules[__name__], isfunction):
        if name.startswith('test'):
            print(f"Running: {name}")
            func()
