# performs magnetometer calibration from a set of data
# using Merayo technique with a non iterative algoritm
# J.Merayo et al. "Scalar calibration of vector magnemoters"
# Meas. Sci. Technol. 11 (2000) 120-132.
# Same as the magnetic calibration function in Octave
# authored by Alain Barraud, Suzanne Lesecq 2008
# Ported into python by Ishwar Mudraje, 2022

import numpy as np


def compute_ellipsoid(X):

    if len(X.shape) == 2:
        N, _ = X.shape
        if N < 10:
            print("Too few values to perform fitting")
            return None
    else:
        print("Data is empty or missing")
        return None

    x = X[:, 0].reshape(-1, 1)
    y = X[:, 1].reshape(-1, 1)
    z = X[:, 2].reshape(-1, 1)

    # Form the design matrix Nx10
    D_list = [
        x ** 2, y ** 2, z ** 2,
        x * y, x * z, y * z,
        x, y, z,
        np.ones_like(x)]
    D = np.concatenate(D_list, axis=1)

    # Only upper triangular matrix (simplifying the Eigenvalue problem)
    Q, D_tri = np.linalg.qr(D)
    U, S, V = np.linalg.svd(D_tri)
    p = V[-1, :]

    # Reorient everything for standardization
    if p[0] < 0:
        p = -p

    # Construct the matrix A which will be Cholesky decomposed later (why??)
    A = np.array([
        [p[0], p[3] / 2, p[4] / 2],
        [p[3] / 2, p[1], p[5] / 2],
        [p[4] / 2, p[5] / 2, p[2]]])

    # Estimating the shape matrix for soft-iron distortions
    # upper triangular matrix
    try:
        U = np.linalg.cholesky(A).T
    except np.linalg.LinAlgError:
        print("Unable to perform Cholesky decomposition. Need more data or retake trial")
        return None

    # Not yet sure what this is about
    b = p[6:9]
    v = np.dot(b / 2, np.linalg.inv(U.T))
    d = p[-1]
    s = 1 / np.sqrt(np.sum(v ** 2) - d)
    c = -1 * np.dot(v, np.linalg.inv(U))
    U = s * U

    # return Shape U and
    return U, c
