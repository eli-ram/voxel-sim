from dataclasses import dataclass
import numpy as np


@dataclass
class Truss:
    # Node Attributes
    # list[(x, y, z)]
    nodes: 'np.ndarray[np.float32]'
    # list[(fx, fy, fz)]
    forces: 'np.ndarray[np.float64]'
    # list[(sx, sy, sz)]
    static: 'np.ndarray[np.bool_]' 

    # Edge Attributes
    # list[(a, b)]
    edges: 'np.ndarray[np.uint32]'
    # list[cross_section_area]
    areas: 'np.ndarray[np.float64]'