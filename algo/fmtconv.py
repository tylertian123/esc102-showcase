from pyntcloud import PyntCloud
import sys

src = sys.argv[1]
dest = sys.argv[2]

print("Loading", src)
cloud = PyntCloud.from_file(src)
#cloud.plot(backend="threejs")
print("Saving to", dest)
cloud.to_file(dest)
print("Done")
