from typing import Protocol
from ..graphics.matrices import Hierarchy
from ..utils.types import float3
from source.data import colors
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

    def toggle(self):
        self.hidden = not self.hidden

    def visible(self, show: bool):
        self.hidden = not show

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


class SceneBase:
    children: list[Render]

    def __init__(self, background: colors.Color):
        glEnable(GL_DEPTH_TEST)
        glClearColor(*background.value)
        self.stack = Hierarchy()
        self.children = []

    def add(self, child: Render):
        self.children.append(child)
        return child

    def insert(self, index: int, child: Render):
        self.children.insert(index, child)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        for child in self.children:
            child.render(self.stack)
