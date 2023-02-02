from functools import cache
from typing import List
import glm
import numpy as np

from source.interactive import scene as s
from source.utils.shapes import line_cube
from source.utils.wireframe.wireframe import Wireframe
from source.data.transform import Transform
from source.parser import all as p

from .parameters import Parameters
from .geometry.collection import GeometryCollection
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

    # Constrain Voxel Region
    region: Box

    # Render Resolution per voxel
    resolution: p.Int

    # Background color
    background: Color

    def buildScene(self, geometry: s.Render):
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

    def getBackground(self):
        return self.config.background.require()

    def getRender(self) -> s.Render:
        # Get the geometry
        R = self.geometry.getRender()

        # Return the scene
        return self.config.buildScene(R)

    def getVoxels(self):
        # Make context
        C = self.geometry.makeContext()
        # Get Geometry voxels
        N = self.geometry.getVoxels(C)
        # Return
        return N