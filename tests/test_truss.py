from typing import Any
import __init__
import numpy as np
from source.math.truss2stress import fem_simulate, stress_matrix
from source.data.truss import Truss

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
    forces=np.array([  # type: ignore
        [0, 0],
        [0, 1],
        [0, 0],
        [0, 0],
        [0, 0],
        [0, 0],
    ], np.float32),
    static=np.array([  # type: ignore
        [1, 1],
        [0, 0],
        [1, 1],
        [1, 1],
        [0, 0],
        [1, 1],
    ], np.bool_),
    # Edge attrs
    edges=np.array([  # type: ignore
        [0, 1],
        [1, 2],
        [1, 4],
        [3, 4],
        [4, 5],
        [0, 4],
        [1, 5],
    ], np.uint32),
    areas=np.array([  # type: ignore
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
        1.0,
    ], np.float32),
)


M = stress_matrix(T, 1E1)  # type: ignore
D, E = fem_simulate(T, 1E1)


def preprocess(S: str):
    return [" ".join(line.split()) for line in str(S).split('\n') if line]


def check(value: Any, fasit: str, what: str):
    print(what + ':')
    print(value)
    A = preprocess(value)
    B = preprocess(fasit)
    assert A == B, \
        "Does not match fasit!"

# this is validated to be exactly equal matlab !


M_fasit = """
  (0, 0)        13.535534
  (0, 1)        3.5355337
  (0, 2)        -10.0
  (1, 0)        3.5355337
  (1, 1)        23.535534
  (2, 0)        -10.0
  (2, 2)        13.535534
  (2, 3)        3.5355337
  (3, 2)        3.5355337
  (3, 3)        23.535534
"""
check(M, M_fasit, "Stress Matrix")

D_fasit = """
[[ 0.      0.    ]
 [-0.0283  0.0467]
 [ 0.      0.    ]
 [ 0.      0.    ]
 [-0.0217  0.0033]
 [ 0.      0.    ]]
"""

check(D.round(4), D_fasit, "Node Displacement")


E_fasit = """
[ 0.4673 -0.4673  0.0653  0.0327 -0.0327 -0.0923 -0.0923]
"""

if E is not None:
    check(E.round(4), E_fasit, "Edge Stress")
