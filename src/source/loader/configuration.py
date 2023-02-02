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

    def buildScene(self, geometry: s.Scene):
        """ Build the scene presented to the user """
        B = self.region.box

        # If no region, just present the geometry
        if B.is_empty:
            return geometry

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
        return s.Scene(matrix, [geometry, bbox])

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
    scene: s.Scene
    renderer: VoxelRenderer

    def getNode(self, G: Geometry, C: Config):
        # Make context
        ctx = C.buildContext()
        # No context -> no geometry
        if ctx is None:
            return None

        # Get Geometry voxels
        N = G.getVoxels(ctx)

        # Return Corrected voxels
        self.node = ctx.finalize(N)
        return self.node

    def getRenderer(self, shape: t.int3, count: int):
        # Check if cached value can be re-used
        if hasattr(self, 'renderer'):
            R = self.renderer
            if R.shape == shape and R.count == count:
                return R

        # Build new
        R = VoxelRenderer(shape, count)
        self.renderer = R
        return R

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

    def configure(self, TQ: TaskQueue):
        """ Process config (called from parser thread) """

        print("Processing config ...")

        # Get background color
        BG = self.config.background.require()

        # synchronized context to render scene
        @TQ.dispatch
        def render():
            # Get the geometry
            R = self.geometry.getRender()

            # Return the scene
            return self.config.buildScene(R)

        # Compute voxels
        N = self.__cache.getNode(self.geometry, self.config)

        # Wait for render to finish
        R = render()
        self.__cache.scene = R

        # Not configured for voxels
        if N is None:
            print("Cannot build voxels")
            return R, BG

        # synchronized context to render voxels
        @TQ.dispatch
        def voxels():
            # Build voxel renderer
            return self.getVoxelRenderer(N)

        # Wait for voxels to finish
        R.add(voxels())

        # Return scene
        return R, BG

    def run(self, TQ: TaskQueue):
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
        # D, _ = fem.fem_simulate(T, 1E3)

        # Build wireframe on main thread
        @TQ.dispatch
        def wireframe():
            return Wireframe(M)
            # return DeformationWireframe(M, D)

        # Create transform
        T = glm.translate(glm.vec3(*node.data.box.start))

        # Get wireframe
        W = wireframe()
        W.setColor(c.Color(0.1, 0.1, 0.1, 0.2))

        # Add to scene
        S = self.__cache.scene
        S.children.insert(0, s.Transform(T, W))

        # Return def-frame¨
        return W
