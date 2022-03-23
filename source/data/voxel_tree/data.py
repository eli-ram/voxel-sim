
from .operation import Operation
import numpy as np



class Data:
    op: Operation
    mask: np.ndarray[np.bool_]
