
from typing import Any, TypeVar
from contextlib import contextmanager
import os

def require(base: str, *extra: str):
    path = os.path.join(base, *extra)
    os.makedirs(path, exist_ok=True)
    return path

@contextmanager
def directory(base: str, *extra: str):
    path = os.path.join(base, *extra)
    prev = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(prev)

Func = TypeVar('Func')

def cwd(base: str, *extra: str):
    def capture(func: Func) -> Func:
        def wrap(*args: Any, **kwargs: Any) -> Any:
            with directory(base, *extra):
                return func(*args, **kwargs) # type: ignore
        return wrap # type: ignore
    return capture

def script_dir(__file__: str):
    return os.path.dirname(os.path.realpath(__file__))

