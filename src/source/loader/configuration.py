from functools import cache
import glm
import numpy as np
from source.interactive.tasks import TaskQueue

import source.parser.all as p
import source.interactive.scene as s
import source.data.voxel_tree.node as n
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

    # Voxel alpha
    alpha: p.Float

    # Constrain Voxel Region
    region: Box

    # Render Resolution per voxel
    resolution: p.Int

    # Background color
    background: Color

    def getResolution(self):
        return self.resolution.getOr(1024)

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

    def getResolution(self):
        return self.config.resolution.getOr(256)

    def getBackground(self):
        return self.config.background.require()

    def getRender(self) -> s.Scene:
        # Get the geometry
        R = self.geometry.getRender()

        # Return the scene
        return self.config.buildScene(R)

    def getVoxelRenderer(self, data: n.Data):
        # Get Materials
        M = data.material
        # Instance voxel renderer
        V = VoxelRenderer(M.shape, self.config.getResolution())
        # Set alpha
        V.alpha = self.config.alpha.getOr(0.9)
        # Set colors
        V.set_colors(self.materials.get().colors())
        # Set data
        V.fill(M.astype(np.float32))
        # Make transformation
        T = glm.translate(glm.vec3(*data.box.start))
        # Return renderer
        return V, T

    def getVoxels(self):
        # Make context
        C = self.config.buildContext()
        # No context -> no geometry
        if C is None:
            return None

        # Get Geometry voxels
        print("Context:", C.offset, C.shape)
        print(f"{C.matrix}")
        N = self.geometry.getVoxels(C)

        # Return Corrected voxels
        return C.finalize(N)


    def configure(self, TQ: TaskQueue, S: s.SceneBase):
        """ Process config (called from parser thread) """

        print("Processing config ...")

        # Get Config
        C = self.config

        # hack to get render-scene as local
        R = S

        # synchronized context to render scene
        @TQ.dispatch
        def render():
            nonlocal R, S

            # Set background
            S.setBackground(C.background.require())

            # Build scene
            R = self.getRender()

            # Append scene, include 3D cursor
            S.setChildren([R])

        # Compute voxels
        N = self.getVoxels()

        # Wait for render to finish
        render.wait()

        # Not configured for voxels
        if N is None:
            print("Did not build voxels")
            return

        # synchronized context to render voxels
        @TQ.dispatch
        def voxels():
            print("voxels:", N.data.box)
            # Build voxel renderer
            V, T = self.getVoxelRenderer(N.data) 
            # Transform renderer into the scene
            R.add(s.Transform(T, V))

        # Wait for voxels to finish
        voxels.wait()
