from pathlib import Path
from argparse import ArgumentParser
import numpy as np
import json
import matplotlib.pyplot as plt

current_dir = Path(__file__).resolve().parent
coordinate_dir = current_dir / "coordinates"

# parse arguments
parser = ArgumentParser()
parser.add_argument("--movie", type=str, required=True, help="Movie name. Do not include the extension. ex) sync_1")
parser.add_argument("--range", type=str, nargs="+", help="Range of movies. ex) --range 1m25s 1m35s")
parser.add_argument("--method", type=str, required=True, choices=['track', 'distance', 'angle'], help="Method of analytics.")
parser.add_argument("--keypoints", type=int, nargs="+", help="If the type is track, you need to specify one keypoint, if the type is distance, you need to specify two keypoints, and if the type is angle, you need to specify three keypoints. ex) --keypoints 2 3 4")
movie_name = parser.parse_args().movie
range_of_movies = parser.parse_args().range
method = parser.parse_args().method
keypoints = parser.parse_args().keypoints
assert len(keypoints) == 1 if method == "track" else len(keypoints) == 2 if method == "distance" else len(keypoints) == 3, "The number of keypoints is not correct."
assert len(range_of_movies) == 2, "The number of --range should be 2. ex) --range 1m25s 1m35s"

# load meta data & make time axis
with open(coordinate_dir / "meta.json", "r", encoding="utf-8-sig") as f:
    meta = json.load(f)[movie_name]
    fps = meta["fps"]
    num_frames = meta["num_frames"]
    time_axis = np.arange(num_frames) / fps

# str --> frame
range_of_frames = []
for r in range_of_movies:
    minute, second = r.split("m")
    second = second.replace("s", "")
    s = int(minute) * 60 + int(second)
    frame = int(s * fps)
    range_of_frames.append(frame)
time_axis = time_axis[range_of_frames[0]:range_of_frames[1]]

# load coordinate data
coordinate = np.load(coordinate_dir / (movie_name + ".npy")) 
sub = coordinate[range_of_frames[0]:range_of_frames[1]]

############
# 1. track #
############
if method == "track":
    sub = sub[:, keypoints[0]]
    xmin,xmax = np.nanmin(coordinate[:,:,0]), np.nanmax(coordinate[:,:,0])
    ymin,ymax = np.nanmin(-coordinate[:,:,1]), np.nanmax(-coordinate[:,:,1])
    fig, ax = plt.subplots()
    ax.plot(sub[:,0], -sub[:,1], label=f"keypoint {keypoints[0]}", lw=0.5)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"Track ({movie_name}, {range_of_movies[0]}-{range_of_movies[1]})")
    ax.set_aspect('equal')
    ax.legend()
    ax.grid()
    save_dir = current_dir / "track"
    save_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_dir / f"{movie_name}_{range_of_movies[0]}-{range_of_movies[1]}_keypoint{keypoints[0]}.png", dpi=300)

###############
# 2. distance #
###############
elif method == "distance":
    sub = sub[:, keypoints]
    distance = np.sqrt(np.sum((sub[:,0] - sub[:,1])**2, axis=1))
    fig, ax = plt.subplots(figsize=(15, 4))
    ax.plot(time_axis, distance)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("distance")
    ax.set_title(f"Distance ({movie_name}, {range_of_movies[0]}-{range_of_movies[1]}, keypoint{keypoints[0]}-{keypoints[1]})")
    ax.grid()
    save_dir = current_dir / "distance"
    save_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_dir / f"{movie_name}_{range_of_movies[0]}-{range_of_movies[1]}_keypoint{keypoints[0]}-{keypoints[1]}.png", dpi=300)

#############
# 3. angle #
#############
elif method == "angle":
    sub = sub[:, keypoints]
    vec1 = sub[:,0] - sub[:,1]
    vec2 = sub[:,2] - sub[:,1]
    cos = np.sum(vec1 * vec2, axis=1) / (np.sqrt(np.sum(vec1**2, axis=1)) * np.sqrt(np.sum(vec2**2, axis=1)))
    angle = np.arccos(cos) * 180 / np.pi
    fig, ax = plt.subplots(figsize=(15, 4))
    ax.plot(time_axis, angle)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("angle (°)")
    ax.set_title(f"Angle ({movie_name}, {range_of_movies[0]}-{range_of_movies[1]}, keypoint{keypoints[0]}-{keypoints[1]}-{keypoints[2]})")
    ax.grid()
    save_dir = current_dir / "angle"
    save_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_dir / f"{movie_name}_{range_of_movies[0]}-{range_of_movies[1]}_keypoint{keypoints[0]}-{keypoints[1]}-{keypoints[2]}.png", dpi=300)
