
from .texture import Texture
from typing import Any, Dict, cast
from OpenGL.GL import *  # type: ignore


class Framebuffer:

    def __init__(self):
        self.handle = cast(int, glGenFramebuffers(1))

    def output(self, texture: Texture):
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture.handle, 0)

    def check(self):
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        options: Dict[Any, str] = {
            GL_FRAMEBUFFER_COMPLETE: 'complete',
            GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT: 'incomplete attachment',
            # GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS : 'missing dimensions',
            GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: 'missing attachment',
            GL_FRAMEBUFFER_UNSUPPORTED: 'unsupported',
        }
        result = options.get(status, 'unknown')

        print(f"Framebuffer status: {result} ({status})")

    def __enter__(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.handle)

    def __exit__(self, type: Any, value: Any, traceback: Any):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
