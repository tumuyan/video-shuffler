
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

