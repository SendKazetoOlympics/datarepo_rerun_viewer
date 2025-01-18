import rerun as rr  # NOTE: `rerun`, not `rerun-sdk`!
import numpy as np
import time
from minio import Minio
import psycopg
from psycopg.rows import TupleRow
from dotenv import load_dotenv
import os
import pickle
import uuid
import requests
from io import BytesIO, BufferedReader


# Load the environment variables from the .env file
load_dotenv() 

def get_postgres_client():
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


rr.init("rerun_asset_video_auto_frames")
rr.serve_web(ws_port=4321, web_port=10000)

tag = 'raw_data/2024/12/10/20241210_195854.mp4'
url = get_minio_url(tag)

print(url)

#response = requests.get(url)
# bytes_io = BytesIO(response.content)

video_asset = rr.AssetVideo(path="./test.mp4")#contents=bytes_io)

rr.log("video", video_asset, static=True)
frame_timestamps_ns = video_asset.read_frame_timestamps_ns()
rr.send_columns(
    "video",
    # Note timeline values don't have to be the same as the video timestamps.
    times=[rr.TimeNanosColumn("video_time", frame_timestamps_ns)],
    components=[rr.VideoFrameReference.indicator(), rr.components.VideoTimestamp.nanoseconds(frame_timestamps_ns)],
)

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  print("Ctrl-C received. Exiting.")
