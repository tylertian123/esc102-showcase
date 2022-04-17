from matplotlib import pyplot as plt, patches
import matplotlib
import numpy as np
from skimage.measure import fit, ransac
import math
import sys

matplotlib.use("TkAgg")


stems = [np.load(open(name, "rb")) for name in sys.argv[1:]]

plt.gca().set_aspect('equal')

for stem in stems:
    plt.scatter(stem[:, 0], stem[:, 1])

def plot_fit(points: np.ndarray, outlier_color: str, ellipse_color: str):
    ellipse, inliers = ransac(points, fit.EllipseModel, min(max(3, len(points) // 3), 20), 0.02, max_trials=50)
    plt.gca().add_patch(patches.Ellipse((ellipse.params[0], ellipse.params[1]), 2 * ellipse.params[2], 2 * ellipse.params[3], math.degrees(ellipse.params[4]), fill=False, color=ellipse_color))
    out_pts = points[np.where(inliers == False)]
    plt.scatter(out_pts[:, 0], out_pts[:, 1], c=outlier_color)

    (x0, y0), (x1, y1) = ellipse.predict_xy(np.array([0, np.pi]))
    plt.plot([x0, x1], [y0, y1], linestyle='--', c=ellipse_color)
    (x0, y0), (x1, y1) = ellipse.predict_xy(np.array([np.pi / 2, np.pi * 3 / 2]))
    plt.plot([x0, x1], [y0, y1], linestyle='--', c=ellipse_color)

for stem in stems:
    plot_fit(stem, outlier_color="orange", ellipse_color="limegreen")

#plt.legend(handles=[patches.Patch(color="blue", label="Stem 1"), patches.Patch(color="red", label="Stem 2")])
man = plt.get_current_fig_manager()
man.resize(*man.window.maxsize())
#plt.pause(5)

#plt.gcf().savefig("algo3.png", format="png", dpi=300, transparent=True)
plt.show()
