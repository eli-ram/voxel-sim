# pyright: reportConstantRedefinition=false
from typing import Union, Any
from ..utils.types import Array, F, I
from ..data.truss import Truss
from scipy.sparse import (
    csr_matrix as sparse,
    csc_matrix as vector,
    linalg,
)
import numpy as np


def sh(V: 'Array[Any]', name: str = ""):
    print(name, V.shape)


def solve(M: sparse, F: vector) -> vector:
    # Solve: Ax = b
    return linalg.spsolve(M, F)  # type: ignore


def outer_rows(V: 'Array[F]') -> 'Array[F]':
    return np.einsum('ij,ik->ijk', V, V)  # type: ignore


def inverse_length_rows(D: 'Array[F]') -> 'Array[F]':
    l = np.linalg.norm(D, axis=1)  # type: ignore
    return np.reciprocal(l, out=l)  # type: ignore


def inplace_multiply(out: 'Array[F]', value: 'Union[float, Array[F]]'):
    np.multiply(out, value, out=out)  # type: ignore


def inplace_accumulate(out: 'Array[F]', I: 'Array[I]', values: 'Array[F]'):
    # Doesn't work for 2D arrays...
    np.add.at(out, I, values)  # type: ignore


def inplace_negate(out: 'Array[F]'):
    np.negative(out, out=out)  # type: ignore


def accumulate_rows(C: 'Array[F]', E0: 'Array[I]', E1: 'Array[I]', Q: 'Array[F]'):
    # Native iteration per node
    # Garbage memory garbler
    # par-for <per-node>
    for i in range(C.shape[0]):
        I = (E0 == i) | (E1 == i)
        np.sum(Q[I, :], axis=0, out=C[i, :])  # type: ignore


def accumulate_columns(C: 'Array[F]', E0: 'Array[I]', E1: 'Array[I]', Q: 'Array[F]'):
    # Fewer native iterations
    # Lower memory overhead
    # par-for <per-column>
    for col in range(C.shape[1]):
        inplace_accumulate(C[:, col], E0, Q[:, col])
        inplace_accumulate(C[:, col], E1, Q[:, col])


def flat_join(*arrays: 'Array[F]') -> 'Array[F]':
    return np.concatenate([a.flatten() for a in arrays])


def stress_matrix(truss: Truss, elasticity: float = 2E9):
    # Upack needed parts of truss
    S = truss.static
    A = truss.areas[:, None]
    N = truss.nodes
    E = truss.edges

    # Node Count * Degree of freedom
    L, DOF = N.shape
    N_DOF = L * DOF

    # Edge from <-> to
    E0 = E[:, 0]
    E1 = E[:, 1]

    # edge vectors
    D = N[E0, :] - N[E1, :]

    # inverse edge lengths
    L = inverse_length_rows(D)[:, None]

    # cosinus thetas for force distribution
    inplace_multiply(D, L)

    # Row wise outer product
    # to obtain stress kernels
    Q = outer_rows(D).reshape(D.shape[0], -1)
    inplace_multiply(Q, L * A * elasticity)

    # Accumulate node stress kernels
    C = np.zeros((N.shape[0], Q.shape[1]), np.float32)
    # Choose <one> measure !
    # accumulate_rows(C, E0, E1, Q)
    accumulate_columns(C, E0, E1, Q)

    # negate edge kernels
    inplace_negate(Q)

    # Genereate Diagonal Indices
    ID = np.empty(N.shape, dtype=np.int32)

    # Register Static Axes
    ID[S] = -1

    # Matrix size loss
    L_DOF = N_DOF - np.sum(S)

    # Index recalculation
    # obs, this may be slow ?
    ID[~S] = range(L_DOF)

    # Values
    V = flat_join(C, Q, Q)

    # Column indices
    CI: 'Array[F]' = np.tile(ID, DOF)  # type: ignore
    I = flat_join(CI, CI[E0, :], CI[E1, :])

    # Row indices per half-edge
    CJ: 'Array[F]' = np.repeat(ID, DOF, axis=1)  # type: ignore
    J = flat_join(CJ, CJ[E1, :], CJ[E0, :])

    # Destroy Statically Locked Node Axes
    KEEP = (J != -1) & (I != -1)
    V = V[KEEP]
    I = I[KEEP]
    J = J[KEEP]

    # Build sparse matrix
    M = sparse((V, (I, J)), shape=(L_DOF, L_DOF))

    return M


def force_vector(truss: Truss):
    F = truss.forces
    S = truss.static
    # Remove force on static
    return vector(F[~S, None])


class Solver:

    def __init__(self, truss: Truss):
        M = stress_matrix(truss)
        F = force_vector(truss)
        self.U = solve(M, F)

    def displacement(self):
        pass

    def compression(self):
        pass
