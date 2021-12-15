from dataclasses import dataclass
from ..utils.types import int3, bool3, float3
from .colors import Color
import numpy as np


@dataclass
class Material:
    id: int
    name: str
    color: Color

    def __post_init__(self):
        assert self.id > 0, \
            "Materials should never reference Voxel-VOID (0)"

    def __hash__(self):
        return self.id


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


class Voxels:

    def __init__(self, shape: int3):
        self.shape = shape
        self.grid = np.zeros(shape, np.uint32)
        self.strength = np.zeros(shape, np.float32)
        self.forces: dict[Material, float3] = dict()
        self.statics: dict[Material, bool3] = dict()

    def get_material(self, material: Material):
        return self.grid == material.id

    def set_static(self, material: Material, locks: bool3):
        self.statics[material] = locks

    def set_force(self, material: Material, force: float3):
        self.forces[material] = force

    def static_map(self):
        L = np.max(self.grid) + 1
        static = np.zeros((L, 3), np.bool_)
        for material, locks in self.statics.items():
            static[material.id, :] = locks
        return static

    def force_map(self):
        L = np.max(self.grid) + 1
        static = np.zeros((L, 3), np.float32)
        for material, force in self.forces.items():
            static[material.id, :] = force
        return static