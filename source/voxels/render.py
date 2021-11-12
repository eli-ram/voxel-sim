# pyright: reportUnknownMemberType=false, reportGeneralTypeIssues=false, reportUnknownVariableType=false
from typing import Any
from OpenGL.GL import *  # type: ignore
from OpenGL.arrays.vbo import VBO  # type: ignore
import numpy as np

from source.utils.texture import Format, Sample, Size_3D, Texture1D, Texture3D, TextureProps, Wrap

from ..utils.matrices import Hierarchy
from ..utils.shaders import ShaderCache, ShaderUniforms, ShaderAttributes
from ..utils.directory import cwd, script_dir


class VoxelAttrs(ShaderAttributes):
    t: int


class VoxelUniforms(ShaderUniforms):
    MVP: int
    COLORS: int
    VOXELS: int
    LAYER_DIR: int
    MOD_ALPHA: int
    ENB_OUTLINE: int


class VoxelShader(ShaderCache):

    @cwd(script_dir(__file__), 'shaders')
    def __init__(self):
        self.S = self.compile('voxel.vert', 'voxel.geom', 'voxel.frag')
        self.A = VoxelAttrs(self.S)
        self.U = VoxelUniforms(self.S)


class VoxelGrid:
    """
        Each Voxel is represented by a single float.

        Voxels with a value below 1.0 is considered void-voxels,
        theese will not be drawn.

        Voxels with a value equal or greater than 1.0 is actual voxels,
        theese will be drawn.

        The Value is used to 1-index the color array,
        which is in a RGBA float32 format.
        Values that are close to integers will directly get a single color.
        Values that are in between will interpolate between two colors.
        Warning: does not work if there are fewer than 3 colors !
    """

    # Each voxel is represented by a single float
    VOXEL_FMT = TextureProps(
        sample=Sample.NEAREST,
        format=Format.R_F32,
        wrap=Wrap.CLAMP,
    )

    # Each non-void voxel refers to a color
    COLOR_FMT = TextureProps(
        sample=Sample.LINEAR,
        format=Format.RGBA_F32,
        wrap=Wrap.REPEAT,
    )

    def __init__(self, shape: Size_3D, layer_count: int = 64):
        self.shader = VoxelShader.get()

        self.alpha = 0.5
        self.shape = shape
        self.count = layer_count
        self.outline = True

        data = np.linspace(0.0, 1.0, num=layer_count, dtype=np.float32)
        self.planes = VBO(data)

        with self.shader.A, self.planes:
            glVertexAttribPointer(self.shader.A.t, 1,
                                  GL_FLOAT, GL_FALSE, 0, None)

        colors = 3

        self.voxels = Texture3D(shape, self.VOXEL_FMT)
        self.colors = Texture1D(colors, self.COLOR_FMT)

        self.RNG = np.random.default_rng()
        color_data: Any = self.RNG.random(size=(colors, 4), dtype=np.float32)
        color_data[:, 3] = 1  # fix alpha
        self.colors.setData(color_data)
        self.S = np.ones((1,1,1), dtype=np.float32)

    @property
    def color_count(self) -> int:
        return self.colors.shape[0]

    def set(self, pos: Size_3D, color: float):
        self.voxels.setPixels(pos, self.S * color)

    def setBox(self, pos: Size_3D, colors: 'np.ndarray[np.float32]'):
        self.voxels.setPixels(pos, colors)

    def clear(self, pos: Size_3D):
        self.voxels.setPixels(pos, (1, 1, 1), 0)

    def clearBox(self, pos: Size_3D, shape: Size_3D):
        self.voxels.setPixels(pos, np.zeros(shape, dtype=np.float32))

    def randBox(self, max_size: int = 8):
        RNG = self.RNG
        SHAPE: Any = 1 + RNG.integers(max_size, size=3)
        MIN: Any = RNG.integers(self.shape - SHAPE + 1, size=3)
        COLOR: Any = RNG.integers(0, 1 + self.color_count)
        COLORS = np.ones(shape=SHAPE, dtype=np.float32) * COLOR
        self.setBox(MIN, COLORS)

    def getLayerDirection(self, h: Hierarchy) -> int:
        DIR = h.GetCameraDirection()
        return np.argmax([-DIR, DIR])

    def render(self, h: Hierarchy):
        # Make sure blending is enabled
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Bind Textures
        self.voxels.bind(0)
        self.colors.bind(1)

        # Bind Uniforms & Render
        with self.shader.S, self.shader.A, self.planes:
            U = self.shader.U
            glUniformMatrix4fv(U.MVP, 1, GL_TRUE, h.ptr(h.MVP))
            glUniform1i(U.LAYER_DIR, self.getLayerDirection(h))
            # TODO: scale alpha by voxel-layer-ratio ?
            glUniform1f(U.MOD_ALPHA, self.alpha)
            glUniform1i(U.ENB_OUTLINE, self.outline)
            glVertexAttribPointer(
                self.shader.A.t,    # attribute
                1,                  # size
                GL_FLOAT,           # type
                GL_FALSE,           # normalize
                0,                  # stride    (0 => tighty packed)
                None,               # start     (None => start at 0)
            )
            glDrawArrays(GL_POINTS, 0, self.count)
