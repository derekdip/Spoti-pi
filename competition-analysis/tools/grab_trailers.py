#!/usr/bin/env python3
"""Download competition trailers and turn each into small frame grids + captions.

Run on your own computer (YouTube blocks the cloud research container):
    pip install yt-dlp           # also needs ffmpeg on PATH (brew/winget/apt install ffmpeg)
    python grab_trailers.py
Output: trailer_pack.zip (a few MB). Upload that zip to the Claude session.
"""
import os, subprocess, sys, zipfile, glob, shutil

TRAILERS = {
    "doodle-figure": "3wYZPEKiKsQ",
    "game-night": "ktcjpyVD8ic",
    "23-17": "sP5u69Aq0yM",
    "sneak-a-snack": "CUzi74dLO7Q",
    "campy": "RXwQpWt2CbE",
    "rule-maker": "jW5aQqDpB74",
    "lets-flock": "FpNMwfshoss",
    "kaiju-corp": "e_grbP5unmU",
    "crokinole": "QenNcsiwx5Y",
    "bots-and-pans": "sVtDYQTE6GY",
}
FRAME_EVERY_S = 2          # one frame every 2 seconds
GRID = "4x3"               # 12 frames per grid image (24 s of video per grid)
OUT = "trailer_pack"

def run(cmd):
    print(">", " ".join(cmd)); return subprocess.run(cmd, check=False)

def main():
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH. Install it first.")
    os.makedirs(OUT, exist_ok=True)
    for name, vid in TRAILERS.items():
        d = os.path.join(OUT, name); os.makedirs(d, exist_ok=True)
        video = os.path.join(d, "video.mp4")
        if not os.path.exists(video):
            run([sys.executable, "-m", "yt_dlp", "-f", "bv*[height<=480][ext=mp4]+ba[ext=m4a]/b[height<=480]/b",
                 "--merge-output-format", "mp4", "-o", video,
                 "--write-auto-subs", "--write-subs", "--sub-langs", "en.*", "--sub-format", "vtt",
                 "--write-info-json", f"https://www.youtube.com/watch?v={vid}"])
            for f in glob.glob(os.path.join(d, "video*.vtt")):
                os.replace(f, os.path.join(d, "captions.vtt"))
        if not os.path.exists(video):
            print(f"!! could not download {name}"); continue
        # frame grids with timestamps burned in
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-vf",
             f"fps=1/{FRAME_EVERY_S},scale=480:-2,"
             "drawtext=text='%{pts\\:hms}':x=8:y=8:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.6,"
             f"tile={GRID}:padding=4", "-q:v", "4", os.path.join(d, "grid_%02d.jpg")])
        # first 5 seconds at higher density (1 frame / 0.5 s)
        run(["ffmpeg", "-y", "-loglevel", "error", "-t", "5", "-i", video, "-vf",
             "fps=2,scale=480:-2,tile=5x2:padding=4", "-q:v", "4", os.path.join(d, "first5s.jpg")])
    with zipfile.ZipFile("trailer_pack.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in glob.glob(f"{OUT}/*/*"):
            if not f.endswith(".mp4"):
                z.write(f)
    print("\nDone: upload trailer_pack.zip (videos are kept locally, not zipped).")

if __name__ == "__main__":
    main()
