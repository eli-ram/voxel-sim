

"""
    E = edges
    N = nodes
    D = distances = N[E[:, 0], :] - N[E[:, 1], :]
    L = lengths = np.linalg.norm(D, axis=0)
    C = cosine = D / L
    Q = np.outer(C, C).reshape(len(E), -1)

    I = np.arange(len(N))
    S_N_0 = I[:, np.newaxis] == E[np.newaxis, :, 0]
    S_N_1 = I[:, np.newaxis] == E[np.newaxis, :, 1]
    S_N_I = node stiffness indices = S_N_0 | S_N_1
    S_N = node stiffness = np.sum(Q, where=S_N_I)
"""