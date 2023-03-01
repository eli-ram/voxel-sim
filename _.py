import numpy as np

R = np.random.default_rng()
M = lambda : R.random() # type: ignore
A = M()
B = M()