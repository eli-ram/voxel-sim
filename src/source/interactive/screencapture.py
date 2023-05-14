from ..utils.directory import directory
from datetime import datetime
from OpenGL import GL
from PIL import Image, ImageOps
import os


class Screencapture:
    def resize(self, w: int, h: int):
        self.offset = (0, 0)
        self.shape = (w, h)

    def captureframe(self) -> Image.Image:
        # Prepare data
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        # Read data
        data = GL.glReadPixels(  # type: ignore
            *self.offset,
            *self.shape,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
        )
        # Encode data
        image = Image.frombytes(  # type: ignore
            "RGBA",
            self.shape,
            data,
        )
        # Fix data
        return ImageOps.flip(image).convert("RGB")

    def save(self, dir, file: str):
        with directory(dir):
            if os.path.exists(file):
                print(f"Overwriting '{file}' !")
            self.captureframe().save(file)

    def screenshot(self, dir, file_fmt: str):
        return lambda: self.save(dir, file_fmt.format(datetime.now()))
