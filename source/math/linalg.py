from typing import TypeVar
import numpy as np

N = TypeVar('N', np.float32, np.float64)


def normalize(V: 'np.ndarray[N]') -> 'np.ndarray[N]':
    return V / np.linalg.norm(V)  # type: ignore


def normal(A: 'np.ndarray[N]', B: 'np.ndarray[N]', C: 'np.ndarray[N]') -> 'np.ndarray[N]':
    AB = B - A
    AC = C - A
    N = np.cross(AB, AC)  # type: ignore
    return normalize(N)  # type: ignore


def grid(*R: 'np.ndarray[N]') -> tuple['np.ndarray[N]', ...]:
    return np.meshgrid(*R)  # type: ignore


def coords(lx: int, hx: int, ly: int, hy: int):
    xs = np.arange(lx, hx)
    ys = np.arange(ly, hy)
    xs, ys = grid(xs, ys)
    return np.vstack((xs.ravel(), ys.ravel()))


def unpack(M: 'np.ndarray[N]') -> tuple['np.ndarray[N]', ...]:
    return M  # type: ignore
