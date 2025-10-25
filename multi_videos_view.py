import rerun as rr  # NOTE: `rerun`, not `rerun-sdk`!
import numpy as np
import time
import argparse
import os
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument("--folder", type=str, help="Folder name")
args = parser.parse_args()

file_list = os.listdir(args.folder)
ips = [f.split('_')[0] for f in file_list if f.lower().endswith('.mp4')]
timestamps = {}
for ip in ips:
    timestamps[ip] = np.loadtxt(os.path.join(args.folder, ip + "_timestamps.csv"))
#    timestamps[ip] -= timestamps[ip][0]  # Normalize to start from zero
    
print(timestamps)
    
min_time = min([np.min(timestamps[ip]) for ip in ips])

# plt.figure(figsize=(10, 6))
# for ip in ips:
#     plt.plot(timestamps[ip][:-1] - min_time , np.diff(timestamps[ip]) , label=ip)
# # plt.ylim(0, 3e-2)
# plt.xlim(5, 6)
# plt.yscale('log')
# plt.savefig('test')

rr.init("rerun_asset_video_auto_frames")
rr.serve_web(web_port=10000)


for idx, ip in enumerate(ips):
    # Extract IP address from the video filename (assumes IP is before first '_')
    video_asset = rr.AssetVideo(path=os.path.join(args.folder, ip + "_video.mp4"))
    rr.log("video" + str(idx), video_asset, static=True)
    time_stamps = (timestamps[ip] - min_time)*1e9

    # frame_timestamps_ns = video_asset.read_frame_timestamps_nanos()
    rr.send_columns(
        "video" + str(idx),
        # Note timeline values don't have to be the same as the video timestamps.
        indexes=[rr.TimeColumn("video_time", duration=1e-9*time_stamps )],
        columns=rr.VideoFrameReference.columns_nanos(time_stamps),
    )

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  print("Ctrl-C received. Exiting.")
