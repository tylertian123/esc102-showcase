from matplotlib import pyplot as plt
import numpy as np
from typing import Tuple
import scipy.spatial
import sys

def compute_diameters(points: np.ndarray) -> Tuple[float, float]:
    if len(points) < 3:
        return (np.nan, np.nan)
    plt.scatter(points[:, 0], points[:, 1])
    plt.gca().set_aspect('equal')
    hull = points[scipy.spatial.ConvexHull(points).vertices]
    plt.plot(hull[:, 0], hull[:, 1], c='y')
    distances = scipy.spatial.distance_matrix(hull, hull)
    # Get the indices of the two points with maximum distance
    i, j = np.unravel_index(np.argmax(distances), distances.shape)
    plt.plot([hull[i][0], hull[j][0]], [hull[i][1], hull[j][1]], c='r')
    # Compute the distance along the axis perpendicular to the diameter axis
    # Find the vector to project onto, normalized and perpendicular to the difference between the diameter points
    s = hull[i] - hull[j]
    s /= np.sqrt(np.dot(s, s))
    s[0], s[1] = -s[1], s[0]
    plt.arrow(hull[i][0], hull[i][1], s[0] * 0.2, s[1] * 0.2)
    # Find the length of each projection by taking the dot product
    proj_lens = np.dot(hull - hull[i], s)
    idx = np.argmax(np.abs(proj_lens))
    proj_len = np.dot(hull[idx] - hull[i], s)
    plt.arrow(hull[i][0], hull[i][1], s[0] * proj_len, s[1] * proj_len, color='limegreen')
    plt.arrow(hull[i][0], hull[i][1], *(hull[idx] - hull[i]), color='limegreen')
    plt.plot([hull[i][0] + s[0] * proj_len, hull[idx][0]], [hull[i][1] + s[1] * proj_len, hull[idx][1]], color='limegreen', linestyle=':')
    plt.show()
    # Instead of taking the most positive projected length and subtracting the most negative, we take the projected
    # length furthest from zero and double it. This is because in the scanned point cloud, the stem might appear as
    # only half of an ellipse since the back is blocked
    return distances[i, j], np.max(np.abs(proj_lens)) * 2

with open(sys.argv[1], 'rb') as f:
    points = np.load(f)
compute_diameters(points)
