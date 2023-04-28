from typing import Any, Callable, Generic, Type, TypeVar, Optional, cast
from OpenGL import GL  # type: ignore
from OpenGL.GL.shaders import (  # type: ignore
    ShaderProgram,
    ShaderCompilationError,
    compileShader,
    compileProgram,
)
from ..utils.directory import script_dir, directory, content, prefix
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
        '.vert': GL.GL_VERTEX_SHADER,
        '.comp': GL.GL_COMPUTE_SHADER,
        '.geom': GL.GL_GEOMETRY_SHADER,
        '.frag': GL.GL_FRAGMENT_SHADER,
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
    """ [InternalClass] Setup Binding class 

        caches annotations as _fields, 
        allowing lookup using a getter in init method
    """

    def __new__(cls, *args: Any, **kwargs: Any):
        annotations = getattr(cls, '__annotations__', {})
        cls = super().__new__(cls)
        cls._fields = annotations.keys()
        return cls

    def __init__(self, shader: ShaderProgram, get: Binding):

        # Binding method
        def bind(field):
            value = get(shader, field)
            setattr(self, field, value)
            return cast(int, value)

        # Collect fields
        with shader:
            self._list = [bind(field) for field in self._fields]

    def __iter__(self):
        return iter(self._list)

    def __str__(self):
        binds = (f"{field}={getattr(self, field)}" for field in self._fields)
        return f"{self.__class__.__name__}({', '.join(binds)})"


class ShaderUniforms(ShaderBindings):
    """ Define shader uniforms (type should be <int>) """

    def __init__(self, shader: ShaderProgram):
        super().__init__(shader, GL.glGetUniformLocation)


class ShaderAttributes(ShaderBindings):
    """ Define shader attributes (type should be <int>) """

    def __init__(self, shader: ShaderProgram):
        super().__init__(shader, GL.glGetAttribLocation)


S = TypeVar('S', bound='ShaderCache[Any, Any]')
A = TypeVar('A', bound=ShaderAttributes)
U = TypeVar('U', bound=ShaderUniforms)


class ShaderCache(Generic[A, U]):
    """ Define shader using generics [Attributes, Uniforms] """

    FILE: str       # __file__ to find script_dir
    CODE: list[str]  # list of source code
    GLOB: str       # directory if source code [overrides CODE if set]
    DEBUG = False   # enable debugging

    def __init__(self):
        self.S = self.compile()
        base, = self.__orig_bases__  # type: ignore
        acls, ucls = base.__args__  # type: ignore
        self.A: A = acls(self.S)
        self.U: U = ucls(self.S)
        self.dbg(self.A)
        self.dbg(self.U)

    @classmethod
    def dbg(cls, *args):
        if cls.DEBUG:
            print(f"[{cls.__name__}]", *args)

    @classmethod
    def compile(cls):
        assert not hasattr(cls, '__cache__'), \
            f"Cache for {cls.__name__} was reinitialized!"
        with directory(script_dir(cls.FILE)):
            if hasattr(cls, 'GLOB'):
                cls.CODE = prefix(content(cls.GLOB), cls.GLOB)
            cls.dbg('Sources:', *[f"\n - {file}" for file in cls.CODE])
            return shader(*cls.CODE)

    @classmethod
    def get(cls: Type[S]) -> S:
        if not hasattr(cls, '__cache__'):
            cls.dbg("Initializing ...")
            setattr(cls, '__cache__', cls())  # type: ignore
            cls.dbg("Initialized !")
        return getattr(cls, '__cache__')

    def __enter__(self):
        self.S.__enter__()
        for i in self.A:
            GL.glEnableVertexAttribArray(i)
        return (self.A, self.U)

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        for i in self.A:
            GL.glDisableVertexAttribArray(i)
        self.S.__exit__(exc_type, exc_val, exc_tb)  # type: ignore
