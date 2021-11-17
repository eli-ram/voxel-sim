from typing import Any, Tuple, Type, TypeVar
from .colors import Color, Colors
import numpy as np

Volume = Tuple[int, int, int]
Offset = Tuple[int, int, int]
Locks = Tuple[bool, bool, bool]

T = TypeVar('T')


def _zeros(shape, dtype: Type[T]) -> 'np.ndarray[T]':  # type: ignore
    return np.zeros(shape, dtype)  # type: ignore


class Material:
    id: int
    color: Color

    def __init__(self, id: int, color: Color):
        assert id > 0, "Materials should never reference VOID (0)"
        self.id = id
        self.color = color


class MaterialStore:
    NONE = Color(0, 0, 0, 0)
    STATIC = Material(1, Colors.BLUE)
    FORCE = Material(2, Colors.GREEN)

    def __init__(self):
        self.all: dict[int, Material] = dict()
        self.add(self.STATIC)
        self.add(self.FORCE)

    def add(self, material: Material):
        assert material.id not in self.all, " Material id is already occupied "
        self.all[material.id] = material

    def colors(self):
        all = [self.all[k] for k in self.all]
        count = max(all, key=lambda m: m.id)
        colors = _zeros((count, 4), np.float32)
        for m in all:
            colors[m.id, :] = m.color.value
        return colors


class VoxelForces:
    # TODO: this is a possible memory-optimization (!?)
    def __init__(self, offset: Offset, shape: Volume, material: Material):
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
        indices = np.nonzero(voxels.get_material(self.material)) # type: ignore
        forces = self.index(indices).flatten()
        indices = lut[indices].flatten()
        return indices, forces

class Voxels:

    def __init__(self, shape: Volume):
        self.shape = shape
        self.grid = _zeros(shape, np.uint32)
        self.strength = _zeros(shape, np.float32)
        self.forces = _zeros((*shape,3), np.float32)
        self.statics: dict[Material, Locks] = dict()

    def get_material(self, material: Material):
        return self.grid == material.id

    def set_static(self, material: Material, locks: Locks):
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
        delattr(self, '__buffer__')

class VoxelDataBuffer:
    # Voxel grid index buffer
    voxels: Tuple['np.ndarray[np.int64]',...]
    # Voxel vertices
    vertices: 'np.ndarray[np.float32]'
    # Voxel grid with vertex id's
    lut: 'np.ndarray[np.uint32]'

    def __init__(self, voxels: Voxels):
        self.voxels = np.nonzero(voxels.grid) # type: ignore
        self.vertices = np.vstack(self.voxels).astype(np.float32).transpose()
        self.lut = _zeros(voxels.shape, dtype=np.uint32)
        self.lut[self.voxels] = range(len(self.vertices))
