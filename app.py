import gradio as gr
import cut
import merge

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


def fn_cut_video1(ass, video,  remove_comment, time_threshold, name):
    ass_obj = get_ass_obj(ass, video, remove_comment, time_threshold)
    return ass_obj.split(name, False, True)


def fn_cut_video2(ass, video,  remove_comment, time_threshold, name, content):
    ass_obj = get_ass_obj(ass, video, remove_comment, time_threshold)
    return ass_obj.split(name, False, True, content)



def fn_ass2lrc(t2_input):
    if not t2_input:
        return [],""


    if (len(t2_input)>1):
        return [], "此模式只支持输入一个txt格式的文件列表"

    for input in t2_input:
        input_ = t2_input.name.toLower()
        if  input_.endswith(".txt"):
            merge.merge_videos(input.name,True)
            output = t2_input.name[0:-4] + ".lrc"
            return output, "\n".join(output)
        else:
            output = merge.ass2lrc(input.name)
            return output,output
    return [],""


def fn_ass2lrc2(t2_input):
    
    if not t2_input:
        return "",""
    inputs = []
    for input in t2_input:
        inputs.append(input.name)
    result = merge.asslist2lrc(inputs)
    return result,"\n".join(result)

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
                        cut_video1 = gr.Button("分割字幕和视频")

                with gr.Column():
                    video = gr.Video(label="input viedo")
                    files = gr.File(label="Files")
                    content = gr.TextArea(label="content")
                    cut_video2 = gr.Button("用目录分割字幕和视频")

            cut_ass1.click(fn=fn_cut_ass1, inputs=[
                           ass, video,  remove_comment, time_threshold, name], outputs=[content, files])
            cut_ass2.click(fn=fn_cut_ass2, inputs=[
                           ass, video,  remove_comment, time_threshold, name], outputs=[content, files])
            cut_video1.click(fn=fn_cut_video1, inputs=[
                ass, video,  remove_comment, time_threshold, name], outputs=[content, files])
            cut_video2.click(fn=fn_cut_video2, inputs=[
                ass, video,  remove_comment, time_threshold, name, content], outputs=[content, files])

        with gr.TabItem("Ass2Lrc"):

            with gr.Row():
                with gr.Column():
                    t2_input = gr.Files(label="Input ass file or ass filelist")
                    with gr.Row():
                        ass2lrc = gr.Button("Ass 2 Lrc")
                        ass2lrc2 = gr.Button("Ass 2 Lrcs")
                with gr.Column():
                    t2_output = gr.Files(label="Files")
                    t2_content = gr.TextArea(label="content")
                ass2lrc.click(fn=fn_ass2lrc, inputs=[ t2_input], outputs=[t2_output, t2_content])
                ass2lrc2.click(fn=fn_ass2lrc2, inputs=[ t2_input], outputs=[t2_output, t2_content])

    app.launch()
