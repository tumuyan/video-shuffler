import argparse
import cut

def main():
    parser = argparse.ArgumentParser(
        description="Cut video to clips and shuffle them by ass file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("input", type=str,  help="Input file path (ass or txt)")
    parser.add_argument("video", type=str,  help="Input video path")
    parser.add_argument("name", type=str,  help=" suffix for output files")
    
    parser.add_argument(
        "-c",
        "--remove-comment", help="Level of remove comment",
        choices=["0", "1", "2"],
        default="1"
    )
    
    parser.add_argument(
        "-t",
        "--time-threshold", help="time threshold for ass",
        type=int,
        default=10
    )

    parser.add_argument(
        "-v",
        "--cut-video",
        help="output videos",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "-r",
        "--raw-time",
        help="output ass file with raw time",
        action=argparse.BooleanOptionalAction,
    )


    args = parser.parse_args()

    input_ = args.input.lower()
    if(input_.endswith(".ass")):
        ass_obj = cut.Ass(args.input, args.video, args.remove_comment,args.time_threshold)
        return ass_obj.split(args.name, args.raw_time,args.cut_video)

    else:
        print("To be continued")

if __name__ == "__main__":
    main()
