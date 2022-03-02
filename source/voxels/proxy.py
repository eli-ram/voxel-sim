from ..utils.mesh.simplemesh import SimpleMesh
from ..interactive.tasks import Task
from ..math.mesh2voxels import mesh_to_voxels
from ..utils.matrices import Hierarchy
from ..data.colors import Color
from ..data.voxels import Voxels, MaterialStore
from ..utils.types import Array, F, int3, bool3, float3
from .render import VoxelRenderer
import numpy as np
import glm

class VoxelProxy:
    tag: str = 'main-voxels'
    data: Voxels
    graphics: VoxelRenderer
    materials: MaterialStore

    def __init__(self, shape: int3, res: int, materials: dict[str, Color]):
        self.data = Voxels(shape)
        self.shape = shape
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

    def add_mesh(self, mesh: SimpleMesh, transform: glm.mat4, strength: float, material: str):
        task = AddMeshTask(self, material)
        task.setMesh(mesh, transform, strength)
        return task

    def add_box(self, offset: int3, strength: 'Array[F]', material: str):
        task = AddBoxTask(self, material)
        task.setBox(offset, strength)
        return task
        # Get material
        M = self.materials[material]

        def build():
            # Get Material indices
            I = np.where(strength > 0.0)  # type: ignore
            # Get with offset
            O = tuple(i + o for i, o in zip(I, offset))
            # Set Material
            self.data.grid[O] = M.id
            # Set Strengths
            self.data.strength[O] = strength[I]
            # Get Box slices
            R = tuple(slice(o, o + s) for o, s in zip(offset, strength.shape))
            return self.data.grid[R].astype(np.float32)

    def update_colors(self):
        self.graphics.colors.setData(self.materials.colors())


class AddBoxTask(Task):

    def __init__(self, proxy: VoxelProxy, material: str):
        self.tag = proxy.tag
        self.P = proxy
        self.material = proxy.materials[material]

    def setBox(self, offset: int3, values: 'Array[F]'):
        self.offset = offset
        self.values = values
        self.S = tuple(slice(o,o+l) for o, l in zip(offset, values.shape))

    def compute(self):
        B = self.values > 0.0
        D = self.P.data
        D.grid[self.S][B] = self.material.id
        D.strength[self.S][B] = self.values[B]

    def complete(self):
        colors = self.P.data.grid[self.S].astype(np.float32)
        self.P.graphics.setBox(self.offset, colors)

class AddMeshTask(AddBoxTask):

    def setMesh(self, mesh: SimpleMesh, transform: glm.mat4, strength: float):
        self.mesh = mesh
        self.transform = Hierarchy.copy(transform)[:3, :]
        self.strength = strength

    def compute(self):
        offset, grid = mesh_to_voxels(self.mesh, self.transform, self.P.shape)
        values = grid * self.strength
        self.setBox(offset, values)
        AddBoxTask.compute(self)
