from typing import Callable, Optional, TypeVar
import glm

__all__ = [
    "Transform",
]

T = TypeVar("T")
S = TypeVar("S")
M = Callable[[S], T]


class Cache:
    def __init__(self):
        self.attrs = set[str]()

    def __call__(self, name: str):
        self.attrs.add(name)

        def wrapper(method: M[S, T]) -> M[S, T]:
            def wrap(self: S):
                if not hasattr(self, name):
                    setattr(self, name, method(self))
                return getattr(self, name)
            return wrap
        return wrapper

    def invalidate(self, target):
        for attr in self.attrs:
            if hasattr(target, attr):
                delattr(target, attr)


cache = Cache()


class Transform:
    scale = glm.vec3(1, 1, 1)
    rotation = glm.quat()
    position = glm.vec3()

    parent: 'Optional[Transform]'

    @property
    @cache('_wtl')
    def world_to_local(self):
        return self.makeWorldToLocal()

    @property
    @cache('_ltw')
    def local_to_world(self):
        return self.makeLocalToWorld()

    @property
    @cache('_mat')
    def matrix(self) -> glm.mat4:
        S = glm.scale(self.scale)
        P = glm.translate(self.position)
        R = glm.mat4_cast(self.rotation)
        # Scale => Rotate => Translate
        return P * R * S

    def invalidate(self):
        cache.invalidate(self)

    def makeLocalToParent(self) -> glm.mat4:
        return self.matrix

    def makeParentToLocal(self) -> glm.mat4:
        M = self.makeLocalToParent()
        return glm.affineInverse(M)

    def makeLocalToWorld(self) -> glm.mat4:
        M = self.makeLocalToParent()
        if P := self.parent:
            return P.makeLocalToWorld() * M
        return M

    def makeWorldToLocal(self) -> glm.mat4:
        M = self.makeParentToLocal()
        if P := self.parent:
            return M * P.makeWorldToLocal()
        return M
