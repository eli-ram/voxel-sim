from functools import cache

import glm
import numpy as np

import source.data.mesh as m
import source.parser.all as p
import source.utils.types as t
import source.data.voxels as v
import source.data.colors as c
import source.interactive.scene as s
import source.data.voxel_tree.node as n
import source.math.voxels2truss as v2t
import source.math.truss2stress as fem

from source.utils.shapes import line_cube
from source.utils.wireframe.deformation import DeformationWireframe
from source.utils.wireframe.wireframe import Wireframe
from source.interactive.tasks import TaskQueue
from source.voxels.render import VoxelRenderer

from .parameters import Parameters
from .geometry import Geometry, GeometryCollection, Context
from .material import Color, MaterialStore
from .box import Box


@cache
def unit_box():
    return Wireframe(line_cube())


class Config(p.Struct):
    # Run simulation / ga
    run: p.Bool

    # Build Voxels
    build: p.Bool

    # Render Raw Geometry
    render: p.Bool

    # Voxel global alpha
    alpha: p.Float

    # Voxel outline
    outline: p.Bool

    # Constrain Voxel Region
    region: Box

    # Render Resolution per voxel
    resolution: p.Int

    # Background color
    background: Color

    def buildScene(self):
        """ Build the scene presented to the user """
        B = self.region.box

        # If no region, just present the geometry
        if B.is_empty:
            return s.Scene()

        # Build the region bounding box
        bbox = s.Transform((
            # translate to origin of the box
            glm.translate(glm.vec3(*B.start))
            # scale the box to match
            * glm.scale(glm.vec3(*B.shape))
        ), unit_box())

        # Build the scene matrix to center the bounding box
        matrix = (
            # Scale based on the longes side
            glm.scale(glm.vec3(1 / max(B.shape)))
            # Translate to center
            * glm.translate(-glm.vec3(*B.center))
        )

        # return the scene
        return s.Scene(matrix, [bbox])

    def buildContext(self):
        # Requested not to build
        if not self.build.require():
            return None
        # Get box
        B = self.region.box
        # Unable to build with no box
        if B.is_empty:
            return None
        # Create context
        return Context(B)


class VoxelCache:
    node: n.VoxelNode
    renderer: VoxelRenderer | None = None

    def getNode(self, G: Geometry, ctx: Context):
        # Get Geometry voxels
        N = G.buildVoxels(ctx)

        # Return Corrected voxels
        self.node = ctx.finalize(N)
        return self.node

    def getRenderer(self, shape: t.int3, count: int) -> VoxelRenderer:
        # Rebuild if changed
        if not (R := self.renderer) or R.shape != shape or R.count != count:
            self.renderer = VoxelRenderer(shape, count)

        # return cached
        return self.renderer

    def refNode(self):
        if hasattr(self, 'node'):
            return self.node


class Configuration(p.Struct):
    # General Settings
    config: Config

    # Defined Materials
    materials: MaterialStore

    # Application order of Geometry
    geometry: GeometryCollection

    # Machine Learning Parameters
    parameters: Parameters

    def postParse(self):
        store = self.materials.get()
        self.geometry.loadMaterial(store)
        self.parameters.loadMaterial(store)

    __cache = VoxelCache()

    def getVoxelRenderer(self, node: n.VoxelNode):
        # Get data
        D = node.data
        # Get config
        C = self.config
        # Instance voxel renderer
        V = self.__cache.getRenderer(
            D.material.shape,
            C.resolution.getOr(256),
        )
        # Set alpha
        V.alpha = C.alpha.getOr(0.9)
        # Set colors
        V.set_colors(self.materials.get().colors())
        # Set data
        V.fill(D.material.astype(np.float32))
        # Set outline
        V.outline = C.outline.getOr(True)
        # Make transformation
        T = glm.translate(glm.vec3(*D.box.start))
        # Return renderer
        return s.Transform(T, V)

    def buildVoxelsObject(self, node: n.VoxelNode):
        # Get
        D = node.data
        M = self.materials
        # Create
        V = v.Voxels(D.material.shape)
        # Set internals
        V.grid = D.material
        V.strength = D.strength
        V.forces = M.forces
        V.statics = M.statics
        # Return
        return V

    def background(self):
        return self.config.background.require()

    def scene(self, TQ: TaskQueue):
        return TQ.dispatch(self.config.buildScene)()

    def configure(self, TQ: TaskQueue, S: s.Scene):
        """ Process config (called from parser thread) """
        # Build the scene
        @TQ.dispatch
        def scene():
            # geometry
            S.add(self.geometry.buildRender())
            # params
            S.opt(self.parameters.render())

        # Compute voxels

        # Not configured for voxels
        CTX = self.config.buildContext()
        if CTX is None:
            print("Cannot build voxels")
            return

        # Build voxels
        N = self.__cache.getNode(self.geometry, CTX)

        # Build tmp
        ROD = CTX.finalize(self.parameters.sample(CTX))

        # JOIN
        N = n.VoxelNode.Parent(n.Operation.OVERWRITE, [N, ROD])
        self.__cache.node = N

        # Wait for scene to finish
        scene()

        # synchronized context to render voxels
        voxels = TQ.dispatch(lambda: self.getVoxelRenderer(N))

        # Await voxels
        S.add(voxels())

    def run(self, TQ: TaskQueue, S: s.Scene):
        if not self.config.run.get():
            return

        node = self.__cache.refNode()

        # No node, no actions
        if node is None:
            return

        # Get voxel object
        V = self.buildVoxelsObject(node)
        # Build truss
        T = v2t.voxels2truss(V)
        # Make mesh
        M = m.Mesh(T.nodes, T.edges, m.Geometry.Lines)
        # Simulate Truss
        D, _ = fem.fem_simulate(T, 1E3)

        # Build wireframe on main thread
        @TQ.dispatch
        def wireframe():
            # return Wireframe(M)
            return DeformationWireframe(M, D)

        # Create transform
        T = glm.translate(glm.vec3(*node.data.box.start))

        # Get wireframe
        W = wireframe()
        # W.setColor(c.Color(0.1, 0.1, 0.1, 0.2))
        W.setWidth(2.0)

        # Add to scene
        S.children.insert(0, s.Transform(T, W))

        # Return def-frame¨
        return W
