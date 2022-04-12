import numpy as np
import open3d as o3d
import time

print("Loaded libraries")

cloud = o3d.io.read_point_cloud("corners.xyz")
vis = o3d.visualization.Visualizer()
print(cloud)
vis.create_window()
vis.add_geometry(cloud)

num_points = 1000
points_per_update = 10

start = time.time()
for i in range(num_points // points_per_update):
    for point in np.random.rand(points_per_update, 3):
        cloud.points.append(point)
    vis.update_geometry(cloud)
    vis.poll_events()
    vis.update_renderer()
end = time.time()
print(cloud)
print(f"Adding {num_points} points took {end - start:.3f}s ({(end - start) / num_points * 1000:.1f}ms per point)")

while True:
    vis.poll_events()
    vis.update_renderer()

vis.destroy_window()
