# pyright: reportUnknownArgumentType=false, reportUnknownMemberType=false
import __init__
from typing import cast
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import *  # type: ignore
from OpenGL.arrays.vbo import *  # type: ignore
from source.interactive import Window
import numpy as np

vs = \
    """
#version 430

layout (location = 0) uniform vec2 aspect;

in vec2 pos;
out vec2 uv;

void main() {
    uv = 0.5 + pos * 0.5; // Bad magic dependency
	gl_Position = vec4(pos * aspect, 0.0, 1.0);
}
"""

fs = \
    """
#version 430

layout (binding = 0) uniform sampler2D srcTex;

in vec2 uv;
out vec4 color;

void main() {
    vec4 px = texture(srcTex, uv);
    float r = .3 + px.x * px.y;
    float b = .4 + px.x * px.z;
    float g = .01;
	color = vec4(r, g, b, 1.0);
}
"""

cs = \
    """
#version 430

layout (location = 0) uniform float roll;
layout (binding = 0) restrict writeonly uniform image2D dstTex;
layout (local_size_x = 16, local_size_y = 16) in;

void main() {
    ivec2 gp = ivec2(gl_GlobalInvocationID.xy);
    ivec2 lp = ivec2(gl_LocalInvocationID.xy);
    ivec2 id = ivec2(gl_WorkGroupID.xy);
    float lc = length(vec2(lp - 8) / 8.0);
    float xc = sin(float(id.x + id.y) * 0.4 + 0.5 * roll) * 0.5;
    float yc = sin(float(id.x - id.y) * 0.2 + 3.5 * roll) * 0.5;
    vec4 color = vec4(lc, xc, yc, 1.);
    imageStore(dstTex, gp, color);
}
"""

class GL_Window(Window):

    def setup(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.3, 1.0)
        self.texture = generateTexture()
        self.compute = compileProgram(
            compileShader(cs, GL_COMPUTE_SHADER),
        )
        self.shader = compileProgram(
            compileShader(vs, GL_VERTEX_SHADER),
            compileShader(fs, GL_FRAGMENT_SHADER),
        )
        self.square = np.array([
            [-1,-1],
            [+1,-1],
            [+1,+1],
            [-1,+1],
        ], np.float32)

        # conf compute shader
        with self.compute:
            glUniform1i(glGetUniformLocation(self.compute, "dstTex"), 0)
            self.roll_handle = glGetUniformLocation(self.compute, "roll")

        # conf render shader
        with self.shader:
            glUniform1i(glGetUniformLocation(self.shader, "srcTex"), 0)
            self.aspect_handle = glGetUniformLocation(self.shader, "aspect")

    def resize(self, width: int, height: int):
        glViewport(0, 0, width, height)
        aspect = [(height / width), 1.0] if width > height else [1.0, (width / height)]
        with self.shader:
            glUniform2f(self.aspect_handle, *aspect)


    def update(self, time: float, delta: float):
        with self.compute:
            glUniform1f(self.roll_handle, time)
            glDispatchCompute(512//16, 512//16, 1)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        glEnableClientState(GL_VERTEX_ARRAY)
        with self.shader:
            glVertexPointer(2, GL_FLOAT, 0, self.square)
            glDrawArrays(GL_QUADS, 0, 4)
            

def generateTexture():
    handle = cast(int, glGenTextures(1))
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, handle)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 512,
                 512, 0, GL_RGBA, GL_FLOAT, None)

    # Because we're also using this tex as an image (in order to write to it),
    # we bind it to an image unit as well
    glBindImageTexture(0, handle, 0, GL_FALSE,
                       0, GL_WRITE_ONLY, GL_RGBA32F)

    return handle


if __name__ == '__main__':
    window = GL_Window(800, 800, "OpenGL_Window")
    window.spin()
