
from typing import Any
from contextlib import contextmanager
import os

@contextmanager
def directory(base: str, *extra: str):
    path = os.path.join(base, *extra)
    prev = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(prev)

def cwd(base: str, *extra: str):
    path = os.path.join(base, *extra)
    def capture(func: Any):
        def wrap(*args: Any, **kwargs: Any):
            prv = os.getcwd()
            os.chdir(path)
            try:
                return func(*args, **kwargs)
            finally:
                os.chdir(prv)
        return wrap
    return capture

def script_dir(__file__: str):
    return os.path.dirname(os.path.realpath(__file__))

