# Video Shuffler | 洋片箱
cut video to clips and shuffle them by ass file。  
用ass字母文件切割视频，并重组输出。

## 缘起
2022年9月，我在做Tacotron2的语音合成模型的训练。
在准备数据集的时候，做了一个简单的用ass字幕切割音频文件的工具。
工作流程非常顺畅，可以通过调整字幕时间控制剪辑位置，可以删除字幕取消一条内容，可以合并多行字幕来合并音频文件
后来我想，如果用这个基础上切割视频并重新排序，是不是就可以方便的剪辑二刀流或者三剪一视频了呢？
但是一直没有动手。

然后我在11月看到李沐老师的 https://github.com/mli/autocut/ ，我们理念相近但是又不完全相合。
因此开始自己制作工具。

洋片箱的命名来自游戏恋爱绮谭，一种现实有原型的怪异，只要更改照片的顺序就能够改变事实。
