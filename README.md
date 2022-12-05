# Video Shuffler | 洋片箱
Cut video to clips and shuffle them by ass file.  
用ass格式的字幕文件切割视频，并重组输出。

## 缘起
2022年9月，我在做Tacotron2的语音合成模型的训练。  
在准备数据集的时候，做了一个简单的用ass字幕切割音频文件的工具。  
工作流程非常顺畅，可以通过调整字幕时间控制剪辑位置，可以删除字幕取消一条内容，可以合并多行字幕来合并音频文件。 
后来我想，如果用这个基础上切割视频并重新排序，是不是就可以方便的剪辑二刀流或者三剪一视频了呢？  
但是一直没有动手。 

然后我在11月看到李沐老师的[AutoCut](https://github.com/mli/autocut/)，我们理念相近但是又不完全相合。
因此开始自己制作工具。 

在制作的过程中，又逐步改变了想法，放弃了Autocut项目使用markdown文件的做法。

洋片箱的命名来自游戏恋爱绮谭，一种现实有原型的怪异，只要更改照片的顺序就能够改变事实。

## 为什么使用字幕驱动剪辑
多数三剪一和二刀流主要是以人物说了什么内容而驱动的。

## 为什么在非编软件外操作
有没有在说话，可以通过波形图查看；说的内容，可以通过字幕查看。似乎目前的非编软件是提供了操作界面，但是还是不够快捷。
并不能很好标注我在剪辑的这几个片段到底是什么内容。

我所推崇的字幕编辑工具Aegisub能够更好地调整字幕；而洋片箱输出的结果，已经裁剪掉了大量无用内容；并且输出的文件名包含了章节信息，导入非编软件之后也能清楚地分辨

最后，对业余视频剪辑来说，存储和搜索视频素材是很困难的；但是文本搜索就简单很多了。如果每个视频都保留了字幕文件（如果保留了音频那就更好了），而本地硬盘中并没有保留视频本身，那么在制作视频前，无需下载原视频文件就可以开工——搜索字幕中需要的片段，编辑并保存字幕副本，当视频下载回来的时候就可以直接进一步剪辑了。

## 计划抄什么
虽然看上去有点缝合怪，但是就要都做进去。
- [x] 使用ass字幕切割视频为多个片段，同时输出切分的字幕和切分章节文件名列表（txt文件）
- [ ] 使用txt文件控制，合并多个视频和字幕为一个，同时输出合并字幕(暂时还没有做，拖剪辑软件里合并其实挺快的)
- [x] 在兼容ass格式的基础上，对字幕的信息做扩展
- [x] 使用gradio制作UI
- [ ] 自动识别字幕中每句分别属于哪个角色（目前试过的几个开源项目效果都还不够实用）
- [ ] 快速切换字幕中是否包含“xxx:”
- [ ] lrc和字幕的转换
- [ ] 音频格式转换

## 安装
安装依赖模块 gradio 和 moviepy
```
pip install gradio
pip install moviepy

```

安装 [ffmpeg](https://ffmpeg.org/)
（注意Windows用户需要把ffmpeg添加到环境变量中）

## 使用
有两种使用方式：
1. 点击app.py，根据弹出的提示，在浏览器中输入类似 http://127.0.0.1:8090 的地址
![](webui.png)

2. 在命令行中输入类似`python main.py 其他参数`

```
usage: main.py [-h] [-n NAME] [-r REF_CONTEXT] [-c {0,1,2}] [-t TIME_THRESHOLD] [-v | --cut-video | --no-cut-video]
               [-rt | --raw-time | --no-raw-time]
               input video

Cut video to clips and shuffle them by ass file

positional arguments:
  input                 Input file path (ass format)
  video                 Input video path

optional arguments:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  suffix for output files
  -r REF_CONTEXT, --ref-context REF_CONTEXT
                        suffix for output files
  -c {0,1,2}, --remove-comment {0,1,2}
                        Level of remove comment
  -t TIME_THRESHOLD, --time-threshold TIME_THRESHOLD
                        time threshold for ass
  -v, --cut-video, --no-cut-video
                        output videos
  -rt, --raw-time, --no-raw-time
                        output ass file with raw time

```

## 工作流说明
1. 使用剪映对视频进行语音识别，并导出src字幕
2. 使用Aegisub对字幕内容进行速览和矫正
3. 在Aegisub中找到重点关注的内容并进行标注和调整；对非关注的内容快速删除，或者把字幕类型改为注释
4. 使用洋片箱对字幕使用原时间轴模式进行切分
5. 检查切分结果，是否有标注错误，并修改context，只保留本次需要使用的章节
6. 使用洋片箱，把context文件作为ref context参数，对字幕和视频进行切分
8. 把切分结果按照需要的顺序拖入剪映或者其他软件

