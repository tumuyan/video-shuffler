import os
import re
from moviepy import editor


def merge_videos(filelist):
    if os.path.exists(filelist):
        videos = []
        video_path = filelist[0:-4] + ".mp4"
        ass_path = filelist[0:-4] + ".ass"
        file = open(
            filelist, 'r', encoding='UTF-8')
        for line in file:
            suffix = line.lower()[-4:]
            if suffix == ".txt" or suffix == ".ass":
                continue
            videos.append(editor.VideoFileClip(line))

        merged = editor.concatenate_videoclips(videos)
        merged.write_videofile(video_path)

        file.close

