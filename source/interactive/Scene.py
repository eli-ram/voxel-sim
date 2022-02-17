from typing import Protocol
from ..utils.matrices import Hierarchy
from ..utils.types import float3
from dataclasses import dataclass, field
from OpenGL.GL import *
import glm


class Render(Protocol):
    """ General Renderable Object Interface """

    def render(self, m: Hierarchy) -> None: ...


@dataclass
class Transform:
    transform: glm.mat4
    mesh: Render
    hidden: bool = False

    def render(self, m: Hierarchy):
        if self.hidden:
            return
        with m.Push(self.transform):
            self.mesh.render(m)


@dataclass
class Scene:
    transform: glm.mat4 = glm.mat4()
    children: list[Render] = field(default_factory=list)
    show: bool = True

    def add(self, child: Render):
        self.children.append(child)

    def insert(self, index: int, child: Render):
        self.children.insert(index, child)

    def render(self, m: Hierarchy):
        if self.show:
            with m.Push(self.transform):
                for child in self.children:
                    child.render(m)


class Void:
    def render(self, m: Hierarchy):
        pass


class Base:
    children: list[Render]

    def __init__(self, background: float3, alpha: float = 1.0):
        glEnable(GL_DEPTH_TEST)
        glClearColor(*background, alpha)
        self.stack = Hierarchy()
        self.children = []

    def add(self, child: Render):
        self.children.append(child)

    def insert(self, index: int, child: Render):
        self.children.insert(index, child)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        for child in self.children:
            child.render(self.stack)
