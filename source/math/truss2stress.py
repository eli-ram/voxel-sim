# pyright: reportConstantRedefinition=false
from typing import Union
from ..utils.types import Array, F, I
from ..data.truss import Truss
import numpy as np

"""
    Q = np.outer(C, C).reshape(len(E), -1)

    I = np.arange(len(N))
    S_N_0 = I[:, np.newaxis] == E[np.newaxis, :, 0]
    S_N_1 = I[:, np.newaxis] == E[np.newaxis, :, 1]
    S_N_I = node stiffness indices = S_N_0 | S_N_1
    S_N = node stiffness = np.sum(Q, where=S_N_I)
"""


def outer_rows(V: 'Array[F]') -> 'Array[F]':
    return np.einsum('ij,ik->ijk', V, V)  # type: ignore


def inverse_length_rows(D: 'Array[F]') -> 'Array[F]':
    l = np.linalg.norm(D, axis=0)  # type: ignore
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
        np.sum(Q[I, :], axis=0, out=C[i, :]) # type: ignore


def accumulate_columns(C: 'Array[F]', E0: 'Array[I]', E1: 'Array[I]', Q: 'Array[F]'):
    # Fewer native iterations
    # Lower memory overhead
    # par-for <per-column>
    for col in range(C.shape[1]):
        inplace_accumulate(C[:, col], E0, Q[:, col])
        inplace_accumulate(C[:, col], E1, Q[:, col])


def stress_matrix(truss: Truss, elasticity: float = 1E-5):
    E = truss.edges
    N = truss.nodes
    A = truss.areas

    # Edge from <-> to
    E0 = E[:, 0]
    E1 = E[:, 1]

    # edge vectors
    D = N[E0, :] - N[E1, :]

    # inverse edge lengths
    L = inverse_length_rows(D)

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

    # Todo node-kernel-indices
    # Todo edge-kernel-indices
    # Todo concat indices
    # Todo concat kernels
    # Todo sparse matrix


    # Remove grounded nodes
    """
	log("Removing rows & columns with locked bounds\n");
    # locked indices
	c = find(extC==0);
    # destroy columns
	KK(c,:)=[];
    # destroy rows
	KK(:,c)=[];
    # destroy forces
	extF(c,:)=[]; % forces on grounded nodes has no effect!
    """

    # Solve
    # U = KK \ extF
    # => KK @ U = extF ?
    # U = s.spsolve(KK, extF)