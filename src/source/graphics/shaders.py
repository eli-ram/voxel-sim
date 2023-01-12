from typing import Any, Callable, Generic, Type, TypeVar, cast
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import (  # type: ignore
    ShaderProgram,
    ShaderCompilationError,
    compileShader,
    compileProgram,
)
from ..utils.directory import script_dir, directory
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
        annotations = getattr(cls, '__annotations__', {})
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


class ShaderUniforms(ShaderBindings):

    def __init__(self, shader: ShaderProgram):
        super().__init__(shader, glGetUniformLocation)


class ShaderAttributes(ShaderBindings):

    def __init__(self, shader: ShaderProgram):
        super().__init__(shader, glGetAttribLocation)


S = TypeVar('S', bound='ShaderCache[Any, Any]')
A = TypeVar('A', bound=ShaderAttributes)
U = TypeVar('U', bound=ShaderUniforms)


class ShaderCache(Generic[A, U]):
    FILE: str
    CODE: list[str]
    DEBUG = False

    def __init__(self):
        self.S = self.compile()
        base, = self.__orig_bases__ # type: ignore
        acls, ucls = base.__args__ # type: ignore
        self.A: A = acls(self.S)
        self.U: U = ucls(self.S)
        if self.DEBUG:
            print(self.A)
            print(self.U)

    @classmethod
    def compile(cls):
        assert not hasattr(cls, '__cache__'), \
            f"Cache for {cls.__name__} was reinitialized!"
        with directory(script_dir(cls.FILE)):
            return shader(*cls.CODE)

    @classmethod
    def get(cls: Type[S]) -> S:
        if not hasattr(cls, '__cache__'):
            setattr(cls, '__cache__', cls())  # type: ignore
        return getattr(cls, '__cache__')

    def __enter__(self):
        self.S.__enter__()
        for i in self.A:
            glEnableVertexAttribArray(i)
        return (self.A, self.U)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        for i in self.A:
            glDisableVertexAttribArray(i)
        self.S.__exit__(exc_type, exc_val, exc_tb)  # type: ignore
