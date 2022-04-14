from matplotlib import pyplot as plt, patches
import matplotlib
import numpy as np
from skimage.measure import fit, ransac
import math

matplotlib.use("TkAgg")


with open("points0.pts", 'rb') as f0, open("points1.pts", 'rb') as f1:
    points0 = np.load(f0)
    points1 = np.load(f1)

plt.gca().set_aspect('equal')
plt.scatter(points0[:, 0], points0[:, 1], c='b')
plt.scatter(points1[:, 0], points1[:, 1], c='r')

def plot_fit(points: np.ndarray, outlier_color: str, ellipse_color: str):
    ellipse, inliers = ransac(points, fit.EllipseModel, min(max(3, len(points) // 3), 20), 0.02, max_trials=50)
    plt.gca().add_patch(patches.Ellipse((ellipse.params[0], ellipse.params[1]), 2 * ellipse.params[2], 2 * ellipse.params[3], math.degrees(ellipse.params[4]), fill=False, color=ellipse_color))
    out_pts = points[np.where(inliers == False)]
    plt.scatter(out_pts[:, 0], out_pts[:, 1], c=outlier_color)

    (x0, y0), (x1, y1) = ellipse.predict_xy(np.array([0, np.pi]))
    plt.plot([x0, x1], [y0, y1], linestyle='--', c=ellipse_color)
    (x0, y0), (x1, y1) = ellipse.predict_xy(np.array([np.pi / 2, np.pi * 3 / 2]))
    plt.plot([x0, x1], [y0, y1], linestyle='--', c=ellipse_color)

plot_fit(points0, outlier_color="orange", ellipse_color="limegreen")
plot_fit(points1, outlier_color="orange", ellipse_color="limegreen")

plt.legend(handles=[patches.Patch(color="blue", label="Stem 1"), patches.Patch(color="red", label="Stem 2"),
    patches.Patch(color="orange", label="Outliers"), patches.Patch(color="limegreen", label="Ellipse Fit")])
man = plt.get_current_fig_manager()
man.resize(*man.window.maxsize())
plt.pause(5)

plt.gcf().savefig("algo.png", format="png", dpi=600, transparent=True)
plt.show()
