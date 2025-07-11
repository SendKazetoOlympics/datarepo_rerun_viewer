import rerun as rr  # NOTE: `rerun`, not `rerun-sdk`!
import numpy as np
import time
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--folder", type=str, help="Folder name")
args = parser.parse_args()

file_list = os.listdir(args.folder)

videos = [f for f in file_list if f.lower().endswith('.mp4')]
time_csv = np.loadtxt(os.path.join(args.folder, "recordings.csv"), delimiter=',', skiprows=1, dtype=str)
starting_timestamps = {}
for row in time_csv:
    starting_timestamps[row[0]] = float(row[1])

rr.init("rerun_asset_video_auto_frames")
rr.serve_web(ws_port=4321, web_port=10000)


for idx, video in enumerate(videos):
    # Extract IP address from the video filename (assumes IP is before first '_')
    ip_addr = video.split('_')[0]
    video_asset = rr.AssetVideo(path=os.path.join(args.folder, video))
    rr.log("video" + str(idx), video_asset, static=True)
    # Use the IP address to get the starting timestamp
    start_ts = starting_timestamps.get(ip_addr, 0)
    frame_timestamps_ns = video_asset.read_frame_timestamps_ns() #+ start_ts
    rr.send_columns(
        "video" + str(idx),
        # Note timeline values don't have to be the same as the video timestamps.
        indexes=[rr.TimeNanosColumn("video_time", frame_timestamps_ns)],
        columns=rr.VideoFrameReference.columns_nanoseconds(frame_timestamps_ns),
    )

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  print("Ctrl-C received. Exiting.")
