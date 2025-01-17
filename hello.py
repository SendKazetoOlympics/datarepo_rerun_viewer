import rerun as rr  # NOTE: `rerun`, not `rerun-sdk`!
import numpy as np
import time

rr.init("rerun_example_my_data")
rr.serve_web(ws_port=4321, web_port=10000)

positions = np.zeros((10, 3))
positions[:,0] = np.linspace(-10,10,10)

colors = np.zeros((10,3), dtype=np.uint8)
colors[:,0] = np.linspace(0,255,10)

rr.log(
    "my_points",
    rr.Points3D(positions, colors=colors, radii=0.5)
)

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  print("Ctrl-C received. Exiting.")
