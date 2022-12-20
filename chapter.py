import utils


class Chapter:
    def __init__(self, name, time_threshold, start_pos, end_pos, time_offset=0):
        """存储一个剪辑片段

        Args:
            name (str): 片段名称
            time_threshold (int): 时间阈值;两个相邻字幕之间的间隔时间如果超过阈值，则进行裁剪.
            start_pos (int): start在字幕中是第几个位置
            end_pos (int): end在字幕中是第几个位置
            time_offset (int, optional): 对字幕时间轴做整体偏移量。使用参数时，只能使用原时间轴. Defaults to 0.
        """
        # 默认text处于data的末位，不重新解析，并且包含了换行符

        print("time_offset:", time_offset)
        self.name = name
        self.time_threshold = time_threshold
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.time_offset = time_offset
        self.data = []
        self.data2 = []
        self.start = -1
        self.clips = []
        self.clip_start = -1
        self.clip_end = -1
        # self.clip_end = -1
        self.dut = 0

    def commitClip(self):
        """仅保存当前编辑中的片段(当需要插入的内容为注释，且不需要保存时)
        """
        if self.clip_start > 0:
            self.dut += (self.clip_end-self.clip_start)
            self.clips.append([self.clip_start, self.clip_end])
            self.clip_start = -1

    def add(self, data, comment,  start, end, name):
        """为片段添加一行字幕

        Args:
            data (list): 已经用`,`切分为数组的一行字幕内容
            comment (bool): 是否为注释
            start (int): 字幕的开始时间
            end (int): 字幕的结束时间
            name (str): 说话人
            skip (bool): 实际不插入内容（当使用一行内容）
        """
        # print(data)
        #
        lenth = len(data)
        if lenth < 2:
            return

        if self.time_offset != 0:
            data[self.start_pos] = utils.sec2TimeStr(start + self.time_offset)
            data[self.end_pos] = utils.sec2TimeStr(end + self.time_offset)
            # print(data)
            self.data.append(data)
            return
        self.data.append(data)

        if not comment:
            if self.clip_start < 0:
                self.clip_start = start
                if self.start < 0:
                    self.start = start
            elif end < self.clip_end or start - self.clip_end > self.time_threshold:
                self.dut += (self.clip_end-self.clip_start)
                self.clips.append([self.clip_start, self.clip_end])
                self.clip_start = start
            self.clip_end = end
            data[self.start_pos] = utils.sec2TimeStr(
                start - self.clip_start + self.dut)
            data[self.end_pos] = utils.sec2TimeStr(
                end - self.clip_start + self.dut)
            self.data2.append(data)
        elif self.clip_start >= 0:
            self.dut += (self.clip_end-self.clip_start)
            self.clips.append([self.clip_start, self.clip_end])
            self.clip_start = -1

        if comment and (data[len(data)-1]).startswith("#"):
            # 如果使用新时间轴，由于注释的内容在视频上没有对应的帧，因此把章节信息的持续帧数改为0，其他注释内容直接删除
            data[self.start_pos] = utils.sec2TimeStr(self.dut)
            data[self.end_pos] = utils.sec2TimeStr(self.dut)
            self.data2.append(data)

    def hasData(self):
        return len(self.data) > 0

    def getAss(self, raw_time):
        # print ("data:",self.data)
        # print("data2:",self.data2)
        text = ""
        if raw_time:
            for item in self.data:
                text = text + ",".join(item)
        else:
            for item in self.data2:
                text = text + ",".join(item)
        return text

    def getLrc(self, raw_time, remove_comment=1):
        text = ""
        if raw_time:
            for item in self.data:
                if remove_comment > 0 and item[0].startswith("Comment"):
                    if remove_comment > 1 and not item[-1].startswith("#"):
                        continue
                text = text + \
                    utils.timeStr2LrcTime(item[self.start_pos]) + item[-1]
        else:
            for item in self.data2:
                if remove_comment > 0 and item[0].startswith("Comment"):
                    if remove_comment > 1 and not item[-1].startswith("#"):
                        continue
                text = text + \
                    utils.timeStr2LrcTime(item[self.start_pos]) + item[-1]
        return text

    def getClips(self):
        if self.clip_start >= 0:
            self.clips.append([self.clip_start, self.clip_end])
            self.clip_start = -1
        return self.clips

    def getSummary(self):
        return utils.sec2TimeStr(self.start) + "\t" + self.name + "\n"


    def isBlankName(self):
        name = self.name.split(" ",2)
        if len(name) !=2:
            return True
        return len(name[1].replace(" ",""))==0