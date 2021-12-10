import __init__
from inspect import getmembers, isfunction
import sys

import numpy as np
from source.math.truss2stress import fem_simulate, stress_matrix
from source.data.truss import Truss


def test_sparse():
    T = Truss(
        # Node attrs
        nodes=np.array([  # type: ignore
            [0, 0],
            [0, 1],
            [0, 2],
            [1, 0],
            [1, 1],
            [1, 2],
        ], np.float32),
        forces=np.array([ # type: ignore
            [0, 0],
            [0, 1],
            [0, 0],
            [0, 0],
            [0, 0],
            [0, 0],
        ], np.float32),
        static=np.array([ # type: ignore
            [1, 1],
            [0, 0],
            [1, 1],
            [1, 1],
            [0, 0],
            [1, 1],
        ], np.bool_),
        # Edge attrs
        edges=np.array([ # type: ignore
            [0, 1],
            [1, 2],
            [1, 4],
            [3, 4],
            [4, 5],
            [0, 4],
            [1, 5],
        ], np.uint32),
        areas=np.array([ # type: ignore
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
        ], np.float32),
    )

    # this is validated to be exactly equal matlab !

    M = stress_matrix(T, 1E1) # type: ignore
    print(M)

    D, E = fem_simulate(T, 1E1)
    print(D.round(4))
    print(E.round(4))


# Run all Test functions
if __name__ == '__main__':
    for name, func in getmembers(sys.modules[__name__], isfunction):
        if name.startswith('test'):
            print(f"Running: {name}")
            func()
