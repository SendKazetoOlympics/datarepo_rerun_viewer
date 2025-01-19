import rerun as rr  # NOTE: `rerun`, not `rerun-sdk`!
import numpy as np
import time
from minio import Minio
import psycopg
from psycopg.rows import TupleRow
from dotenv import load_dotenv
import os
import pickle
import io
import urllib.request

# Load the environment variables from the .env file
load_dotenv() 

def get_postgres_client() -> psycopg.connection:
    return psycopg.connect(
        host = os.getenv("POSTGRES_HOST"),
        port = os.getenv("POSTGRES_PORT"),
        dbname = os.getenv("POSTGRES_DB"),
        user = os.getenv("POSTGRES_USER"),
        password = os.getenv("POSTGRES_PASSWORD")
    )

def get_minio_client():
    return Minio(
        endpoint = os.getenv("MINIO_URL") + ":" + os.getenv("MINIO_PORT"),
        access_key = os.getenv("MINIO_API_ACCESSKEY"),
        secret_key = os.getenv("MINIO_API_SECRETKEY"),
        secure = False)

def get_minio_url(name: str):
    url = get_minio_client().presigned_get_object("highjump", name)
    return url

def query_joint_point(video_name: str):
    with get_postgres_client() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT frame_idx, position FROM video_yolo_pose WHERE video_name = %s", (video_name,))
            row = cursor.fetchall()    
            return row

coco_keypoints = {

}

rr.init("rerun_asset_video_auto_frames")
rr.serve_web(ws_port=4321, web_port=10000)

tag = 'raw_data/2024/10/27/20241027_144541.mp4'
url = get_minio_url(tag)

urllib.request.urlretrieve(url, "./test.mp4")
video_asset = rr.AssetVideo(path="./test.mp4")

# video_asset = rr.AssetVideo(path="./test.mp4")

joint_point_data = query_joint_point(tag)

rr.log("video", video_asset, static=True)
frame_timestamps_ns = video_asset.read_frame_timestamps_ns()
rr.send_columns(
    "video",
    # Note timeline values don't have to be the same as the video timestamps.
    times=[rr.TimeNanosColumn("video_time", frame_timestamps_ns)],
    components=[rr.VideoFrameReference.indicator(), rr.components.VideoTimestamp.nanoseconds(frame_timestamps_ns)],
)

for (idx, joint_point) in joint_point_data:
    rr.set_time_nanos('video_time', frame_timestamps_ns[idx])
    joint_position = pickle.loads(joint_point)
    for j in joint_position:
        rr.log('joint/marker2D', rr.Points2D(j[:, :2]))
        for joint_number in range(0, len(j)):
            rr.log('joint/joint_' + str(joint_number) + 'x', rr.Scalar(j[joint_number][0]))
            rr.log('joint/joint_' + str(joint_number) + 'y', rr.Scalar(j[joint_number][1]))

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  print("Ctrl-C received. Exiting.")
