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

在制作的过程中，又逐步改变了想法，使用markdown文件无法做到视频片段的精确预览，我要做的就是使用字幕文件帮助剪辑工作。

洋片箱的命名来自游戏恋爱绮谭，一种现实有原型的怪异，只要更改照片的顺序就能够改变事实。


## 计划抄什么
虽然看上去有点缝合怪，但是就要都做进去。
- [x] 使用ass字幕切割视频为多个片段，同时输出切分的字幕和切分章节文件名列表（txt文件）
- [ ] 使用txt文件控制，合并多个视频和字幕为一个，同时输出合并字幕
- [x] 在兼容ass格式的基础上，对字幕的信息做扩展
- [x] 使用gradio制作UI
- [ ] 自动识别字幕中每句分别属于哪个角色
- [ ] 分离bgm和人声，并切分为定长音频，以便语音识别
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
2. 在命令行中输入类似`python main.py 其他参数`

```

positional arguments:
  input                 Input file path (ass or txt)
  video                 Input video path
  name                  suffix for output files

optional arguments:
  -h, --help            show this help message and exit
  -c {0,1,2}, --remove-comment {0,1,2}
                        Level of remove comment
  -t TIME_THRESHOLD, --time-threshold TIME_THRESHOLD
                        time threshold for ass
  -v, --cut-video, --no-cut-video
                        output videos
  -r, --raw-time, --no-raw-time
                        output ass file with raw time

```