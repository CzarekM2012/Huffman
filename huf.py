"""
Collection of arguments passed by user and calling encoding with huffman algorithm
"""
import argparse
from itertools import zip_longest
from pathlib import Path

from src.adaptiveHuffman import encode as adaptive_encode
from src.basicHuffman import encode as basic_encode

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

    parser.add_argument(
        "-f",
        "--files",
        metavar="FILE",
        nargs="+",
        type=Path,
        required=True,
        help="Paths to files to encode. Required",
    )
    parser.add_argument(
        "-d",
        "--destinations",
        metavar="DEST",
        nargs="+",
        type=Path,
        default=[],
        help="Paths where encoded files should be saved. Last extensions will be ignored. If \
            omitted encoded files will be saved next to originals.",
    )

    parser.add_argument(
        "-t",
        "--type",
        choices=TYPE_CHOICES,
        default=TYPE_CHOICES[0],
        help="Choose which type of the algorithm will be used",
    )

    def positive_int(text: str):
        val = int(text)
        if val <= 0:
            raise argparse.ArgumentTypeError(f"{val} is not a valid value for positive integer")
        return val

    parser.add_argument(
        "-s",
        "--symbol_size",
        type=positive_int,
        default=1,
        help="Size of symbols that will be encoded in bytes. Needs to be a positive number",
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
    file: Path
    destination: Path | None
    for file, destination in zip_longest(args.files, args.destinations):
        if not file.is_file():
            if args.is_verbose:
                print(f"Path {file} is not a file or doesn't exist. It has been skipped.")
            continue
        if destination is None:
            if args.is_verbose:
                print(
                    (
                        f"Destination for file {file} was not provided. Encoded file will be "
                        "saved in the same directory as the original."
                    )
                )
            destination = file
        if not destination.parent.is_dir():
            if args.is_verbose:
                print(
                    (
                        f"Directory {destination.parent} does not exist. Destination for file "
                        f"{file} will be ignored. Encoded file will saved in the same directory "
                        "as the original."
                    )
                )
            destination = file
        destination = destination.with_suffix(".huf")  # replace extension for new file
        if args.type == TYPE_CHOICES[0]:  # basic Huffman
            basic_encode(file, destination, args.symbol_size)
        elif args.type == TYPE_CHOICES[1]:
            adaptive_encode(file, destination)
        else:
            print("Unkown algorithm type option")
