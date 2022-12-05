import gradio as gr
import cut

mode_remove_comment = ["0 不删除", "1 保留章节信息", "2 不保留"]


def get_ass_obj(ass, video, remove_comment, time_threshold):
    print(ass)
    ass_path = ""

    if ass:
        ass_path = ass.name
    if not video:
        video = ""

    return cut.Ass(ass_path, video, mode_remove_comment.index(remove_comment), time_threshold)


def fn_cut_ass1(ass, video,  remove_comment, time_threshold, name):
    ass_obj = get_ass_obj(ass, video, remove_comment, time_threshold)
    return ass_obj.split(name, True, False)


def fn_cut_ass2(ass, video,  remove_comment, time_threshold, name):
    ass_obj = get_ass_obj(ass, video, remove_comment, time_threshold)
    return ass_obj.split(name, False, False)


def fn_cut_video(ass, video,  remove_comment, time_threshold, name):
    ass_obj = get_ass_obj(ass, video, remove_comment, time_threshold)
    return ass_obj.split(name, False, True)


app = gr.Blocks()
with app:
    tmp = gr.Markdown("")
    with gr.Tabs():
        with gr.TabItem("Cut by Ass"):

            with gr.Row():
                with gr.Column():
                    ass = gr.File(label="input ass file")
                    remove_comment = gr.Radio(
                        mode_remove_comment, value=mode_remove_comment[1], label="从字幕中删除注释")
                    time_threshold = gr.Slider(
                        minimum=0, maximum=60, step=0.01, value=10, label="分离相邻字幕的时间阈值")
                    name = gr.Textbox(label="分割后的文件名前缀")

                    with gr.Row():
                        cut_ass1 = gr.Button("只分割字幕(原时间轴)")
                        cut_ass2 = gr.Button("只分割字幕(新时间轴)")
                        cut_video = gr.Button("分割字幕和视频")

                with gr.Column():
                    video = gr.Video(label="input viedo")
                    files = gr.File(label="Files")
                    output = gr.TextArea(label="output")

            cut_ass1.click(fn=fn_cut_ass1, inputs=[
                           ass, video,  remove_comment, time_threshold, name], outputs=[output, files])
            cut_ass2.click(fn=fn_cut_ass2, inputs=[
                           ass, video,  remove_comment, time_threshold, name], outputs=[output, files])
            cut_video.click(fn=fn_cut_video, inputs=[
                            ass, video,  remove_comment, time_threshold, name], outputs=[output, files])

    app.launch()
