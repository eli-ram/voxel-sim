# pyright: reportUnknownMemberType=false, reportGeneralTypeIssues=false, reportUnknownVariableType=false
from OpenGL.GL import *  # type: ignore
from OpenGL.arrays.vbo import VBO  # type: ignore
import numpy as np
import glm

from ..utils.texture import Format, Sample, Texture1D, Texture3D, TextureProps, Wrap
from ..utils.types import int3
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


class VoxelRenderer:
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
        wrap=Wrap.CLAMP,
    )

    def __init__(self, shape: int3, layer_count: int = 64):
        self.shader = VoxelShader.get()

        # Shader Uniform Values
        self.alpha = 0.5
        self.shape = shape
        self.outline = True

        # The final for the voxels Transform
        self.transform = glm.scale(glm.vec3(*shape))

        # Rendering Layer Stack
        data = np.linspace(0.0, 1.0, num=layer_count, dtype=np.float32)
        self.count = layer_count
        self.planes = VBO(data)

        with self.shader.A, self.planes:
            glVertexAttribPointer(
                self.shader.A.t,    # index
                1,                  # size
                GL_FLOAT,           # type
                GL_FALSE,           # normalize
                0,                  # stride    (0 = tightly packed)
                None,               # start     (None = start at 0)
            )

        # Voxel Textures [3d-grid & colors]
        self.voxels = Texture3D(shape, self.VOXEL_FMT)
        self.colors = Texture1D(1, self.COLOR_FMT)

    def set_colors(self, colors: 'np.ndarray[np.float32]'):
        S = colors.shape
        assert len(S) == 2 and S[1] == 4, \
            "Color array shape must be [Nx4]"
        assert colors.dtype == np.float32, \
            "Color array data format must be float32"
        self.colors.setData(colors)

    @property
    def color_count(self) -> int:
        return self.colors.shape[0]

    def set(self, pos: int3, color: float):
        color = np.full((1, 1, 1), color, np.float32)
        self.voxels.setPixels(pos, color)

    def setBox(self, pos: int3, colors: 'np.ndarray[np.float32]'):
        self.voxels.setPixels(pos, colors)

    def clear(self, pos: int3):
        self.voxels.setPixels(pos, (1, 1, 1), 0)

    def clearBox(self, pos: int3, shape: int3):
        self.voxels.setPixels(pos, np.zeros(shape, dtype=np.float32))

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

        # Calculate full MVP transform
        MVP = h.MVP * self.transform

        # Bind Uniforms & Render
        with self.shader.S, self.shader.A, self.planes:
            U = self.shader.U
            glUniformMatrix4fv(U.MVP, 1, GL_TRUE, h.ptr(MVP))
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
