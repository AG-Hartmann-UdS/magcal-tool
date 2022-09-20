import numpy as np


def convert_to_array(raw_line, delimiter=","):
    dt = raw_line.split(delimiter)
    try:
        data_line = map(float, dt)
        return np.array(list(data_line))
    except ValueError:
        return None


def matrix_string(mat):
    mat_str = np.array2string(mat, precision=4, separator="  ", prefix="", suffix="",
                              formatter={'float_kind': lambda x: "%.4f" % x})
    mat_str = mat_str.replace("[", "")
    mat_str = mat_str.replace("]", "")
    mat_str = " " + mat_str
    return mat_str

def generate_ellispoid(A, c, r):

    delta_theta = np.pi / 100
    delta_phi = np.pi / 100

    theta = np.arange(0, np.pi + delta_theta, delta_theta)
    phi = np.arange(0, 2 * np.pi + delta_phi, delta_phi)

    theta, phi = np.meshgrid(theta, phi)
    x = r * np.cos(phi) * np.sin(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(theta)

    # Convert to ellipsoid and replot
    sphere_data = np.concatenate([np.expand_dims(x, 2), np.expand_dims(y, 2), np.expand_dims(z, 2)], axis=-1)
    ellipsoid_data = np.tensordot(sphere_data, np.linalg.inv(A), axes=((2), (0))) + c
    xprime, yprime, zprime = np.split(ellipsoid_data, axis=-1, indices_or_sections=3)
    # Return all the parameters
    return x, y, z, xprime[:, :, 0], yprime[:, :, 0], zprime[:, :, 0]