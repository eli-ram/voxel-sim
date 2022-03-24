from typing import Callable
from source.math.truss2stress import fem_simulate

from source.math.voxels2truss import voxels2truss

from ..utils.wireframe.deformation import DeformationWireframe
from ..utils.mesh.simplemesh import Geometry, SimpleMesh
from ..interactive.tasks import Task
from ..math.mesh2voxels import mesh_to_voxels
from ..utils.matrices import Hierarchy
from ..data.colors import Color
from ..data.voxels import Voxels
from ..data.material import MaterialStore
from ..utils.types import Array, F, int3, bool3, float3
from .render import VoxelRenderer
import numpy as np
import glm

class VoxelProxy:
    tag: str = 'main-voxels'
    data: Voxels
    graphics: VoxelRenderer
    materials: MaterialStore

    def __init__(self, shape: int3, res: int):
        self.data = Voxels(shape)
        self.shape = shape
        self.graphics = VoxelRenderer(shape, res)
        self.materials = MaterialStore()

    def createMaterials(self, map: dict[str, Color]):
        for k, v in map.items():
            self.materials.create(k, v)
        self.update_colors()        

    def update_colors(self):
        self.graphics.colors.setData(self.materials.colors())

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
        task = AddMeshTask(self)
        task.setMaterial(material)
        task.setMesh(mesh, transform, strength)
        return task

    def add_box(self, offset: int3, strength: 'Array[F]', material: str):
        task = AddBoxTask(self)
        task.setMaterial(material)
        task.setBox(offset, strength)
        return task

    def fem_simulate(self, callback: Callable[[DeformationWireframe], None]):
        task = FemSimulateTask(self)
        task.setCallback(callback)
        return task

class ProxyTask(Task):

    def __init__(self, proxy: VoxelProxy):
        self.tag = proxy.tag
        self.P = proxy

class AddBoxTask(ProxyTask):

    def setMaterial(self, material: str):
        self.material = self.P.materials[material]

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



class FemSimulateTask(ProxyTask):

    def setCallback(self, callback: Callable[[DeformationWireframe], None]):
        self.callback = callback

    def compute(self):
        print("Building Truss")
        truss = voxels2truss(self.P.data)
        print("Simulating Truss")
        D, _ = fem_simulate(truss, 1E3)
        print("Creating Mesh")
        # Render mesh even if simulation failed
        if np.isnan(D).any():
            print("Fem simulation failed & produced nan")
            np.nan_to_num(D, copy=False)

        self.M = SimpleMesh(truss.nodes, truss.edges, Geometry.Lines)
        self.D = D

    def complete(self):
        print("Creating Deformation")
        self.callback(DeformationWireframe(self.M, self.D))
        print("Truss deformation created")
