import open3d as o3d
import numpy as np
import sys

print("Loading point cloud")
tree = o3d.io.read_point_cloud(sys.argv[1])
print(f"Loaded point cloud: {tree}")

# Preprocessing
tree = tree.voxel_down_sample(0.05)
tree.paint_uniform_color([0.75, 0.75, 0.75])
print(f"Downsampled to {tree}")
# Cut out only one tree
tree = tree.select_by_index(np.where(np.asarray(tree.points)[:, 1] > -1)[0])
print(f"Trimmed to {tree}")
tree.remove_radius_outlier(10, 0.1)
print(f"After outlier removal: {tree}")
# Center the tree
tree.translate((2.1, -4.9, 0))
# Rotate
tree.rotate(tree.get_rotation_matrix_from_xyz((0, 0, np.pi)))

camera = o3d.geometry.TriangleMesh.create_box(0.2, 0.2, 0.2)
camera.translate((-0.1, -0.1, -0.1))
camera.translate((-15, 0, 1.30))
camera.paint_uniform_color([0, 0.5, 0])

# Shift the origin
offset = camera.get_center()
camera.translate(-offset)
tree.translate(-offset)

if len(sys.argv) > 2:
    o3d.io.write_point_cloud(sys.argv[2], tree)

vis = o3d.visualization.Visualizer()
vis.create_window()
vis.add_geometry(tree)
vis.add_geometry(camera)
vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame())
vis.get_render_option().point_size = 1.5
while True:
    vis.poll_events()
    vis.update_renderer()
