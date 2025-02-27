import rerun as rr  # NOTE: `rerun`, not `rerun-sdk`!
import numpy as np
import time
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--folder", type=str, help="Folder name")
args = parser.parse_args()

folder = args.folder
print(folder)

videos = os.listdir(folder)

rr.init("rerun_asset_video_auto_frames")
rr.serve_web(ws_port=4321, web_port=10000)

for idx,video in enumerate(videos):
    video_asset = rr.AssetVideo(path=folder + "/" + video)
    rr.log("video" + str(idx), video_asset, static=True)
    frame_timestamps_ns = video_asset.read_frame_timestamps_ns()
    print(video_asset.read_frame_timestamps_ns())
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
