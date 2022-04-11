from pyntcloud import PyntCloud
import sys

PyntCloud.from_file(sys.argv[1]).plot()
