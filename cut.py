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


class Chapter:
    def __init__(self, name, time_threshold, start_pos, end_pos):
        """存储一个剪辑片段

        Args:
            name (str): 片段名称
            time_threshold (int): 时间阈值;两个相邻字幕之间的间隔时间如果超过阈值，则进行裁剪.
            start_pos (int): start在字幕中是第几个位置
            end_pos (int): end在字幕中是第几个位置
        """
        self.name = name
        self.time_threshold = time_threshold
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.data = []
        self.start = -1
        self.clips = []
        self.clip_start = -1
        self.clip_end = -1
        # self.clip_end = -1

    def add(self, data, comment, start, end, name):
        """为片段添加一行字幕

        Args:
            data (list): 已经用`,`切分为数组的一行字幕内容
            comment (bool): 是否为注释
            start (int): 字幕的开始时间
            end (int): 字幕的结束时间
            name (str): 说话人
        """
        self.data.append(data)
        if not comment:
            if self.clip_start < 0:
                self.clip_start = start
                if self.start < 0:
                    self.start = start
            elif start - self.clip_end > self.time_threshold:
                self.clips.append([self.clip_start, self.clip_end])
                self.clip_start = start
            self.clip_end = end
        elif self.clip_start >= 0:
            self.clips.append([self.clip_start, self.clip_end])
            self.clip_start = -1

    def hasData(self):
        return len(self.data) > 0

    def getAss(self, raw_time):
        text = ""
        if raw_time:
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

    def getClips(self):
        if self.clip_start >= 0:
            self.clips.append([self.clip_start, self.clip_end])
            self.clip_start = -1
        return self.clips

    def getSummary(self):
        return sec2TimeStr(self.start) + "\t" + self.name + "\n"


class Ass:
    def __init__(self, ass_path, video_path="", remove_comment=1, time_threshold=10):
        """解析ASS字幕文件

        Args:
            ass_path (str): 字幕文件的路径
            video_path (str, optional): 视频文件的路径. Defaults to "".
            remove_comment (int, optional): 是否删除comment; 0 不删除 1 保留章节信息 2 不保留. Defaults to 1.
            time_threshold (int, optional): 时间阈值;两个相邻字幕之间的间隔时间如果超过阈值，则进行裁剪. Defaults to 10.
        """
        remove_comment = int(remove_comment)
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
        chapter_main = 1
        chapter_sub = 1

        # 输出时的章节名称
        chapter_name = str(chapter_main) + "." + str(chapter_sub)

        self.head = ""
        self.chapters = []
        chapter = None

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
                            self.chapters.append(chapter)
                            chapter_sub += 1
                            chapter_name = str(
                                chapter_main) + "." + str(chapter_sub) + " " + text[2:].strip()
                            chapter = None
                        elif text.startswith("#"):
                            self.chapters.append(chapter)
                            chapter_main += 1
                            chapter_sub = 1
                            chapter_name = str(
                                chapter_main) + "." + str(chapter_sub) + " " + text[1:].strip()
                            chapter = None
                        elif remove_comment > 0:
                            continue

                        if remove_comment > 1:
                            continue

                    if chapter == None:
                        chapter = Chapter(chapter_name, time_threshold,
                                          start_pos, end_pos)

                    chapter.add(l, comment, start, end, name)

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

        if chapter.hasData():
            self.chapters.append(chapter)

    def split(self, name="", raw_time=False, cut_video=False):
        """切分字幕和视频

        Args:
            name (str, optional): 切分后文件名的前缀. Defaults to "".
            raw_time (bool, optional): 使用原视频文件的时间戳. Defaults to False.
            cut_video (bool, optional): 是否切分视频. Defaults to False.
        """
        # dir = os.path.abspath(os.path.join(os.path.dirname(self.path),os.path.pardir))
        # dir = os.path.abspath(os.path.join(os.path.dirname(self.ass_path)))
        dir = self.ass_path[0:-4]
        if len(name) > 0:
            name = name+" "

        if len(self.video_path) < 5:
            cut_video = False
        if cut_video:
            dir = self.ass_path[0:-4]
        os.makedirs(dir, exist_ok=True)
        result = [dir + "/" + name + " filelist.txt"]

        content = dir + "\n"
        content_path = dir + "/" + name + " content.txt"
        print("content file: ", content_path)
        result.append(content_path)
        content_file = open(content_path, 'w', encoding='UTF-8')

        for chapter in self.chapters:
            path = dir + "/" + name + chapter.name + ".ass"
            print(path)
            result.append(path)
            summary = chapter.getSummary()
            content += summary
            content_file.write(summary)
            file = open(path, 'w', encoding='UTF-8')
            file.write(self.head)
            file.write(chapter.getAss(raw_time))
            file.close()

            if cut_video:
                time_clips = chapter.getClips()
                videos = []
                for time_clip in time_clips:
                    videos.append(editor.VideoFileClip(
                        self.video_path).subclip(time_clip[0], time_clip[1]))

                fn = dir + "/" + name + chapter.name + ".mp4"
                result.append(fn)
                merged = editor.concatenate_videoclips(videos)
                merged.write_videofile(
                    fn  # , audio_codec="aac", bitrate=self.args.bitrate
                )

        content_file.close()
        filelist = open(result[0], 'w', encoding='UTF-8')
        filelist.write("\n".join(result))
        filelist.close()

        return content, result
