import open3d as o3d
import sys

cloud = o3d.io.read_point_cloud(sys.argv[1])
print(cloud)
cloud, _ = cloud.remove_statistical_outlier(20, 2.0, True)
print(cloud)
#cloud.paint_uniform_color([0.75, 0.75, 0.75])
vis = o3d.visualization.VisualizerWithEditing()
vis.create_window()
vis.add_geometry(cloud)
vis.get_render_option().point_size = 1.0
vis.run()
