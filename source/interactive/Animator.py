
from ..utils.directory import script_dir, directory, require
from OpenGL.GL import *
from PIL import Image, ImageOps
import os

def force_filename_ext(filename: str, ext: str):
    name, fext = os.path.splitext(filename)
    output = f"{name}{ext}"
    if fext != ext:
        print(f"Converting {filename} to {output}!")
    return output


class Animator:
    PATH: str = require(script_dir(__file__), '..', '..', 'results')
    frames: list[Image.Image]
    
    def __init__(self, filename: str, delta: float = 0.2):
        self.recording = False
        self.filename = force_filename_ext(filename, '.gif')
        self.delta = delta

    def record(self, r: bool):
        if self.recording and not r:
            self.save()
        self.recording = r
        self.time = -self.delta
        self.frames = []

    def resize(self, w: int, h: int):
        self.offset = (0,0)
        self.shape = (w, h)
        self.frames = []

    def update(self, time: float, delta: float):
        if not self.recording:
            return time, delta
        self.time += self.delta
        if self.time > 0.0:
            self.frame()
        return self.time, self.delta

    def frame(self):
        print("Saving frame @", self.time)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels( # type: ignore
            *self.offset,
            *self.shape,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
        )
        image = Image.frombytes( # type: ignore
            'RGBA', 
            self.shape,
            data,
        )
        self.frames.append(ImageOps.flip(image))

    def save(self):
        print("Frames to save", len(self.frames))
        if not self.frames:
            return
        image, *images = self.frames
        with directory(self.PATH):
            if os.path.exists(self.filename):
                print(f"Overwriting {self.filename} !")
            image.save(
                self.filename,
                save_all=True,
                append_images=images,
                duration=self.time,
                loop=0,
            )
