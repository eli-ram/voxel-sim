from typing import Callable, Union
import numpy as np
from ..utils.types import Array, F, I, U

N = Union[F, I, U]


grid: 'Callable[..., tuple[Array[N], ...]]' = \
    np.meshgrid # type: ignore


def coordinates(lx: int, hx: int, ly: int, hy: int):
    xs = np.arange(lx, hx)
    ys = np.arange(ly, hy)
    xs, ys = grid(xs, ys)
    return np.vstack((xs.ravel(), ys.ravel())).transpose()


def unpack(M: 'Array[N]') -> tuple['Array[N]', ...]:
    return M  # type: ignore


def lexsort(*arrays: 'Array[N]') -> slice:
    return np.lexsort(arrays)  # type: ignore
