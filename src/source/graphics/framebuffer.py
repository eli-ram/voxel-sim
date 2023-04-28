
from .texture import Texture
from typing import Any, Dict, cast
from OpenGL import GL


class Framebuffer:

    def __init__(self):
        self.handle = cast(int, GL.glGenFramebuffers(1))

    def output(self, texture: Texture):
        GL.glFramebufferTexture2D(GL.GL_FRAMEBUFFER, GL.GL_COLOR_ATTACHMENT0, GL.GL_TEXTURE_2D, texture.handle, 0)

    def check(self):
        status = GL.glCheckFramebufferStatus(GL.GL_FRAMEBUFFER)
        options: Dict[Any, str] = {
            GL.GL_FRAMEBUFFER_COMPLETE: 'complete',
            GL.GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT: 'incomplete attachment',
            # GL.GL_FRAMEBUFFER_INCOMPLETE_DIMENSIONS : 'missing dimensions',
            GL.GL_FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: 'missing attachment',
            GL.GL_FRAMEBUFFER_UNSUPPORTED: 'unsupported',
        }
        result = options.get(status, 'unknown')

        print(f"Framebuffer status: {result} ({status})")

    def __enter__(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.handle)

    def __exit__(self, type: Any, value: Any, traceback: Any):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, 0)
