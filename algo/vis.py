import open3d as o3d
import sys
import numpy as np

cloud = o3d.io.read_point_cloud(sys.argv[1])
print(cloud)

cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=10))

#o3d.visualization.draw_geometries([cloud], point_show_normal=True)

points = np.asarray(cloud.points)
normals = np.asarray(cloud.normals)
filtered = points[np.where(np.abs([np.dot(a, b) / np.linalg.norm(a) for a, b in zip(points, normals)]) > np.cos(np.deg2rad(75)))]

c = o3d.geometry.PointCloud()
c.points = o3d.utility.Vector3dVector(filtered)
print(c)
c, _ = c.remove_statistical_outlier(20, 1.5, True)
print(c)

#o3d.visualization.draw(cloud)

vis = o3d.visualization.VisualizerWithEditing()
vis.create_window()
vis.get_render_option().point_size = 2.0
vis.add_geometry(c)
vis.run()
