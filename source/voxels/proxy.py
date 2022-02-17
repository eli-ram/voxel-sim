from ..data.colors import Color
from ..data.voxels import Voxels, MaterialStore
from ..utils.types import Array, F, T, I, int3, bool3, float3
from ..debug.time import time
from .render import VoxelRenderer
import numpy as np


class VoxelProxy:
    data: Voxels
    graphics: VoxelRenderer
    materials: MaterialStore

    def __init__(self, shape: int3, res: int, materials: dict[str, Color]):
        self.data = Voxels(shape)
        self.graphics = VoxelRenderer(shape, res)
        self.materials = MaterialStore()
        for k, v in materials.items():
            self.materials.create(k, v)
        self.update_colors()

    def material_list(self) -> list[str]:
        return list(self.materials)

    def set_alpha(self, v: float):
        self.graphics.alpha = v

    def toggle_outline(self):
        self.graphics.outline = not self.graphics.outline

    def set_static(self, material: str, locks: bool3):
        M = self.materials[material]
        self.data.set_static(M, locks)

    def set_force(self, material: str, force: float3):
        M = self.materials[material]
        self.data.set_force(M, force)

    @time("add-box")
    def add_box(self, offset: int3, strength: 'Array[F]', material: str):
        # Get material
        M = self.materials[material]
        # Get Material indices
        I = np.where(strength > 0.0)  # type: ignore
        # Get with offset
        O = tuple(i + o for i, o in zip(I, offset))
        # Set Material
        self.data.grid[O] = M.id
        # Set Strengths
        self.data.strength[O] = strength[I]
        # Get Box slices
        S = strength.shape
        R = tuple(slice(o, o + s) for o, s in zip(offset, S))
        B = self.data.grid[R].astype(np.float32)
        # Update live preview
        self.graphics.setBox(offset, B)

    def update_colors(self):
        self.graphics.colors.setData(self.materials.colors())


def _span(V: 'Array[I]'):
    return slice(V.min(), V.max() + 1)


def remove_padding_strength(strength: 'Array[T]'):
    X, Y, Z = np.where(strength > 0.0)  # type: ignore
    x = _span(X)
    y = _span(Y)
    z = _span(Z)

    strength = strength[x, y, z]
    offset = (x.start, y.start, z.start)

    return offset, strength


def remove_padding_grid(grid: 'Array[np.bool_]'):
    def span(a: int, b: int):
        B = np.any(grid, axis=(a, b)) # type: ignore
        l = np.argmax(B[::+1])  # type: ignore
        h = np.argmax(B[::-1])  # type: ignore
        return slice(l, -h)

    x = span(1, 2)
    y = span(0, 2)
    z = span(0, 1)

    grid = grid[x, y, z]
    offset = (x.start, y.start, z.start)

    return offset, grid
