import socketserver
import threading
import numpy as np
import open3d as o3d
import queue
import struct
import colorsys

print("Libraries loaded")

PORT = 4206

class LidarDemoHandler(socketserver.BaseRequestHandler):

    # This will be running in a different thread, so use the thread safe queue
    point_queue = None # type: queue.Queue
    MSG_SIZE = 24

    def handle(self):
        print(f"Connection established from {self.client_address}")
        self.buf = bytearray()
        while True:
            data = self.request.recv(1024)
            if not data:
                break
            # Combine the newly received data with previous data
            self.buf.extend(data)
            # Unpack the doubles and add them to the queue
            mem = memoryview(self.buf)
            i = 0
            while i < len(self.buf) - (self.MSG_SIZE - 1):
                x, y, z = struct.unpack("ddd", mem[i:i + self.MSG_SIZE])
                self.point_queue.put((x, y, z))
                print(f"Received point ({x}, {y}, {z})")
                i += 24
            del mem
            self.buf = self.buf[i:]
        print(f"Connection from {self.client_address} terminated")


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), LidarDemoHandler) as server:
        # Set up shared queue for points
        point_queue = queue.Queue()
        LidarDemoHandler.point_queue = point_queue

        server_thread = threading.Thread(target=server.serve_forever)
        server.daemon_threads = True
        server_thread.daemon = True
        server_thread.start()
        print(f"Started server on port {PORT} in thread {server_thread.name}")

        # Now set up open3d stuff
        cloud = o3d.geometry.PointCloud()
        vis = o3d.visualization.VisualizerWithKeyCallback()
        vis.create_window()
        vis.get_render_option().point_size = 2.0
        vis.add_geometry(cloud)
        vis.add_geometry(o3d.geometry.TriangleMesh.create_coordinate_frame())

        close = False
        def reset_view_callback(vis, action, mods):
            # Key up
            if action == 1:
                vis.reset_view_point(True)
                print("Reset view")
        def quit_callback(vis, action, mods):
            global close
            if action == 1:
                close = True
        def save_callback(vis, action, mods):
            if action == 1:
                o3d.io.write_point_cloud("network_cloud.ply", cloud)
                print("Saved point cloud")
        def reset_callback(vis, action, mods):
            if action == 1:
                cloud.points = o3d.utility.Vector3dVector()
                vis.update_geometry(cloud)
                print("Reset")
        vis.register_key_action_callback(ord(' '), reset_view_callback)
        vis.register_key_action_callback(ord('Q'), quit_callback)
        vis.register_key_action_callback(ord('S'), save_callback)
        vis.register_key_action_callback(ord('R'), reset_callback)

        while not close:
            updated = False
            try:
                while True:
                    updated = True
                    x, y, z = point_queue.get(block=False)
                    cloud.points.append(np.array((x, y, z)))
                    #cloud.colors.append(np.array(colorsys.hsv_to_rgb(strength / 10000 * 0.667, 1, 1)))
                    #cloud.paint_uniform_color([0.75, 0.75, 0.75])
                    print(f"Added point ({x}, {y}, {z})")
            except queue.Empty:
                pass
            if updated:
                vis.update_geometry(cloud)
            vis.poll_events()
            vis.update_renderer()
        vis.destroy_window()

        server.shutdown()
