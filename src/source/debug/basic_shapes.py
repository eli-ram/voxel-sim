import numpy as np
from OpenGL import GL

S = np.array([  # type: ignore
    [0, -1, +1, 1.0, 0.0, 0.0],
    [0, +1, +1, 1.0, 0.0, 0.0],
    [0, +1, -1, 1.0, 0.0, 0.0],
    [0, -1, -1, 0.0, 1.0, 0.0],
], dtype=np.float32)


def square():
    GL.glBegin(GL.GL_QUADS)
    for v in S:
        pos, color = v[:3], v[3:]  # type: ignore
        GL.glColor3fv(color)
        GL.glVertex3fv(pos)
    GL.glEnd()
