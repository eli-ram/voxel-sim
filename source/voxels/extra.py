from .render import VoxelRenderer
from typing import Any
import numpy as np


def space(size: int) -> 'np.ndarray[np.float32]':
    return np.linspace(-1.0, 1.0, num=size, dtype=np.float32)


def cut(v: Any, l: Any, h: Any):
    v = (v - l) * (h - l)
    L = 0.0 < v
    H = 1.0 > v
    return np.where(L & H, v, 0.0)

def vox_sphere(v: VoxelRenderer):
    X, Y, Z = [space(size)**2 for size in v.shape]
    N = np.newaxis
    field = X[:, N, N] + Y[N, :, N] + Z[N, N, :]
    sphere = np.sqrt(field)  # type: ignore
    data = cut(sphere, 0.0, 1.0).astype(np.float32)

    # Scale to match the color space
    data = data * v.color_count

    # Set data
    v.setBox((0, 0, 0), data) #np.round(data))

    # Make some square cutouts
    x, y, z = [a // 2 for a in v.shape]
    s = (x, y, z)
    l = [
        (x, 0, 0),
        (0, y, 0),
        (0, 0, z),
        (x, y, z),
    ]
    for p in l:
        v.clearBox(p, s)
