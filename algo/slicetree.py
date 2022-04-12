import open3d as o3d
import numpy as np
import sys
import copy
from open3d.visualization import gui

tree = o3d.io.read_point_cloud(sys.argv[1])
print(f"Loaded point cloud: {tree}")

SLICE_COLOR = (0, 0, 1)

class SliceSelectorWindow:

    def __init__(self, tree):
        self.tree = tree
        self.point_arr = np.asarray(self.tree.points)
        self.SLICE_START = np.min(self.point_arr[:, 2])
        self.SLICE_STOP = np.max(self.point_arr[:, 2])
        self.SLICE_COUNT = 500
        self.SLICE_STEP = (self.SLICE_STOP - self.SLICE_START) / self.SLICE_COUNT
        self.slice_z = 0
        self.slice_updated = False

        self.window = gui.Application.instance.create_window("Slice controls", 400, 100)
        em = self.window.theme.font_size
        layout = gui.Vert(0.3 * em, gui.Margins(0.5 * em, 0.5 * em, 0.5 * em, 0.5 * em))

        layout.add_child(gui.Label("Slice height:"))
        slider = gui.Slider(gui.Slider.DOUBLE)
        slider.set_on_value_changed(self.on_slider)
        slider.set_limits(self.SLICE_START, self.SLICE_STOP)
        slider.double_value = self.slice_z
        layout.add_child(slider)

        horiz = gui.Horiz()
        horiz.add_child(gui.Label("Diameter:"))
        numedit = gui.NumberEdit(gui.NumberEdit.DOUBLE)
        horiz.add_child(numedit)
        layout.add_child(horiz)

        self.window.add_child(layout)

    def make_slice(self):
        return tree.select_by_index(np.where(abs(self.slice_z - self.point_arr[:, 2]) < self.SLICE_STEP / 2)[0])
    
    def flatten_slice(self, slice):
        return slice.translate((0, 0, -slice.get_center()[2]))
    
    def on_slider(self, val):
        self.slice_updated = True
        self.slice_z = val
        print("Slice at", val)

gui.Application.instance.initialize()
window = SliceSelectorWindow(tree)

cloud = window.make_slice()
cloud.paint_uniform_color(SLICE_COLOR)
vis = o3d.visualization.Visualizer()
vis.create_window("Tree")
vis.add_geometry(cloud)
vis.add_geometry(tree.uniform_down_sample(10))
vis.get_render_option().point_size = 2.0
vis.reset_view_point(True)

slice_vis = o3d.visualization.Visualizer()
slice_vis.create_window("2D Slice")
flat_cloud = window.flatten_slice(window.make_slice())
flat_cloud.paint_uniform_color(SLICE_COLOR)
slice_vis.add_geometry(flat_cloud)
slice_vis.get_render_option().point_size = 4.0
slice_vis.reset_view_point(True)

while True:
    if not gui.Application.instance.run_one_tick():
        break
    if window.slice_updated:
        window.slice_updated = False
        cloud.points = window.make_slice().points
        cloud.paint_uniform_color(SLICE_COLOR)
        vis.update_geometry(cloud)
        # Create another slice because translate() modifies the original
        flat_cloud.points = window.flatten_slice(window.make_slice()).points
        flat_cloud.paint_uniform_color(SLICE_COLOR)
        slice_vis.update_geometry(flat_cloud)
        slice_vis.reset_view_point(True)
    vis.poll_events()
    vis.update_renderer()
    slice_vis.poll_events()
    slice_vis.update_renderer()
