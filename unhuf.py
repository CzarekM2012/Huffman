"""
Collection arguments passed by user and calling decoding files encoded with huffman algorithm
"""
import argparse
from pathlib import Path
from types import SimpleNamespace
from bitarray.util import ba2int
from src.basicHuffman import decode as basic_decode, BASIC_HUFFMAN, get_n_bits
from src.adaptiveHuffman import decode as adaptive_decode, ADAPTIVE_HUFFMAN

TYPE_CHOICES = ["basic", "adaptive"]


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

    parser.add_argument("files", metavar="FILE", nargs="+", type=Path)

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


def decode(filepath: Path):
    # Can't use constants directly in match-case because they would be always matching
    identifiers = SimpleNamespace()
    identifiers.basic_huffman = BASIC_HUFFMAN
    identifiers.adaptive_huffman = ADAPTIVE_HUFFMAN

    algorithm_identifier = None
    with open(filepath, "rb") as reader:
        algorithm_identifier = ba2int(get_n_bits(reader.read(1), 0, 1))
    match algorithm_identifier:
        case identifiers.basic_huffman:
            basic_decode(filepath)
        case identifiers.adaptive_huffman:
            adaptive_decode(filepath)
        case _:
            print(f"{filepath} was encoded using unknown type of algorithm")


if __name__ == "__main__":
    args = get_args()
    for file in args.files:
        if not file.is_file():
            if args.is_verbose:
                print(
                    f"Path {file} is not a file or doesn't exist. It has been skipped.")
            continue
        decode(file)
