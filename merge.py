import os
import re
from moviepy import editor
import utils
from chapter import Chapter
import re


class Ass2:
    def __init__(self, ass_path, time_offset=0):
        """解析ASS字幕文件

        Args:
            ass_path (str): 字幕文件的路径
        """
        self.ass_path = ass_path

        if not ass_path.lower().endswith(".ass"):
            print("not ass file")
            return

        event_len = 0
        start_pos = -1
        end_pos = -1
        text_pos = -1
        name_pos = -1
        self.head = ""
        self.chapter = None

        regex = r".+[/\\]"
        chapter_name = re.sub(regex, "", ass_path, 0, re.MULTILINE)

        ass = open(ass_path, 'r', encoding='UTF-8')
        for i in ass:
            if event_len > 0:
                l = i.split(",", event_len)
                if (len(l) == event_len):
                    start = utils.timeStr2Sec(l[start_pos])
                    end = utils.timeStr2Sec(l[end_pos])
                    text = (l[text_pos])
                    name = l[name_pos]
                    format = l[0]

                    if self.chapter == None:
                        if format.startswith("Comment") and text.startswith("#"):
                            chapter_name = text
                        self.chapter = Chapter(
                            chapter_name, 999999, start_pos, end_pos, time_offset)
                    self.chapter.add(l, False, start, end, name)

            else:
                if (len(i)) > 0:
                    self.head = self.head + i
                i = i.strip().replace(" ", "")
                if (i[0:7] == "Format:"):
                    i = i[7:].strip()
                    pos = i.split(",")
                    if len(pos) < 5:
                        continue
                    if "Start" not in pos:
                        continue

                    event_len = len(pos)
                    start_pos = pos.index("Start")
                    end_pos = pos.index("End")
                    text_pos = pos.index("Text")
                    name_pos = pos.index("Name")

    def getAss(self):
        return self.chapter.getAss(True)

    def getHead(self):
        return self.head

    def getLrc(self, remove_comment=1):
        return self.chapter.getLrc(remove_comment)

    def hasData(self):
        return self.chapter.hasData()


def merge_videos(filelist, output_lrc=False):
    if os.path.exists(filelist):
        videos = []
        suffix = ".mp4"
        video_output_path = filelist[0:-4] + suffix
        ass_output_path = filelist[0:-4] + ".ass"
        lrc_output_path = filelist[0:-4] + ".lrc"
        duration = 0
        filelist_file = open(
            filelist, 'r', encoding='UTF-8')

        ass_head = None
        ass_file = open(ass_output_path, "w", encoding='UTF-8')
        lrc_file = None
        if output_lrc:
            lrc_file = open(lrc_output_path, "w", encoding='UTF-8')

        for l in filelist_file:
            # 去除换行
            video_path = l.rstrip()
            suffix = video_path.lower()[-4:]
            if suffix == ".txt" or suffix == ".ass":
                continue
            clip = editor.VideoFileClip(video_path)

            if clip.duration > 0:
                videos.append(clip)
                ass_path = video_path[0:-4] + ".ass"
                ass = Ass2(ass_path, duration)
                if ass.hasData():
                    if ass_head == None:
                        ass_head = ass.getHead()
                        ass_file.write(ass_head)
                    ass_file.write(ass.getAss())

                    if output_lrc:
                        lrc_file.write(ass.getLrc(1))
                duration += clip.duration

        filelist_file.close()
        ass_file.close()
        if output_lrc:
            lrc_file.close()
        merged = editor.concatenate_videoclips(videos)
        merged.write_videofile(video_output_path)


def ass2lrc(path):
    if os.path.exists(path) and path.lower().endswith(".ass"):
        lrc_output_path = path[0:-4] + ".lrc"
        print("ass2lrc: ", lrc_output_path)
        lrc_file = open(lrc_output_path, "w", encoding='UTF-8')
        ass = Ass2(path)
        if ass.hasData():
            lrc_file.write(ass.getLrc(1))
        lrc_file.close()
        return lrc_output_path

def asslist2lrc(filelist):
    """把每个ass字幕文件转换为lrc

    Args:
        filelist (list, str): 一个文件路径列表，或者一个包含文件列表的txt文件的路径

    Returns:
        list: lrc文件列表
    """
    result = []
    if type(filelist) == str:
        if os.path.exists(filelist):
            if filelist.lower().endswith("txt"):
                filelist_file = open(
                    filelist, 'r', encoding='UTF-8')
                for l in filelist_file:
                    result.append(ass2lrc(l.rstrip()))
            else:
                # 仅兜底
                result.append(ass2lrc(filelist))
    elif type(filelist) == list:
        for path in filelist:
            if os.path.exists(path):
                result.append(ass2lrc(path))


    else:
        print("Err: asslist2lrc() filelist not str ")
    return result

# merge_videos("./test/7月11日/ filelist.txt",True)
