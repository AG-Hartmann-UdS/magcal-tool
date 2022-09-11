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
