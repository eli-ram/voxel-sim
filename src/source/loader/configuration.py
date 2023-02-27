from functools import cache

import glm
import numpy as np

import source.ml.ga as ga
import source.data.mesh as m
import source.parser.all as p
import source.utils.types as t
import source.data.voxels as v
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
from .geometry import GeometryCollection, Context
from .material import Color, MaterialStore
from .box import Box
from .utils import Cache, Attr, cache

class Mode(p.Enum):
    # Setup mode (default)
    setup: p.Empty
    # Build voxels
    build: p.Empty
    # Sample parameters
    sample: p.Empty
    # Run simulation / ga
    run: p.Empty

    def postParse(self) -> None:
        K = self.variant() if self.ok() else "setup"
        self._run = K == "run"
        self._sample = K == "sample"
        self._build = self._run or self._sample or K == "build"
        self._setup = True



class Config(p.Struct):
    # Run simulation / ga
    mode: Mode

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

    # Output file for results
    output: p.String

    @cache
    def unitBox(self):
        return Wireframe(line_cube())

    def buildScene(self):
        """ Build the scene presented to the user """
        B = self.region.box

        # If no region, just present the geometry
        if B.is_empty:
            return s.Scene()

        ubox = self.unitBox()

        # Build the region bounding box
        bbox = s.Transform((
            # translate to origin of the box
            glm.translate(glm.vec3(*B.start))
            # scale the box to match
            * glm.scale(glm.vec3(*B.shape))
        ), ubox)

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
        if not self.mode._build:
            return None
        # Get box
        B = self.region.box
        # Unable to build with no box
        if B.is_empty:
            return None
        # Create context
        return Context(B)


class _Cache(Cache):
    ga: Attr[ga.GA]
    node: Attr[n.VoxelNode]
    renderer: Attr[VoxelRenderer]


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

    @cache
    def cache(self):
        return _Cache()

    def getVoxelRenderer(self, D: n.Data):
        # Get config
        C = self.config
        # Instance voxel renderer
        shape = D.material.shape
        count = C.resolution.getOr(256)
        V = self.cache().renderer.opt()
        # Build if missing or invalidated
        if not V or V.shape != shape or V.count != count:
            V = VoxelRenderer(shape, count)
            self.cache().renderer.set(V)
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
            S.opt(self.parameters.buildRender())

        # Compute voxels

        # Not configured for voxels
        ctx = self.config.buildContext()
        if ctx is None:
            print("Cannot build voxels")
            return

        # Build voxels
        node = ctx.finalize(self.geometry.buildVoxels(ctx))
        self.cache().node.set(node)

        # Build tmp rod
        if self.config.mode._sample:
            ROD = ctx.finalize(self.parameters.sample(ctx))
            node = n.VoxelNode.Parent(n.Operation.OVERWRITE, [node, ROD])
            self.cache().node.set(node)

        # Wait for scene to finish
        scene()

        # synchronized context to render voxels
        voxels = TQ.dispatch(lambda: self.getVoxelRenderer(node.data))

        # Await voxels
        S.add(voxels())

    def buildDeformation(self, TQ: TaskQueue, S: s.Scene):
        if not self.config.mode._sample:
            return

        node = self.cache().node.opt()

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

        # simulation failed
        if not D:
            return

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

    def buildAlgorithm(self):
        if not self.config.mode._run:
            return

        ctx = self.config.buildContext()
        if not ctx:
            return

        node = self.cache().node.opt()
        if not node:
            return

        P = self.parameters
        M = self.materials

        C = ga.Config(
            ctx=ctx.push(P.transform.matrix),
            # matrix=P.transform.matrix,
            width=P.width.getOr(1.0),
            mat_a=P.volume_a.transform.matrix,
            mat_b=P.volume_b.transform.matrix,
            material=P.material.get(),
            op=P.operation.require(),
            node=node,
            forces=M.forces,
            statics=M.statics,
            seed=P.seed.get(),
            size=P.population_size.getOr(10),
            filename=self.config.output.getOr(self.getFilename())
        )

        # Check cache
        G = self.cache().ga.opt()

        # Check if unset or invalid
        if not G or G.config != C:
            G = ga.GA(C)
            self.cache().ga.set(G)

        # ok
        return G
