import os
import re
from moviepy import editor


def timeStr2Sec(string):
    strs = string.split(":")
    v = 0.0
    for s in strs:
        v = v*60 + float(s)
    return v


def sec2TimeStr(sec):
    s = sec % 60
    m = int(sec // 60)
    h = m // 60
    m = m % 60
    return "{}:{}:{:.2f}".format(h, m, s)


class Clip:
    def __init__(self, name, time_threshold, start_pos, end_pos):
        self.name = name
        self.time_threshold = time_threshold
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.data = []
        self.start = -1

    def add(self, data, comment, start, end, name):
        self.data.append(data)
        if not comment:
            self.end = end
            if self.start < 0:
                self.start = start

    def hasData(self):
        return len(self.data) > 0

    def getAss(self, abs_time):
        text = ""
        if abs_time:
            for item in self.data:
                text = text + ",".join(item)
        else:
            for item in self.data:
                it = item.copy()
                it[self.start_pos] = sec2TimeStr(
                    timeStr2Sec(it[self.start_pos]) - self.start)
                it[self.end_pos] = sec2TimeStr(
                    timeStr2Sec(it[self.end_pos]) - self.start)
                text = text + ",".join(it)

        return text

    def getContent(self):
        return sec2TimeStr(self.start) + "\t" + self.name + "\n"


# def AssEvent:
#     def __init__(self,line, Layer, Start, End, Style, Name, Text):
#         self.line = line
#         self.

# path 待处理的文件
# remove_comment 是否删除comment。0 不删除 1 保留章节信息 2 不保留
# time_threshold 时间阈值。两个相邻字幕之间的间隔时间如果超过阈值，则进行裁剪


class Ass:
    def __init__(self, ass_path, video_path="", remove_comment=1, time_threshold=10):
        self.ass_path = ass_path
        self.video_path = video_path

        if not ass_path.lower().endswith(".ass"):
            print("not ass file")
            return

        event_len = 0

        # 各个字段在event中的位置,只能处理开头Format: Layer, 结尾Text的ASS格式的字幕，并且不会对layer做处理
        # 原因是直接简单粗暴的使用逗号分割每行字幕，因此Format: layer是一个整体；而Text可能包含逗号。分多次分割的话是可以处理这些情况的，但是意义不大
        # Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        start_pos = -1
        end_pos = -1
        text_pos = -1
        name_pos = -1

        #章节标号, 只实现两级章节
        chapter = 1
        chapter_ = 1

        # 输出时的章节名称
        chapter_name = str(chapter) + "." + str(chapter_)

        self.head = ""
        self.clips = []
        clip = None

        ass = open(ass_path, 'r', encoding='UTF-8')
        for i in ass:
            if event_len > 0:
                l = i.split(",", event_len)
                if (len(l) == event_len):
                    start = timeStr2Sec(l[start_pos])
                    end = timeStr2Sec(l[end_pos])
                    text = (l[text_pos])
                    name = l[name_pos]
                    format = l[0]
                    comment = not format.startswith("Dialogue")
                    if comment:
                        text = text.strip()
                        if text.startswith("##"):
                            self.clips.append(clip)
                            chapter_ += 1
                            chapter_name = str(
                                chapter) + "." + str(chapter_) + " " + text[2:].strip()
                            clip = None
                            content = ""

                        elif text.startswith("#"):
                            self.clips.append(clip)
                            chapter += 1
                            chapter_ = 1
                            chapter_name = str(
                                chapter) + "." + str(chapter_) + " " + text[1:].strip()
                            clip = None
                            content = ""
                        elif remove_comment > 0:
                            continue

                        if remove_comment > 1:
                            continue

                    if clip == None:
                        clip = Clip(chapter_name, time_threshold,
                                    start_pos, end_pos)

                    clip.add(l, comment, start, end, name)

                    # l[start_pos] = sec2TimeStr(start - time_dif)
                    # l[end_pos] = sec2TimeStr(end - time_dif)

                    # # if(event_len - text_pos ==1):
                    # content = content + ",".join(l)

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

        if clip.hasData():
            self.clips.append(clip)

    # 默认只切分字幕，不切分视频
    def split(self, name="", abs_time=False, cut_video=False):
        # dir = os.path.abspath(os.path.join(os.path.dirname(self.path),os.path.pardir))
        dir = os.path.abspath(os.path.join(os.path.dirname(self.ass_path)))
        if len(name) > 0:
            name = name+" "

        if len(self.video_path) < 5:
            cut_video = False

        content_path = dir + "/" + name + " content.txt"
        print("content file: ", content_path)
        content_file = open(content_path, 'w', encoding='UTF-8')

        for clip in self.clips:
            path = dir + "/" + name + clip.name + ".ass"
            print(path)
            content_file.write(clip.getContent())
            file = open(path, 'w', encoding='UTF-8')
            file.write(self.head)
            file.write(clip.getAss(abs_time))
            file.close()

        content_file.close()
