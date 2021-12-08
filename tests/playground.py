from typing import Any
import __init__
from inspect import getmembers, isfunction
import sys


def test_sparse():
    import numpy as np
    from scipy import sparse as s

    V = np.ones(16)
    X = np.arange(16) % 4
    Y = np.arange(16) // 4

    X[4:8] = 0
    Y[4:8] = 0

    print(V)
    print(X)
    print(Y)

    S = s.coo_matrix((V, (X, Y)), shape=(4,4))

    # print(S)

    M: Any = S.todense() # type: ignore

    print(M)

# Run all Test functions
if __name__ == '__main__':
    for name, func in getmembers(sys.modules[__name__], isfunction):
        if name.startswith('test'):
            print(f"Running: {name}")
            func()
