from OpenGL.GL import (
    glGetIntegerv,
)
from OpenGL.GL.NVX.gpu_memory_info import (
    GL_GPU_MEMORY_INFO_TOTAL_AVAILABLE_MEMORY_NVX as TOTAL,
    GL_GPU_MEMORY_INFO_CURRENT_AVAILABLE_VIDMEM_NVX as CURRENT,
)
from enum import Enum


"""
TODO:
    1. Find GPU in runtime
    2. Allow getting Memory usage for other GPU's
    3. Set up frametime average

"""

class GPU(Enum):
    NVIDIA = 0
    AMD = 1
    UNKNOWN = 2

def kb2mb(v: int) -> int:
    return v // 1024


def memory_nvidia():
    total: int = glGetIntegerv(TOTAL)
    current: int = glGetIntegerv(CURRENT)
    return kb2mb(total), kb2mb(current)


def memory(gpu: GPU):
    """ Returns vram usage in MB (total, current)"""
    if gpu is GPU.NVIDIA:
        return memory_nvidia()
    return -1, -1



def performance(gpu: GPU):
    total, current = memory(gpu)

    print(f"V-Ram-Usage: {current} MB / {total} MB")
