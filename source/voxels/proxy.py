from ..data.colors import Color
from ..data.voxels import Voxels, MaterialStore, int3, bool3
from ..math.voxels2truss import voxels2truss
from ..utils.matrices import Hierarchy
from ..utils.wireframe import Geometry, SimpleMesh, Wireframe
from .render import VoxelRenderer
import numpy as np
import glm


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

    def add_box(self, offset: int3, strength: 'np.ndarray[np.float32]', material: str):
        M = self.materials[material]
        G = np.where(strength > 0.0, M.id, 0).astype(np.uint32)
        I = np.nonzero(G)  # type: ignore
        O = tuple(i + o for i, o in zip(I, offset))
        self.data.grid[O] = G[I]
        self.data.strength[O] = strength[I]
        S = strength.shape
        R = tuple(slice(o, o + s) for o, s in zip(offset, S))
        B = self.data.grid[R]
        self.graphics.setBox(offset, B.astype(np.float32))

    def update_colors(self):
        self.graphics.colors.setData(self.materials.colors())

    def render(self, h: Hierarchy):
        self.graphics.render(h)

    def get_mesh(self, color: glm.vec4):
        T = voxels2truss(self.data, exclude=['edges'])
        M = SimpleMesh(T.nodes, T.edges, Geometry.Lines)
        test(M.indices)
        W = Wireframe(M, color, 1.0)
        return W


def test(v: 'np.ndarray[np.uint32]'):
    A = np.vstack([v, v[:, ::-1]])
    _, C = np.unique(A, axis=0, return_counts=True)
    assert np.max(C) == 1
