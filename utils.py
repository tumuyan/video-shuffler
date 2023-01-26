
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


# 测试发现部分软件对lrc的时间只支持分:秒，不能使用小时
def timeStr2LrcTime(string):
    strs = string.split(":")
    length = len(strs)
    m = 0
    if length > 1:
        m = int(strs[-2])
    if length > 2:
        m = m + int(strs[-3])*60
    return "[{}:{}]".format(m, strs[-1])

# cue的时间格式为 分：秒：帧 一秒钟的音乐包含75个帧，数字从零开始，到74为止
def time2CueTime(sec):
    s = sec % 60
    m = int(sec // 60)
    f = int( s%1 * 75) 
    s = int(s)
    return "{}:{}:{}".format(m, s, f)
