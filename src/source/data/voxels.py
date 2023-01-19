from ..utils.types import int3, bool3, float3
from .material import Material
import numpy as np

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
