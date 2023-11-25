"""
Collection arguments passed by user and calling decoding files encoded with huffman algorithm
"""
import argparse
import pathlib


def get_args() -> argparse.Namespace:
    """
    Instantiate argument parser and parse execution arguments

    :return: Namespace containing parsed execution arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Decode files encoded using Huffmann algorithm",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("files", metavar="FILE", nargs="+", type=pathlib.Path)

    parser.add_argument(
        "-v",
        "--verbose",
        dest="is_verbose",
        action="store_true",
        default=False,
        help="Show more details about execution",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    for file in args.files:
        if not file.is_file():
            if args.is_verbose:
                print(f"Path {file} is not a file or doesn't exist. It has been skipped.")
            continue
        # recognize encoding algorithm type
        # recognize original extension
        # new_file = file.with_suffix(original_extension)
        # decode(file, new_file)
        print("Decoding has not been implemented yet")
