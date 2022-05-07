from typing import List
import glm

from source.data.transform import Transform


from .parse import all as p
from .parameters import Parameters
from .geometry import GeometryArray
from .material import Color, MaterialStore
from .box import Box

from source.interactive import scene as s
from source.utils.shapes import line_cube
from source.utils.wireframe.wireframe import Wireframe


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

    # Scene Matrix
    matrix = glm.mat4()

    def makeMatrix(self):
        B = self.region.box
        if B.is_empty:
            return glm.mat4()

        T = Transform()

        # Scale Scene
        S = 1 / min(B.shape)
        T.scale = glm.vec3(S, S, S)

        # Center Scene
        O = 0.5 * (B.start - B.stop) - B.start
        T.position = glm.vec3(*O)

        return T.matrix

    def postParse(self) -> None:
        self.matrix = self.makeMatrix()

    def addOutline(self, list: List[s.Render]):
        B = self.region.box
        if B.is_empty:
            return
        
        T = Transform()
        T.position = glm.vec3(0.5 * B.start)
        T.scale = glm.vec3(*B.shape)
        M = T.matrix
        W = Wireframe(line_cube())
        list.append(s.Transform(M, W))

        


class Configuration(p.Struct):
    # General Settings
    config: Config

    # Defined Materials
    materials: MaterialStore
    
    # Application order of Geometry
    geometry: GeometryArray
    
    # Machine Learning Parameters
    parameters: Parameters

    def postParse(self):
        store = self.materials.get()
        self.geometry.loadMaterials(store)

    def getRender(self) -> s.Render:
        transform = self.config.matrix
        children = self.geometry.getRenders()
        self.config.addOutline(children)
        return s.Scene(transform, children)

    def getBackground(self):
        return self.config.background.require()
        
