from typing import Tuple
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import patches
import sys
from skimage.measure import fit, ransac
import math
from scipy.spatial import ConvexHull

def compute_diameters(points: np.ndarray) -> Tuple[float, float]:
    if len(points) < 3:
        return (np.nan, np.nan)
    fig, ax = plt.subplots()
    #ax.scatter(points[:, 0], points[:, 1], s=1)
    points = points[ConvexHull(points).vertices]
    plt.plot(points[:, 0], points[:, 1], c='y')
    ellipse = fit.EllipseModel()
    rellipse, inliers = ransac(points, fit.EllipseModel, min(max(3, len(points) // 3), 20), 0.01, max_trials=50)
    print(inliers)
    if not ellipse.estimate(points):
        raise ValueError("Can't estimate!")
    ax.set_aspect('equal')
    print(ellipse.params)
    ax.add_patch(patches.Ellipse((ellipse.params[0], ellipse.params[1]), 2 * ellipse.params[2], 2 * ellipse.params[3], math.degrees(ellipse.params[4]), fill=False))
    ax.add_patch(patches.Ellipse((rellipse.params[0], rellipse.params[1]), 2 * rellipse.params[2], 2 * rellipse.params[3], math.degrees(rellipse.params[4]), fill=False, color='red'))
    plt.show()
    return ellipse.params[2], ellipse.params[3]


with open(sys.argv[1], 'rb') as f:
    points = np.load(f)
print(compute_diameters(points))
