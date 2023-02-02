from functools import cache
import glm
import numpy as np
from source.interactive.tasks import TaskQueue

import source.parser.all as p
import source.data.voxels as v
import source.data.colors as c
import source.interactive.scene as s
import source.data.voxel_tree.node as n
from source.utils.types import int3
from source.utils.shapes import line_cube
from source.utils.wireframe.wireframe import Wireframe
from source.voxels.render import VoxelRenderer

from .parameters import Parameters
from .geometry import GeometryCollection, Context
from .material import Color, MaterialStore
from .box import Box


@cache
def unit_box():
    return Wireframe(line_cube())


class Config(p.Struct):
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


class VoxelRendererCache:
    renderer: VoxelRenderer

    def get(self, shape: int3, count: int):
        # Check if cached value can be re-used
        if hasattr(self, 'renderer'):
            R = self.renderer
            if R.shape == shape and R.count == count:
                return R

        # Build new
        R = VoxelRenderer(shape, count)
        self.renderer = R
        return R


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

    def getRender(self) -> s.Scene:
        # Get the geometry
        R = self.geometry.getRender()

        # Return the scene
        return self.config.buildScene(R)

    def getVoxels(self):
        # Make context
        C = self.config.buildContext()
        # No context -> no geometry
        if C is None:
            return None

        # Get Geometry voxels
        print("Context:", C.box)
        print(f"{C.matrix}")
        N = self.geometry.getVoxels(C)

        # Return Corrected voxels
        return C.finalize(N)

    __cache = VoxelRendererCache()

    def getVoxelRenderer(self, node: n.VoxelNode):
        # Get data
        D = node.data
        # Get config
        C = self.config
        # Instance voxel renderer
        V = self.__cache.get(
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

        # Get Config
        C = self.config

        # Get background color
        BG = C.background.require()

        # synchronized context to render scene
        render = TQ.dispatch(self.getRender)

        # Compute voxels
        N = self.getVoxels()

        # Wait for render to finish
        # getting return value here would be nice !
        R = render()
        
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