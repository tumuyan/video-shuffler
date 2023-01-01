import argparse
import cut
import merge


modes = ["cut", "merge", "mergelrc", "lrc"]
formats = cut.video_suffixs + cut.audio_suffixs

def main():
    parser = argparse.ArgumentParser(
        description="Cut video to clips and shuffle them by ass file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-m",
        "--mode", help="mode",
        choices=modes,
        default="cut"
    )

    parser.add_argument("input", type=str,
                        help="Input file path (ass format)")
    parser.add_argument("-n", "--name", type=str, default="",
                        help="prefix for output files")
    parser.add_argument("-r", "--ref-content", type=str,
                        default="", help="ref content file or str")

    parser.add_argument("-i", "--input-video", type=str,
                        default="", help="Input video path")

    parser.add_argument(
        "-v",
        "--cut-video",
        help="output videos",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-a",
        "--cut-audio",
        help="output audio ( --cut-audio will override --cut-video )",
        action=argparse.BooleanOptionalAction,
    )

    parser.add_argument(
        "-c",
        "--remove-comment", help="Level of remove comment",
        choices=["0", "1", "2"],
        default="1"
    )

    parser.add_argument(
        "-b",
        "--skip-blank-chapter-name", help="Not output chapters without chapter name",
        action=argparse.BooleanOptionalAction,
    )

    parser.add_argument(
        "-t",
        "--time-threshold", help="time threshold for ass",
        type=int,
        default=10
    )

    parser.add_argument(
        "-rt",
        "--raw-time",
        help="output ass file with raw time",
        action=argparse.BooleanOptionalAction,
    )

    parser.add_argument(
        "-f",
        "--format",
        help="format of output media file",
        choices=formats,
        default=formats[0]
    )

    args = parser.parse_args()

    input_ = args.input.lower()
    cut_media = args.cut_video or args.cut_audio

    if (args.mode == "lrc"):
        merge.asslist2lrc(args.input)
        return

    if (input_.endswith(".txt")):
        if (args.mode == "merge"):
            merge.merge_videos(args.input)
        elif (args.mode == "mergelrc"):
            merge.merge_videos(args.input, True)
        return

    if (input_.endswith(".ass")):
        ass_obj = cut.Ass(args.input, args.input_video,
                          args.remove_comment, args.time_threshold)
        if args.cut_audio:
            if args.format in cut.video_suffixs:
                args.format = cut.audio_suffixs[0]
            return ass_obj.split(args.name, args.raw_time, cut_media, args.ref_content,  args.format, args.skip_blank_chapter_name)
        return ass_obj.split(args.name, args.raw_time, cut_media, args.ref_content, args.format, args.skip_blank_chapter_name)

    elif input_.endswith(".srt"):
        print("Error: input srt file, need ass file")
    else:
        print("To be continued")


if __name__ == "__main__":
    main()
