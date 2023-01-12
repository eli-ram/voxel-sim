from typing import Any, List, Union, cast
from OpenGL.GL import *  # type: ignore
from dataclasses import dataclass
from enum import IntEnum, Enum
from numpy import ndarray, float32, uint32
from ..utils.types import int2, int3, intN

Array = Union['ndarray[float32]', 'ndarray[uint32]']
OptArray = Union[Array, None]

class Sample(IntEnum):
    """ Texture sampling in shaders """
    NEAREST = GL_NEAREST
    LINEAR = GL_LINEAR


class Access(IntEnum):
    """ Allowed shader access """
    READ = GL_READ_ONLY
    WRITE = GL_WRITE_ONLY
    READ_WRITE = GL_READ_WRITE


@dataclass
class FormatSet:
    internal_format: Any
    data_format: Any
    data_type: Any


class Format(Enum):
    """ Internal image format """
    RGBA_F32 = FormatSet(
        internal_format=GL_RGBA32F,
        data_format=GL_RGBA,
        data_type=GL_FLOAT,
    )
    R_F32 = FormatSet(
        internal_format=GL_R32F,
        data_format=GL_RED,
        data_type=GL_FLOAT,
    )
    R_UI8 = FormatSet(
        internal_format=GL_R8UI,
        data_format=GL_RED,
        data_type=GL_UNSIGNED_INT
    )


class Wrap(IntEnum):
    """ Image wrapping """
    REPEAT = GL_REPEAT
    CLAMP = GL_CLAMP_TO_EDGE


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
        self.handle = cast(int, glGenTextures(1))
        self.props = props
        self.shape = shape
        self.bind(0)
        glTexParameteri(self.TARGET, GL_TEXTURE_MIN_FILTER, props.sample.value)
        glTexParameteri(self.TARGET, GL_TEXTURE_MAG_FILTER, props.sample.value)
        # vec3 tex = tex.str
        glTexParameteri(self.TARGET, GL_TEXTURE_WRAP_S, props.wrap.value)
        glTexParameteri(self.TARGET, GL_TEXTURE_WRAP_T, props.wrap.value)
        glTexParameteri(self.TARGET, GL_TEXTURE_WRAP_R, props.wrap.value)
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
        glBindImageTexture(
            0,                  # unit
            self.handle,        # texture
            level,              # level-of-detail
            GL_FALSE,           # layered
            0,                  # layer
            GL_WRITE_ONLY,      # access
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
        glActiveTexture(cast(int, GL_TEXTURE0) + at)
        glBindTexture(self.TARGET, self.handle)


class Texture1D(Texture):
    TARGET = GL_TEXTURE_1D
    SETDATA = glTexImage1D
    SUBSETDATA = glTexSubImage1D

    def __init__(self, size: int, props: TextureProps = TextureProps()) -> None:
        super().__init__((size,), props)


class Texture2D(Texture):
    TARGET = GL_TEXTURE_2D
    SETDATA = glTexImage2D
    SUBSETDATA = glTexSubImage2D

    def __init__(self, size: int2, props: TextureProps = TextureProps()) -> None:
        super().__init__(size, props)


class Texture3D(Texture):
    TARGET = GL_TEXTURE_3D
    SETDATA = glTexImage3D
    SUBSETDATA = glTexSubImage3D

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
        glBindTextures(self.start, self.count, self.ids)
        glBindImageTextures(self.start, self.count, self.ids)

    def __exit__(self, type: Any, value: Any, traceback: Any):
        glBindTextures(self.start, self.count, None)
        glBindImageTextures(self.start, self.count, None)

    def swap(self, A: int, B: int):
        t = self.textures
        t[A], t[B] = t[B], t[A]
        self.refresh()

    def __getitem__(self, id: int):
        return self.textures[id]
