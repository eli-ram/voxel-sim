from typing import TypeVar
import numpy as np

N = TypeVar('N', np.float32, np.float64)


def normalize(V: 'np.ndarray[N]') -> 'np.ndarray[N]':
    return V / np.linalg.norm(V)  # type: ignore


def grid(*R: 'np.ndarray[N]') -> tuple['np.ndarray[N]', ...]:
    return np.meshgrid(*R)  # type: ignore


def coordinates(lx: int, hx: int, ly: int, hy: int):
    xs = np.arange(lx, hx)
    ys = np.arange(ly, hy)
    xs, ys = grid(xs, ys)
    return np.vstack((xs.ravel(), ys.ravel())).transpose()


def unpack(M: 'np.ndarray[N]') -> tuple['np.ndarray[N]', ...]:
    return M  # type: ignore

