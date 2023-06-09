from typing import Any, List, Union, cast
from OpenGL import GL
from dataclasses import dataclass
from enum import IntEnum, Enum
from numpy import ndarray, float32, uint32
from ..utils.types import int2, int3, intN

Array = Union['ndarray[float32]', 'ndarray[uint32]']
OptArray = Union[Array, None]


class Sample(IntEnum):
    """ Texture sampling in shaders """
    NEAREST = GL.GL_NEAREST
    LINEAR = GL.GL_LINEAR


class Access(IntEnum):
    """ Allowed shader access """
    READ = GL.GL_READ_ONLY
    WRITE = GL.GL_WRITE_ONLY
    READ_WRITE = GL.GL_READ_WRITE


@dataclass
class FormatSet:
    internal_format: Any
    data_format: Any
    data_type: Any


class Format(Enum):
    """ Internal image format """
    RGBA_F32 = FormatSet(
        internal_format=GL.GL_RGBA32F,
        data_format=GL.GL_RGBA,
        data_type=GL.GL_FLOAT,
    )
    R_F32 = FormatSet(
        internal_format=GL.GL_R32F,
        data_format=GL.GL_RED,
        data_type=GL.GL_FLOAT,
    )
    R_UI8 = FormatSet(
        internal_format=GL.GL_R8UI,
        data_format=GL.GL_RED,
        data_type=GL.GL_UNSIGNED_INT
    )


class Wrap(IntEnum):
    """ Image wrapping """
    REPEAT = GL.GL_REPEAT
    CLAMP = GL.GL_CLAMP_TO_EDGE


@dataclass
class TextureProps:
    sample: Sample = Sample.LINEAR
    access: Access = Access.READ
    format: Format = Format.RGBA_F32
    wrap: Wrap = Wrap.CLAMP


class Texture:
    """ Generic Texture """
    TARGET: Any
    SETDATA: Any
    SUBSETDATA: Any

    def __init__(self, shape: intN, props: TextureProps):
        """ (Protected) Texture Constructor """
        self.handle = cast(int, GL.glGenTextures(1))
        self.props = props
        self.shape = shape
        self.bind(0)
        GL.glTexParameteri(
            self.TARGET, GL.GL_TEXTURE_MIN_FILTER, props.sample.value)
        GL.glTexParameteri(
            self.TARGET, GL.GL_TEXTURE_MAG_FILTER, props.sample.value)
        # vec3 tex = tex.str
        GL.glTexParameteri(self.TARGET, GL.GL_TEXTURE_WRAP_S, props.wrap.value)
        GL.glTexParameteri(self.TARGET, GL.GL_TEXTURE_WRAP_T, props.wrap.value)
        GL.glTexParameteri(self.TARGET, GL.GL_TEXTURE_WRAP_R, props.wrap.value)
        self.setData()

    def setData(self, data: OptArray = None, level: int = 0):
        f: FormatSet = self.props.format.value
        if data is not None:
            # todo shape stack per layer ?
            L = len(self.shape)
            self.shape = data.shape[:L]
            assert L == len(self.shape), \
                "Cannot set data of lower dimensionality"

        self.bind(0)
        self.SETDATA(
            self.TARGET,        # target
            level,              # level-of-detail
            f.internal_format,  # internal-format
            *self.shape,        # shape
            0,                  # border [must be 0]
            f.data_format,      # data-format
            f.data_type,        # data-type
            data,               # data
        )
        GL.glBindImageTexture(
            0,                  # unit
            self.handle,        # texture
            level,              # level-of-detail
            GL.GL_FALSE,        # layered
            0,                  # layer
            GL.GL_WRITE_ONLY,   # access
            f.internal_format,  # internal-format
        )

    def setPixels(self, offset: intN, data: Array, level: int = 0):
        f: FormatSet = self.props.format.value
        self.bind(0)
        self.SUBSETDATA(
            self.TARGET,    # target
            level,          # level-of-detail
            *offset,        # offset-in-image
            *data.shape,    # shape-of-data
            f.data_format,  # data-format
            f.data_type,    # data-type
            data.T,         # data
        )

    def bind(self, at: int):
        GL.glActiveTexture(cast(int, GL.GL_TEXTURE0) + at)
        GL.glBindTexture(self.TARGET, self.handle)


class Texture1D(Texture):
    TARGET = GL.GL_TEXTURE_1D
    SETDATA = GL.glTexImage1D
    SUBSETDATA = GL.glTexSubImage1D

    def __init__(self, size: int, props: TextureProps = TextureProps()) -> None:
        super().__init__((size,), props)


class Texture2D(Texture):
    TARGET = GL.GL_TEXTURE_2D
    SETDATA = GL.glTexImage2D
    SUBSETDATA = GL.glTexSubImage2D

    def __init__(self, size: int2, props: TextureProps = TextureProps()) -> None:
        super().__init__(size, props)


class Texture3D(Texture):
    TARGET = GL.GL_TEXTURE_3D
    SETDATA = GL.glTexImage3D
    SUBSETDATA = GL.glTexSubImage3D

    def __init__(self, size: int3, props: TextureProps = TextureProps()) -> None:
        super().__init__(size, props)


class TextureSet:
    """ Bind a set of textures in sequence """

    def __init__(self, start: int, textures: List[Texture]):
        self.start = start
        self.count = len(textures)
        self.textures = textures
        self.refresh()

    def refresh(self):
        self.ids = [t.handle for t in self.textures]

    def __enter__(self):
        GL.glBindTextures(self.start, self.count, self.ids)
        GL.glBindImageTextures(self.start, self.count, self.ids)

    def __exit__(self, type: Any, value: Any, traceback: Any):
        GL.glBindTextures(self.start, self.count, None)
        GL.glBindImageTextures(self.start, self.count, None)

    def swap(self, A: int, B: int):
        t = self.textures
        t[A], t[B] = t[B], t[A]
        self.refresh()

    def __getitem__(self, id: int):
        return self.textures[id]
