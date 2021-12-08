import __init__
from inspect import getmembers, isfunction
import sys

import numpy as np
from source.math.truss2stress import Solver, stress_matrix
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

    M = stress_matrix(T)

    R = np.round(M.todense(), 2)

    print(R)

    S = Solver(T)

    print(S.U)


# Run all Test functions
if __name__ == '__main__':
    for name, func in getmembers(sys.modules[__name__], isfunction):
        if name.startswith('test'):
            print(f"Running: {name}")
            func()
