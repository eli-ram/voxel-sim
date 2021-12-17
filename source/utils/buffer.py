from typing import Any, Literal
from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
from OpenGL.arrays.numpymodule import NumpyHandler, ARRAY_TO_GL_TYPE_MAPPING # type: ignore
from ctypes import c_void_p as ptr
from dataclasses import dataclass

from .types import Array, N
import numpy as np


@dataclass
class BufferView:
    # 0 => tighty packed
    stride: int = 0
    start: int = 0

    def __add__(self, offset: int):
        return BufferView(self.stride, self.start + offset)


TARGET_MAP: dict[str, Any] = {
    "vertices": GL_ARRAY_BUFFER,
    "indices": GL_ELEMENT_ARRAY_BUFFER,
}
TARGET_OPTS = Literal["vertices", "indices"]


@dataclass
class BufferConfig:
    target: TARGET_OPTS
    norm: bool = False

    def element_size(self, array: 'Array[N]'):
        D = len(array.shape)
        assert D <= 2, \
            "Cannot infer size for array !"
        size = array.shape[1] if D == 2 else 1
        assert size in (1, 2, 3, 4), \
            "Size must be one of (1, 2, 3, 4) !"
        return size

    def element_type(self, array: 'Array[N]') -> Any:
        return ARRAY_TO_GL_TYPE_MAPPING[array.dtype] # type: ignore
        # return NumpyHandler.arrayToGLType(array)  # type: ignore

    def element_stride(self, array: 'Array[N]'):
        if self.target == 'indices':
            # Using stride as element count
            return array.size
        return 0

    def array_buffer(self, array: 'Array[N]'):
        usage: Any = GL_STATIC_DRAW
        target = TARGET_MAP[self.target]
        return VBO(array, usage, target)

    def single(self, array: 'Array[N]', *, views: list[BufferView] = []):
        if not views:
            stride = self.element_stride(array)
            views = [BufferView(stride=stride)]

        return Buffer(
            vbo=self.array_buffer(array),
            size=self.element_size(array),
            type=self.element_type(array),
            norm=GL_TRUE if self.norm else GL_FALSE,
            views=views,
        )

    def combine(self, *arrays: 'Array[N]'):
        array = np.concatenate(arrays)
        bytes = [array.nbytes for array in arrays]
        stride = self.element_stride(array)
        first = BufferView(stride=stride, start=-bytes[0])
        views = [first := first + offset for offset in bytes]
        return self.single(array, views=views)


@dataclass
class Buffer:
    vbo: VBO
    size: int
    type: Any
    norm: Any
    views: list[BufferView]

    def __enter__(self):
        self.vbo.bind()
        return self.views

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        self.vbo.unbind()

    def attribute(self, view: BufferView, attr: int):
        glVertexAttribPointer(
            attr,               # attribute
            self.size,          # size
            self.type,          # type
            self.norm,          # normalize
            view.stride,        # stride
            ptr(view.start),    # start
        )

    def draw(self, view: BufferView, geometry: Any):
        glDrawElements(
            geometry,           # geometry type
            view.stride,        # geometry count
            self.type,          # index type
            ptr(view.start),    # index start
        )
