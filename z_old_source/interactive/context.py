import atexit
import glfw # type: ignore

class UninitializedException(Exception):
    " Something critical was not able to initialize "

    @classmethod
    def check(cls, item: bool, name: str):
        if not item:
            raise cls(f"no {name}")

UninitializedException.check(glfw.init(), "glfw")
atexit.register(glfw.terminate)
