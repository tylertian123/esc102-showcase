# Showcase Code - Tree Processing Algorithm

Files:

* `fmtconv.py <in_file> <out_file>`: Converts between two point cloud formats using PyntCloud. Useful because open3d can't read the .las file format.
* `vis.py <in_file>`: Runs the open3d visualizer with editing on an input point cloud. This can be used to cut out parts of the cloud.
* `pyntcloud_visualize.py <in_file>`: Runs the PyntCloud visualizer on an input point cloud.
* `extract.py <in_file> <out_file>`: Extracts and processes one of the trees from the point cloud.
* `demo.py <in_file>`: Main algorithm demo code, input file should be a processed point cloud.
* `lidar_demo.py`: Main lidar demo code for live point cloud display (hosts server on port 4206).
