from typing import Tuple
import math
import open3d as o3d
import numpy as np
import sys
import scipy
import itertools
from open3d.visualization import gui
from skimage import measure

SLICE_COLOR = (0, 0, 1)
TREE_COLOR = (0, 0, 0)
COLORS = np.array([
    [0, 0, 1],
    [0, 1, 0],
    [1, 0, 0],
    [1, 1, 0],
    [1, 0, 1],
    [0, 1, 1],
])


def get_color(label: int):
    return np.array([0, 0, 0]) if label == -1 else COLORS[label % len(COLORS)]

def compute_diameters_ellipse(points: np.ndarray, use_ransac: bool = True) -> Tuple[float, float]:
    if len(points) < 3:
        return (np.nan, np.nan)
    # Use RANSAC to fit an ellipse to the points
    if use_ransac:
        ellipse, _ = measure.ransac(points, measure.fit.EllipseModel, min(max(3, len(points) // 3), 20), 0.01, max_trials=30)
        if ellipse is None:
            return compute_diameters_ellipse(points, use_ransac=False)
    else:
        ellipse = measure.fit.EllipseModel()
        if not ellipse.estimate(points):
            return np.nan, np.nan
    a = ellipse.params[2] * 2
    b = ellipse.params[3] * 2
    return max(a, b), min(a, b)

def compute_diameters_simple(points: np.ndarray) -> Tuple[float, float]:
    if len(points) < 3:
        return np.nan, np.nan
    try:
        hull = points[scipy.spatial.ConvexHull(points).vertices]
    except scipy.spatial.qhull.QhullError:
        return np.nan, np.nan
    dist = scipy.spatial.distance_matrix(hull, hull)
    i, j = np.unravel_index(np.argmax(dist), dist.shape)
        # Compute the distance along the axis perpendicular to the diameter axis
    # Find the vector to project onto, normalized and perpendicular to the difference between the diameter points
    s = hull[i] - hull[j]
    s /= np.sqrt(np.dot(s, s))
    s[0], s[1] = -s[1], s[0]
    # Find the length of each projection by taking the dot product
    proj_lens = np.dot(hull - hull[i], s)
    # Instead of taking the most positive projected length and subtracting the most negative, we take the projected
    # length furthest from zero and double it. This is because in the scanned point cloud, the stem might appear as
    # only half of an ellipse since the back is blocked
    return dist[i, j], np.max(np.abs(proj_lens)) * 2


class Demo:

    def __init__(self, filename: str) -> None:
        self.tree = o3d.io.read_point_cloud(filename)
        print("Loaded", self.tree)

        self.point_arr = np.asarray(self.tree.points)
        self.SLICE_START = np.min(self.point_arr[:, 2])
        self.SLICE_STOP = np.max(self.point_arr[:, 2])
        self.slice_step = 0.1
        self.slice_z = self.SLICE_START
        self.slice_updated = True

        self.window = None
        self.slice_z_slider = None
        self.slice_z_edit = None
        self.diam_edits = []
        self.stems_edit = None
        self.crown_width_edits = []
        self.cluster_eps = 0.15
        self.cluster_min_points = 5
        self.use_ransac = False
        self.use_ellipse_fit = True
        self.init_window()
        self.recompute_crown_width()

        self.tree_vis = None
        self.slice_vis = None
        self.slice_cloud = None
        self.flat_slice_cloud = None
        self.init_visualizers()

    def init_window(self) -> None:
        self.window = gui.Application.instance.create_window(
            "Output", 500, 500)
        em = self.window.theme.font_size
        layout = gui.Vert(0.33 * em, gui.Margins(0.5 * em,
                                                 0.5 * em, 0.5 * em, 0.5 * em))

        layout.add_child(gui.Label("Slice height (m):"))
        horiz = gui.Horiz(0.33 * em)
        self.slice_z_slider = gui.Slider(gui.Slider.DOUBLE)
        self.slice_z_slider.set_on_value_changed(self._on_slider)
        self.slice_z_slider.set_limits(self.SLICE_START, self.SLICE_STOP)
        self.slice_z_slider.double_value = self.slice_z
        horiz.add_child(self.slice_z_slider)
        self.slice_z_edit = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        self.slice_z_edit.double_value = self.slice_z
        self.slice_z_edit.set_on_value_changed(self._on_slider)
        horiz.add_child(self.slice_z_edit)
        layout.add_child(horiz)

        horiz = gui.Horiz()
        horiz.add_child(gui.Label("Height (m):"))
        nedit = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        nedit.double_value = self.SLICE_STOP
        horiz.add_child(nedit)
        layout.add_child(horiz)

        
        collapse = gui.CollapsableVert("Crown width", 0.33 * em, gui.Margins(em, 0, 0, 0))
        horiz = gui.Horiz()
        horiz.add_child(gui.Label("Long Axis (m):"))
        nedit = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        self.crown_width_edits.append(nedit)
        horiz.add_child(nedit)
        collapse.add_child(horiz)
        horiz = gui.Horiz()
        horiz.add_child(gui.Label("Short Axis (m):"))
        nedit = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        self.crown_width_edits.append(nedit)
        horiz.add_child(nedit)
        collapse.add_child(horiz)
        horiz = gui.Horiz()
        horiz.add_child(gui.Label("Average (m):"))
        nedit = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        self.crown_width_edits.append(nedit)
        horiz.add_child(nedit)
        collapse.add_child(horiz)
        layout.add_child(collapse)

        horiz = gui.Horiz()
        horiz.add_child(gui.Label("Number of Stems:"))
        self.stems_edit = gui.NumberEdit(gui.NumberEdit.INT)
        horiz.add_child(self.stems_edit)
        layout.add_child(horiz)

        horiz = gui.Horiz(0.33 * em)
        horiz.add_child(gui.Label("Diameters (m):"))
        self.diam_edits.append(gui.NumberEdit(gui.NumberEdit.DOUBLE))
        self.diam_edits.append(gui.NumberEdit(gui.NumberEdit.DOUBLE))
        self.diam_edits.append(gui.NumberEdit(gui.NumberEdit.DOUBLE))
        horiz.add_child(self.diam_edits[0])
        horiz.add_child(self.diam_edits[1])
        horiz.add_child(self.diam_edits[2])
        layout.add_child(horiz)

        collapse = gui.CollapsableVert("Tunables", 0.33 * em, gui.Margins(em, 0, 0, 0))

        horiz = gui.Horiz()
        horiz.add_child(gui.Label("Slice thickness:"))
        nedit = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        nedit.double_value = self.slice_step
        nedit.set_on_value_changed(self._on_slice_step_edit)
        horiz.add_child(nedit)
        collapse.add_child(horiz)

        horiz = gui.Horiz()
        horiz.add_child(gui.Label("Clustering eps:"))
        nedit = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        nedit.double_value = self.cluster_eps
        nedit.set_on_value_changed(self._on_cluster_eps_slider)
        horiz.add_child(nedit)
        collapse.add_child(horiz)

        horiz = gui.Horiz()
        horiz.add_child(gui.Label("Clustering #points:"))
        nedit = gui.NumberEdit(gui.NumberEdit.INT)
        nedit.int_value = self.cluster_min_points
        nedit.set_on_value_changed(self._on_cluster_points_slider)
        horiz.add_child(nedit)
        collapse.add_child(horiz)

        cb = gui.Checkbox("Use RANSAC?")
        cb.set_on_checked(self._on_ransac_cb)
        cb.checked = self.use_ransac
        collapse.add_child(cb)

        cb = gui.Checkbox("Use ellipse fit?")
        cb.set_on_checked(self._on_ellipse_cb)
        cb.checked = self.use_ellipse_fit
        collapse.add_child(cb)

        layout.add_child(collapse)

        self.window.add_child(layout)
    
    def recompute_crown_width(self):
        # Use convex hull to eliminate all the points not on the perimeter after squashing
        pts = self.point_arr[:, :2]
        hull = pts[scipy.spatial.ConvexHull(pts).vertices]
        if self.use_ellipse_fit:
            long_diam, perp_diam = compute_diameters_ellipse(hull, use_ransac=self.use_ransac)
        else:
            long_diam, perp_diam = compute_diameters_simple(hull)
        self.crown_width_edits[0].double_value = long_diam
        self.crown_width_edits[1].double_value = perp_diam
        self.crown_width_edits[2].double_value = (long_diam + perp_diam) / 2

    def _on_slider(self, val: float):
        self.slice_updated = True
        self.slice_z = val
        if self.slice_z_slider.double_value != val:
            self.slice_z_slider.double_value = val
        if self.slice_z_edit.double_value != val:
            self.slice_z_edit.double_value = val
        print("Slice at", val)

    def _on_cluster_eps_slider(self, val: float):
        self.slice_updated = True
        self.cluster_eps = val

    def _on_cluster_points_slider(self, val: int):
        self.slice_updated = True
        self.cluster_min_points = int(val)
    
    def _on_slice_step_edit(self, val: float):
        self.slice_updated = True
        self.slice_step = val
    
    def _on_ransac_cb(self, checked: bool):
        self.slice_updated = True
        self.use_ransac = checked
        self.recompute_crown_width()
    
    def _on_ellipse_cb(self, checked: bool):
        self.slice_updated = True
        self.use_ellipse_fit = checked
        self.recompute_crown_width()

    def init_visualizers(self) -> None:
        self.tree_vis = o3d.visualization.Visualizer()
        self.slice_vis = o3d.visualization.Visualizer()
        self.tree_vis.create_window("Tree")
        self.slice_vis.create_window("2D Slice")
        self.tree_vis.get_render_option().point_size = 2.0
        self.slice_vis.get_render_option().point_size = 4.0

        self.slice_cloud = self.make_slice()
        self.slice_cloud.paint_uniform_color(SLICE_COLOR)
        self.flat_slice_cloud = self.make_flat_slice()
        self.flat_slice_cloud.paint_uniform_color(SLICE_COLOR)
        self.tree.paint_uniform_color(TREE_COLOR)
        self.tree_vis.add_geometry(self.tree.uniform_down_sample(10))
        self.tree_vis.add_geometry(self.slice_cloud)
        self.slice_vis.add_geometry(self.flat_slice_cloud)

        self.tree_vis.reset_view_point(True)
        self.slice_vis.reset_view_point(True)

    def make_slice(self):
        cloud_slice = self.tree.select_by_index(
            np.where(abs(self.slice_z - self.point_arr[:, 2]) < self.slice_step / 2)[0])
        return cloud_slice

    def make_flat_slice(self):
        cloud_slice = self.make_slice()
        return cloud_slice.translate((0, 0, -cloud_slice.get_center()[2]))

    def update_characteristics(self, cloud: o3d.geometry.PointCloud):
        # Use clustering to find different stems
        labels = np.array(cloud.cluster_dbscan(eps=self.cluster_eps, min_points=self.cluster_min_points))
        cluster_count = np.max(labels) + 1
        self.stems_edit.int_value = cluster_count
        # Colour each stem differently
        colors = np.empty((len(labels), 3))
        for i, label in enumerate(labels):
            colors[i] = get_color(label)
        cloud.colors = o3d.utility.Vector3dVector(colors)
        # To find the stem diameter, we need the distance between the furthest 2 points
        # These 2 points will always be a part of the convex hull
        # Use numpy to find stem diameter, since the slice is 2D
        cloud_points = np.asarray(cloud.points)
        diameters = []
        for cluster_index in range(cluster_count):
            # Extract the points in the current cluster and slice to make it 2D
            points = cloud_points[np.where(labels == cluster_index)][:, :2]
            if self.use_ellipse_fit:
                diam, _ = compute_diameters_ellipse(points, use_ransac=self.use_ransac)
            else:
                diam, _ = compute_diameters_simple(points)
            if not math.isnan(diam):
                diameters.append(diam)
        # Set the diameters in sorted order
        for diam_edit, long_diam in zip(self.diam_edits, itertools.chain(sorted(diameters, reverse=True), itertools.repeat(np.nan))):
            diam_edit.double_value = long_diam

    def run(self):
        while True:
            if self.slice_updated:
                self.slice_updated = False
                self.slice_cloud.points = self.make_slice().points
                self.slice_cloud.paint_uniform_color(SLICE_COLOR)
                self.flat_slice_cloud.points = self.make_flat_slice().points
                self.flat_slice_cloud.paint_uniform_color(SLICE_COLOR)

                self.update_characteristics(self.flat_slice_cloud)

                self.tree_vis.update_geometry(self.slice_cloud)
                self.slice_vis.update_geometry(self.flat_slice_cloud)
                self.slice_vis.reset_view_point(True)
            if not gui.Application.instance.run_one_tick():
                break
            self.tree_vis.poll_events()
            self.tree_vis.update_renderer()
            self.slice_vis.poll_events()
            self.slice_vis.update_renderer()


if __name__ == "__main__":
    gui.Application.instance.initialize()
    window = Demo(sys.argv[1])
    window.run()
