import numpy as np
from OpenGL.GL import *  # type: ignore

S = np.array([  # type: ignore
    [0, -1, +1, 1.0, 0.0, 0.0],
    [0, +1, +1, 1.0, 0.0, 0.0],
    [0, +1, -1, 1.0, 0.0, 0.0],
    [0, -1, -1, 0.0, 1.0, 0.0],
], dtype=np.float32)


def square():
    glBegin(GL_QUADS)
    for v in S:
        pos, color = v[:3], v[3:]  # type: ignore
        glColor3fv(color)
        glVertex3fv(pos)
    glEnd()
