"""
Collection arguments passed by user and calling encoding with huffman algorithm
"""
import argparse
import pathlib

TYPE_CHOICES = ["basic", "adaptive"]


def get_args() -> argparse.Namespace:
    """
    Instantiate argument parser and parse execution arguments

    :return: Namespace containing parsed execution arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Encode files using Huffmann algorithm",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("files", metavar="FILE", nargs="+", type=pathlib.Path)

    parser.add_argument(
        "-t",
        "--type",
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES[0],
        help="Choose which type of the algorithm will be used",
    )

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
        new_file = file.with_suffix(".huf")  # replace extension for new file
        if args.type == TYPE_CHOICES[0]:  # basic Huffman
            # basic_encode(file, new_file)
            print("Encoding with basic Huffman algorithm has not been implemented yet")
        else:  # adaptive Huffman
            # adaptive_encode(file, new_file)
            print("Encoding with adaptive Huffman algorithm has not been implemented yet")
