import source.utils.types as t
from .material import Material
import numpy as np

class Voxels:

    def __init__(self, shape: t.int3):
        self.shape = shape
        self.grid = np.zeros(shape, np.uint32)
        self.strength = np.zeros(shape, np.float64)
        self.forces = dict[Material, t.float3]()
        self.statics = dict[Material, t.bool3]()
        
    def get_material(self, material: Material):
        return self.grid == material.id

    def set_static(self, material: Material, locks: t.bool3):
        self.statics[material] = locks

    def set_force(self, material: Material, force: t.float3):
        self.forces[material] = force

    def static_map(self):
        L = np.max(self.grid) + 1
        static = np.zeros((L, 3), np.bool_)
        for material, locks in self.statics.items():
            static[material.id, :] = locks
        return static

    def force_map(self):
        L = np.max(self.grid) + 1
        static = np.zeros((L, 3), np.float64)
        for material, force in self.forces.items():
            static[material.id, :] = force
            # Number of voxels
            # count = np.count_nonzero(self.grid == material.id) # type: ignore
            # Inverse proportional force
            # static[material.id, :] = np.divide(force, count)
        return static
