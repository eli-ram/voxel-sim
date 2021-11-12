from typing import Any, Callable, Type, TypeVar, cast
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import (  # type: ignore
    ShaderProgram,
    ShaderCompilationError,
    compileShader,
    compileProgram,
)
from os.path import splitext
from functools import wraps

def shaderprune(func: Any):
    def print_source(source: bytes):
        lines = source.decode("utf-8").split("\n")
        for i, line in enumerate(lines):
            print(f"{(i+1):3}| {line}")

    def wrap(*args: Any, **kwargs: Any):
        try:
            return func(*args, **kwargs)
        except ShaderCompilationError as e:
            msg, sources, type = e.args
            head, errs = msg.split('b', 1)
            print(f"[{type}] {head}")
            print(eval(errs))
            for source in sources:
                print_source(source)
        raise Exception("Shader Fault")

    return wrap


def shader(*files: str):
    __mapping__ = {  # type: ignore
        '.vert': GL_VERTEX_SHADER,
        '.comp': GL_COMPUTE_SHADER,
        '.geom': GL_GEOMETRY_SHADER,
        '.frag': GL_FRAGMENT_SHADER,
    }

    @shaderprune
    def compile(file: str) -> int:
        _, ext = splitext(file)
        with open(file, 'r') as f:
            return compileShader(f.read(), __mapping__[ext])  # type: ignore

    return compileProgram(*(compile(file) for file in files))

def bind(shader: ShaderProgram):
    def wrapper(func: Any):
        @wraps(func)
        def wrap(*args: Any, **kwargs: Any):
            with shader:
                return func(*args, **kwargs)
        return wrap
    return wrapper

Binding = Callable[[int, str], int]

class ShaderBindings:

    def __new__(cls, *args: Any, **kwargs: Any):
        annotations = cls.__annotations__
        cls = super().__new__(cls)
        cls._fields = annotations.keys()
        return cls

    def __init__(self, shader: ShaderProgram, get: Binding):
        with shader:
            for field in self._fields:
                setattr(self, field, get(shader, field))

    def __iter__(self):
        for field in self._fields:
            yield cast(int, getattr(self, field))

    def __str__(self):
        binds = (f"{field}={getattr(self, field)}" for field in self._fields)
        return f"{self.__class__.__name__}({', '.join(binds)})"

    def __call__(self):
        print(self)
        return self

class ShaderUniforms(ShaderBindings):

    def __init__(self, shader: ShaderProgram):
        super().__init__(shader, glGetUniformLocation)
    
class ShaderAttributes(ShaderBindings):

    def __init__(self, shader: ShaderProgram):
        super().__init__(shader, glGetAttribLocation)

    def __enter__(self):
        for i in self:
            glEnableVertexAttribArray(i)

    def __exit__(self, type: Any, value: Any, traceback: Any):
        for i in self:
            glDisableVertexAttribArray(i)

T = TypeVar('T', bound='ShaderCache')

class ShaderCache:
        
    @classmethod
    def compile(cls, *files: str):
        assert not hasattr(cls, '__cache__'), \
            f"Cache for {cls.__name__} was reinitialized!"
        return shader(*files)

    @classmethod
    def get(cls: Type[T]) -> T:
        if not hasattr(cls, '__cache__'):
            setattr(cls, '__cache__', cls())
        return getattr(cls, '__cache__')
