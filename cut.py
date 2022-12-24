import os
import re
from moviepy import editor
import utils
from chapter import Chapter

video_suffixs = [".mp4",".mkv"]
audio_suffixs = [".mp3",".wav",".aac"]

class Ass:
    def __init__(self, ass_path, video_path="", remove_comment=1, time_threshold=10):
        """解析ASS字幕文件

        Args:
            ass_path (str): 字幕文件的路径
            video_path (str, optional): 视频文件的路径. Defaults to "".
            remove_comment (int, optional): 是否删除comment; 0 不删除（只有输出原时间轴才有效） 1 保留章节信息 2 不保留. Defaults to 1.
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
                    start = utils.timeStr2Sec(l[start_pos])
                    end = utils.timeStr2Sec(l[end_pos])
                    text = (l[text_pos])
                    name = l[name_pos]
                    format = l[0]
                    comment = not format.startswith("Dialogue")
                    if comment:
                        text = text.strip()
                        if text.startswith("##"):
                            if chapter:
                                self.chapters.append(chapter)
                                chapter_sub += 1
                            chapter_name = str(
                                chapter_main) + "." + str(chapter_sub) + " " + text[2:].strip()
                            chapter = None
                        elif text.startswith("#"):
                            if chapter:
                                self.chapters.append(chapter)
                                chapter_main += 1
                                chapter_sub = 1
                            chapter_name = str(
                                chapter_main) + "." + str(chapter_sub) + " " + text[1:].strip()
                            chapter = None
                        elif remove_comment > 0:
                            chapter.commitClip()
                            continue

                        if remove_comment > 1:
                            chapter.commitClip()
                            continue

                    if chapter == None:
                        chapter = Chapter(chapter_name, time_threshold,
                                          start_pos, end_pos)

                    chapter.add(l, comment, start, end, name)

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
        if chapter:
            if chapter.hasData():
                self.chapters.append(chapter)

    def split(self, name="", raw_time=False, cut_media=False, ref_content_text="", suffix=video_suffixs[0],skip_blank_chapter_name=False):
        """切分字幕和视频

        Args:
            name (str, optional): 切分后文件名的前缀. Defaults to "".
            raw_time (bool, optional): 使用原视频文件的时间戳. Defaults to False.
            cut_media (int, optional): 是否切分视频. Defaults to False.
            ref_content_text (str, optional): 文本文件或字符串；使用参考的目录切分（因为输出的视频片段变少了，速度会更快）. Defaults to "".
            suffix (str, optional): 输出多媒体文件的后缀
        Returns:
            str: 输出文件的文件夹，以及包含时间和章节信息的目录
            list: 输出的文件列表
        """
        write_content_file = True
        ref_content = []
        if len(ref_content_text) > 0:
            if os.path.exists(ref_content_text):
                ref_content_file = open(
                    ref_content_text, 'r', encoding='UTF-8')
                for line in ref_content_file:
                    rows = line.split('\t', 1)
                    ref_content.append(rows[0])

                ref_content_file.close()
                write_content_file = len(ref_content) > 0
            else:
                lines = ref_content_text.split("\n")
                for line in lines:
                    rows = line.split('\t', 1)
                    ref_content.append(rows[0])

        # dir = os.path.abspath(os.path.join(os.path.dirname(self.path),os.path.pardir))
        # dir = os.path.abspath(os.path.join(os.path.dirname(self.ass_path)))
        dir = self.ass_path[0:-4]
        if len(name) > 0:
            name = name+" "

        if len(self.video_path) < 5:
            cut_media = False
        if cut_media:
            dir = self.ass_path[0:-4]
        os.makedirs(dir, exist_ok=True)
        result = [dir + "/" + name + " filelist.txt"]

        content = dir + "\n"
        content_path = dir + "/" + name + " content.txt"
        print("content file: ", content_path)
        if write_content_file:
            result.append(content_path)

        print("len(ref_content): ", len(ref_content))

        cut_audio = suffix in audio_suffixs
        cut_video = suffix in video_suffixs

        for chapter in self.chapters:
            if len(ref_content) > 0:
                if utils.sec2TimeStr(chapter.start) not in ref_content:
                    continue
            if skip_blank_chapter_name:
                if chapter.isBlankName():
                    continue

            path = dir + "/" + name + chapter.name + ".ass"
            print(path)
            result.append(path)
            summary = chapter.getSummary()
            content += summary

            file = open(path, 'w', encoding='UTF-8')
            file.write(self.head)
            file.write(chapter.getAss(raw_time))
            file.close()
            if cut_media:
                time_clips = chapter.getClips()
                print(time_clips)
                media_clips = []
                for time_clip in time_clips:
                    if cut_video:
                        media_clips.append(editor.VideoFileClip(
                            self.video_path).subclip(time_clip[0], time_clip[1]))
                    elif cut_audio:
                        media_clips.append(editor.AudioFileClip(
                            self.video_path).subclip(time_clip[0], time_clip[1]))

                fn = dir + "/" + name + chapter.name + suffix
                result.append(fn)

                if cut_video:
                    merged = editor.concatenate_videoclips(media_clips)
                    merged.write_videofile(
                        fn  # , audio_codec="aac", bitrate=self.args.bitrate
                    )
                elif cut_audio:
                    merged = editor.concatenate_audioclips(media_clips)
                    merged.write_audiofile(fn)

        if write_content_file:
            content_file = open(content_path, 'w', encoding='UTF-8')
            content_file.write(content)
            content_file.close()
        filelist = open(result[0], 'w', encoding='UTF-8')
        filelist.write("\n".join(result))
        filelist.close()

        return content, result
