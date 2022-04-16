import open3d as o3d
import sys

cloud = o3d.io.read_point_cloud(sys.argv[1])
print(cloud)
cloud, _ = cloud.remove_statistical_outlier(20, 2.0, True)
print(cloud)

#o3d.visualization.draw(cloud)

vis = o3d.visualization.VisualizerWithEditing()
vis.create_window()
vis.get_render_option().point_size = 2.0
vis.add_geometry(cloud)
vis.run()
