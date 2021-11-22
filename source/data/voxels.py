from dataclasses import dataclass
from typing import Any, Tuple, Type, TypeVar
from ..utils.types import int3, bool3
from .colors import Color
import numpy as np


T = TypeVar('T')


def _zeros(shape, dtype: Type[T]) -> 'np.ndarray[T]':  # type: ignore
    return np.zeros(shape, dtype)  # type: ignore


@dataclass
class Material:
    id: int
    name: str
    color: Color

    def __post_init__(self):
        assert self.id > 0, "Materials should never reference VOID (0)"


class MaterialStore:

    def __init__(self):
        self._lut: dict[str, Material] = {}
        self._all: list[Material] = []

    def create(self, name: str, color: Color):
        assert name not in self._lut, " Material name is already occupied "
        L = len(self._all)
        M = Material(L + 1, name, color)
        self._lut[name] = M
        self._all.append(M)
        return M

    def __getitem__(self, key: str):
        return self._lut[key]

    def __iter__(self):
        yield from self._lut

    def colors(self):
        return Color.stack([m.color for m in self._all])


class VoxelForces:
    # TODO: this is a possible memory-optimization (!?)
    def __init__(self, offset: int3, shape: int3, material: Material):
        # position in volume
        self.offset = offset
        # list-3D[(fx, fy, fz)]
        self.forces = _zeros((*shape, 3), np.float32)
        # material
        self.material = material

    def index(self, indices: Any) -> 'np.ndarray[np.float32]':
        indices = [I + O for I, O in zip(indices, self.offset)]
        return self.forces[indices, :]

    def pack(self, voxels: 'Voxels', lut: 'np.ndarray[np.uint32]'):
        M = voxels.get_material(self.material)
        indices = np.nonzero(M)  # type: ignore
        forces = self.index(indices).flatten()
        indices = lut[indices].flatten()
        return indices, forces


class Voxels:

    def __init__(self, shape: int3):
        self.shape = shape
        self.grid = _zeros(shape, np.uint32)
        self.strength = _zeros(shape, np.float32)
        self.forces = _zeros((*shape, 3), np.float32)
        self.statics: dict[Material, bool3] = dict()

    def get_material(self, material: Material):
        return self.grid == material.id

    def set_static(self, material: Material, locks: bool3):
        self.statics[material] = locks

    @property
    def vertices(self):
        return self.buffer.vertices

    @property
    def index_table(self):
        return self.buffer.lut

    @property
    def indices(self):
        return self.buffer.voxels

    def force_array(self):
        return self.forces[self.indices]

    def static_array(self):
        B = self.buffer
        static = _zeros((len(B.vertices), 3), np.bool_)
        for material, locks in self.statics.items():
            I = B.lut[self.get_material(material)]
            static[I] = locks
        return static

    @property
    def buffer(self) -> 'VoxelDataBuffer':
        if not hasattr(self, '__buffer__'):
            setattr(self, '__buffer__', VoxelDataBuffer(self))
        return getattr(self, '__buffer__')

    def invalidate(self):
        if hasattr(self, '__buffer__'):
            delattr(self, '__buffer__')


class VoxelDataBuffer:
    # Voxel grid index buffer
    voxels: Tuple['np.ndarray[np.int64]', ...]
    # Voxel vertices
    vertices: 'np.ndarray[np.float32]'
    # Voxel grid with vertex id's
    lut: 'np.ndarray[np.uint32]'

    def __init__(self, voxels: Voxels):
        self.voxels = np.nonzero(voxels.grid)  # type: ignore
        self.vertices = np.vstack(self.voxels).astype(np.float32).transpose()
        self.vertices += 0.5 # type: ignore
        self.lut = _zeros(voxels.shape, dtype=np.uint32)
        self.lut[self.voxels] = range(len(self.vertices))
