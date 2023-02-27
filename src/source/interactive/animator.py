
from datetime import datetime
from ..utils.directory import directory
from OpenGL import GL
from PIL import Image, ImageOps
import os

_results_dir = ['']
def setResultsDir(dir: str):
    _results_dir[0] = dir


def force_filename_ext(filename: str, ext: str):
    name, fext = os.path.splitext(filename)
    output = f"{name}{ext}"
    if fext != ext:
        print(f"Converting {filename} to {output}!")
    return output


class Animator:
    frames: list[Image.Image]
    
    def __init__(self, delta: float = 0.2):
        self.delta = delta
        self.frames = []
        self.recording = False

    def startRecording(self):
        self.time = -self.delta
        self.frames = []
        self.recording = True

    def stopRecording(self, file):
        self.save(file)
        self.frames = []
        self.recording = False

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
        # print("Saving frame @", self.time)
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        data = GL.glReadPixels( # type: ignore
            *self.offset,
            *self.shape,
            GL.GL_RGBA,
            GL.GL_UNSIGNED_BYTE,
        )
        image = Image.frombytes( # type: ignore
            'RGBA', 
            self.shape,
            data,
        )
        self.frames.append(ImageOps.flip(image))

    def save(self, file):
        print("Frames to save", len(self.frames))
        if not self.frames:
            return
        image, *images = self.frames
        filename = force_filename_ext(file, '.gif')
        with directory(_results_dir[0]):
            if os.path.exists(filename):
                print(f"Overwriting '{_results_dir[0]}/{filename}' !")
            image.save(
                file,
                save_all=True,
                append_images=images,
                duration=self.time,
                loop=0,
            )

    def recorder(self, file_fmt: str):
        def record(press: bool):
            if press:
                self.startRecording()
            else:
                self.stopRecording(file_fmt.format(datetime.now()))
        return record
