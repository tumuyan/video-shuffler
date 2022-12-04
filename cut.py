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
    return "{}:{}:{:.2f}".format(h,m,s)



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
        self.chapter_names = []
        self.chapter_content = []

        head=""
        content = ""

        time_dif = -1
        clip_start =-1
        clip_end = -1
        clips = []


        ass = open(ass_path ,'r',encoding= 'UTF-8')
        for i in ass:
            if event_len>0:
                l = i.split(",",event_len)
                if(len(l)==event_len):
                    start = timeStr2Sec(l[start_pos])
                    end =  timeStr2Sec(l[end_pos])
                    text = (l[text_pos])
                    name = l[name_pos]
                    format = l[0]

                    if not format.startswith("Dialogue"):
                        text = text.strip()
                        if text.startswith("##"):
                            chapter_ +=1
                            self.chapter_names.append(chapter_name)
                            self.chapter_content.append(content)
                            chapter_name = str(chapter) + "." + str(chapter_) + text[2:].strip()
                            time_dif =-1
                            content = ""

                        elif text.startswith("#"):
                            chapter +=1
                            chapter_ = 1
                            self.chapter_names.append(chapter_name)
                            self.chapter_content.append(content)
                            chapter_name = str(chapter) + "." + str(chapter_) + text[1:].strip()
                            time_dif=-1
                            content = ""
                        elif remove_comment>0:
                            continue

                        if remove_comment >1:
                            continue

                    if time_dif <0:
                        time_dif = start
                        content = head

                    l[start_pos] = sec2TimeStr(start - time_dif)
                    l[end_pos] = sec2TimeStr(end - time_dif)

                    # if(event_len - text_pos ==1):
                    content = content + ",".join(l)


            else:
                if(len(i))>0:
                    head = head + i
                i = i.strip().replace(" ","")
                if (i[0:7] == "Format:"):
                    i = i[7:].strip()
                    pos = i.split(",")
                    if len(pos) <5 :
                        continue
                    if "Start" not in pos:
                        continue

                    event_len = len(pos)
                    start_pos = pos.index("Start")
                    end_pos = pos.index("End")
                    text_pos = pos.index("Text")
                    name_pos = pos.index("Name")
        if(len(content)>0):
            self.chapter_names.append(chapter_name)
            self.chapter_content.append(content)

    # 默认只切分字幕，不切分视频
    def split(self,name="",cut_video=False):
        # dir = os.path.abspath(os.path.join(os.path.dirname(self.path),os.path.pardir))
        dir = os.path.abspath(os.path.join(os.path.dirname(self.ass_path))) 
        if  len(name)>0:
            name = name+" " 

        if len(self.video_path) < 5:
            cut_video = False
        
        txt_path = dir + "/" + name + "_filelist.txt" 
        print("filelist: ",txt_path)
        txt_file = open( txt_path,'w',encoding= 'UTF-8')

        for i in range(0,len(self.chapter_names)):
            chapter_name = self.chapter_names[i]
            path = dir + "/" + name +chapter_name+ ".ass" 
            print(path)
            txt_file.write(path)
            txt_file.write("\n")
            file = open( path,'w',encoding= 'UTF-8')
            file.write(self.chapter_content[i])
            file.close()

        txt_file.close()
