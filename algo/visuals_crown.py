from matplotlib import pyplot as plt, patches
import matplotlib
import numpy as np
import scipy
from skimage.measure import fit, ransac
import math

matplotlib.use("TkAgg")


with open("real_crown.pts", 'rb') as f:
    points = np.load(f)

plt.gca().set_aspect('equal')
plt.scatter(points[:, 0], points[:, 1], c='b', s=0.5)

hull = points[scipy.spatial.ConvexHull(points).vertices]
plt.plot(hull[:, 0], hull[:, 1], c='r')
plt.plot([hull[0][0], hull[-1][0]], [hull[0][1], hull[-1][1]], c='r')

def plot_fit(points: np.ndarray, outlier_color: str, ellipse_color: str):
    ellipse, inliers = ransac(points, fit.EllipseModel, min(max(3, len(points) // 3), 20), 0.1, max_trials=50)
    plt.gca().add_patch(patches.Ellipse((ellipse.params[0], ellipse.params[1]), 2 * ellipse.params[2], 2 * ellipse.params[3], math.degrees(ellipse.params[4]), fill=False, color=ellipse_color))
    out_pts = points[np.where(inliers == False)]
    if outlier_color is not None:
        plt.scatter(out_pts[:, 0], out_pts[:, 1], c=outlier_color)

    (x0, y0), (x1, y1) = ellipse.predict_xy(np.array([0, np.pi]))
    plt.plot([x0, x1], [y0, y1], linestyle='--', c=ellipse_color)
    (x0, y0), (x1, y1) = ellipse.predict_xy(np.array([np.pi / 2, np.pi * 3 / 2]))
    plt.plot([x0, x1], [y0, y1], linestyle='--', c=ellipse_color)

plot_fit(hull, outlier_color=None, ellipse_color="limegreen")

plt.legend(handles=[patches.Patch(color="blue", label="Points"), patches.Patch(color="red", label="Convex Hull"),
    patches.Patch(color="limegreen", label="Ellipse Fit")])
man = plt.get_current_fig_manager()
man.resize(*man.window.maxsize())
plt.pause(5)

plt.gcf().savefig("crown1.png", format="png", dpi=600, transparent=True)
plt.show()
