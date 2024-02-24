from pathlib import Path
import json
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

current_dir = Path(__file__).resolve().parent
coordinate_dir = current_dir / "coordinates"

name_to_id = {
    "WRIST": 0,
    "THUMB_CMC": 1, "THUMB_MCP": 2, "THUMB_IP": 3, "THUMB_TIP": 4,
    "INDEX_FINGER_MCP": 5, "INDEX_FINGER_PIP": 6, "INDEX_FINGER_DIP": 7, "INDEX_FINGER_TIP": 8,
    "MIDDLE_FINGER_MCP": 9, "MIDDLE_FINGER_PIP": 10, "MIDDLE_FINGER_DIP": 11, "MIDDLE_FINGER_TIP": 12,
    "RING_FINGER_MCP": 13, "RING_FINGER_PIP": 14, "RING_FINGER_DIP": 15, "RING_FINGER_TIP": 16,
    "PINKY_MCP": 17, "PINKY_PIP": 18, "PINKY_DIP": 19, "PINKY_TIP": 20
}

id_to_name = dict()
for k,v in name_to_id.items():
    id_to_name[v] = k

movie_name_dict = {
    "手元1": "hand_1",
    "手元2": "hand_2",
    "同期1": "sync_1",
    "同期2": "sync_2",
    "同期3": "sync_3"
}
method_dict = {
    "あるキーポイントの軌跡を見る": "track",
    "2つのキーポイント間の距離の変化を見る": "distance",
    "角度の変化を見る": "angle"
}

#########
# INPUT #
#########
movie_name_org = st.selectbox("動画の名前", ["手元1", "手元2", "同期1", "同期2", "同期3"]) 
movie_name = movie_name_dict[movie_name_org]

cols = st.columns(2)
start_min = cols[0].number_input("開始時間（分）", 0, 10, 0)
start_sec = cols[1].number_input("開始時間（秒）", 0, 59, 0)
cols = st.columns(2)
end_min = cols[0].number_input("終了時間（分）", 0, 10, 0)
end_sec = cols[1].number_input("終了時間（秒）", 0, 59, 0)
range_of_movies = [f"{start_min}分{start_sec}秒", f"{end_min}分{end_sec}秒"]

# check the time
if start_min*60+start_sec >= end_min*60+end_sec:
    st.error(":warning: 終了時間は開始時間よりも後にしてください！")

method_org = st.selectbox("分析方法", ["あるキーポイントの軌跡を見る", "2つのキーポイント間の距離の変化を見る", "角度の変化を見る"])
method = method_dict[method_org]

keypoints = st.multiselect(
    "Keypoints", list(name_to_id.keys()), 
    max_selections=1 if method == "track" else 2 if method == "distance" else 3, 
    default=["MIDDLE_FINGER_PIP"] if method == "track" else ["PINKY_TIP", "THUMB_TIP"] if method == "distance" else ["THUMB_TIP", "THUMB_IP", "THUMB_MCP"]
    )
keypoints = list(map(lambda x: name_to_id[x], keypoints))
st.image("https://developers.google.com/static/mediapipe/images/solutions/hand-landmarks.png")
st.markdown("---")

# check the number of keypoints
if method == "track" and len(keypoints) != 1:
    st.error(":warning: The number of keypoints must be 1 !")
    st.stop()
elif method == "distance" and len(keypoints) != 2:
    st.error(":warning: The number of keypoints must be 2 !")
    st.stop()
elif method == "angle" and len(keypoints) != 3:
    st.error(":warning: The number of keypoints must be 3 !")
    st.stop()

##################
# show the input #
##################
st.info(f"""\
- :movie_camera: ：{movie_name_org}
- :clock3: ：{range_of_movies[0]} ～ {range_of_movies[1]}
- :male-detective: ：{method_org}
- :raised_hand_with_fingers_splayed: ：{', '.join([id_to_name[k] for k in keypoints])}
""")

###################################
# load meta data & make time axis #
###################################
with open(coordinate_dir / "meta.json", "r", encoding="utf-8-sig") as f:
    meta = json.load(f)[movie_name]
    fps = meta["fps"]
    num_frames = meta["num_frames"]
    time_axis = np.arange(num_frames) / fps

#################
# str --> frame #
#################
range_of_frames = []
for r in range_of_movies:
    minute, second = r.split("分")
    second = second.replace("秒", "")
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
    ax.plot(sub[:,0], -sub[:,1], lw=0.5)
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect('equal')
    ax.grid()
    st.pyplot(fig)

###############
# 2. distance #
###############
elif method == "distance":
    sub = sub[:, keypoints]
    distance = np.sqrt(np.sum((sub[:,0] - sub[:,1])**2, axis=1))
    df = pd.DataFrame({"time":time_axis, "distance":distance})
    df = df.set_index("time")
    st.line_chart(df)

#############
# 3. angle #
#############
elif method == "angle":
    sub = sub[:, keypoints]
    vec1 = sub[:,0] - sub[:,1]
    vec2 = sub[:,2] - sub[:,1]
    cos = np.sum(vec1 * vec2, axis=1) / (np.sqrt(np.sum(vec1**2, axis=1)) * np.sqrt(np.sum(vec2**2, axis=1)))
    angle = np.arccos(cos) * 180 / np.pi
    df = pd.DataFrame({"time":time_axis, "angle":angle})
    df = df.set_index("time")
    st.line_chart(df)