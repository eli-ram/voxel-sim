from typing import List, Protocol
from ..graphics.matrices import Hierarchy
from source.data.colors import Color
from dataclasses import dataclass, field
from OpenGL import GL
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

    def __init__(self):
        GL.glEnable(GL.GL_DEPTH_TEST)
        self.stack = Hierarchy()
        self.children = []

    def setBackground(self, color: Color):
        GL.glClearColor(*color.value)

    def setChildren(self, children: List[Render]):
        self.children = children

    def setCamera(self, m: glm.mat4):
        self.stack.V = m

    def add(self, child: Render):
        self.children.append(child)
        return child

    def insert(self, index: int, child: Render):
        self.children.insert(index, child)

    def render(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)  # type: ignore
        for child in self.children:
            child.render(self.stack)
