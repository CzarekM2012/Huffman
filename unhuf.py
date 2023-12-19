"""
Collection arguments passed by user and calling decoding files encoded with huffman algorithm
"""
import argparse
from pathlib import Path
from types import SimpleNamespace
from itertools import zip_longest
from bitarray.util import ba2int
from src.basicHuffman import decode as basic_decode, BASIC_HUFFMAN, get_n_bits
from src.adaptiveHuffman import decode as adaptive_decode, ADAPTIVE_HUFFMAN


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

    parser.add_argument(
        "-f",
        "--files",
        metavar="FILE",
        nargs="+",
        type=Path,
        required=True,
        help="Paths to files to decode. Required",
    )
    parser.add_argument(
        "-d",
        "--destinations",
        metavar="DEST",
        nargs="+",
        type=Path,
        default=[],
        help="Paths where decoded files should be saved. Last extensions will be ignored. If \
            omitted decoded files will be saved next to originals.",
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


def decode(src: Path, dst: Path):
    # Can't use constants directly in match-case because they would be always matching
    identifiers = SimpleNamespace()
    identifiers.basic_huffman = BASIC_HUFFMAN
    identifiers.adaptive_huffman = ADAPTIVE_HUFFMAN

    algorithm_identifier = None
    with open(src, "rb") as reader:
        algorithm_identifier = ba2int(get_n_bits(reader.read(1), 0, 1))
    match algorithm_identifier:
        case identifiers.basic_huffman:
            basic_decode(src, dst)
        case identifiers.adaptive_huffman:
            adaptive_decode(src, dst)
        case _:
            print(f"{src} was encoded using unknown type of algorithm")


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
        decode(file, destination)
