from collections import defaultdict
from pathlib import Path
from datetime import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import imageio.v2 as imageio

from src.utility import read_n_bytes
from src.HuffmanTree import HuffmanTree
from src.basicHuffman import encode as basic_encode, decode as basic_decode, \
                             count_symbols, counts_to_nodes, build_tree
from src.adaptiveHuffman import encode as adaptive_encode, \
                                decode as adaptive_decode


def plot_histogram(file_name, file_path, save_path=None):
    plt.figure()
    image = imageio.imread(file_path)
    histogram, _ = np.histogram(image.flatten(), bins=256, range=(0, 256))
    plt.bar(np.arange(len(histogram)), histogram, color='gray', alpha=0.8)
    plt.title(f'Histogram {file_name}')
    plt.xlabel('Wartość')
    plt.ylabel('Częstość')
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def calculate_entropy(symbols: dict) -> float:
    vals = symbols.values()
    all_symbols = sum(symbols.values())
    entropy = 0
    for val in vals:
        entropy += val / all_symbols * np.log2(val / all_symbols)
    return -entropy


def local_count_symbols(filepath: Path, block_size: int = 1) -> dict:
    symbols = defaultdict(int)
    for block in read_n_bytes(filepath=filepath, n=block_size):
        symbols[block] += 1
    return symbols


def measure_time_encode_basic(file_target: Path, file_destination: Path
                              ) -> float:
    time = 0
    for _ in range(5):
        time_start = datetime.now()
        basic_encode(filepath=Path(file_target),
                     new_filepath=Path(file_destination),
                     symbol_size=1)
        time_end = datetime.now()
        time += (time_end - time_start).total_seconds()
    return time / 5


def measure_time_decode_basic(file_target: Path, file_destination: Path
                              ) -> float:
    time = 0
    for _ in range(5):
        time_start = datetime.now()
        basic_decode(filepath=Path(file_target),
                     destination=Path(file_destination))
        time_end = datetime.now()
        time += (time_end - time_start).total_seconds()
    return time / 5


def measure_time_encode_adaptive(file_target: Path, file_destination: Path
                                 ) -> float:
    time = 0
    for _ in range(5):
        time_start = datetime.now()
        adaptive_encode(src=Path(file_target),
                        dst=Path(file_destination))
        time_end = datetime.now()
        time += (time_end - time_start).total_seconds()
    return time / 5


def measure_time_decode_adaptive(file_target: Path, file_destination: Path
                                 ) -> float:
    time = 0
    for _ in range(5):
        time_start = datetime.now()
        adaptive_decode(src=Path(file_target),
                        dst=Path(file_destination))
        time_end = datetime.now()
        time += (time_end - time_start).total_seconds()
    return time / 5


def calculate_bitrate_basic(filepath: Path, symbol_size: int = 1
                            ) -> float:
    symbols_counts = count_symbols(filepath, symbol_size)
    leaves = counts_to_nodes(symbols_counts)
    encoding_tree = build_tree(leaves)
    encodings = encoding_tree.get_codings()
    symbols_counts = local_count_symbols(filepath)

    all_symbols = sum(symbols_counts.values())
    bitrate = 0
    for symbol in symbols_counts.keys():
        bitrate += len(encodings[symbol]) * (
            symbols_counts[symbol] / all_symbols)

    return bitrate


def calculate_bitrate_adaptive(filepath: Path) -> float:
    tree = HuffmanTree()
    for byte in read_n_bytes(filepath):
        tree.encode(byte)

    return tree.bitrate()


if __name__ == "__main__":
    filenames = []
    times_encode_basic = []
    times_encode_adaptive = []
    times_decode_basic = []
    times_decode_adaptive = []

    entropy_1B = []
    entropy_2B = []
    entropy_3B = []

    bitrate_basic = []
    bitrate_adaptive = []

    filesizes = []
    filesizes_basic = []
    filesizes_adaptive = []
    cr_basic = []
    cr_adaptive = []

    DATA_DIR = Path("data")
    RESULTS_DIR = Path("results")
    ENCODING_RESULTS = RESULTS_DIR.joinpath("encoded")
    DECODING_RESULTS = RESULTS_DIR.joinpath("decoded")
    HISTOGRAMS = RESULTS_DIR.joinpath("histograms")
    for directory in [RESULTS_DIR, ENCODING_RESULTS,
                      DECODING_RESULTS, HISTOGRAMS]:
        if not directory.is_dir():
            directory.mkdir()

    files = DATA_DIR.glob("*.pgm")
    for file in files:
        print(file.name)
        file_size = os.path.getsize(file)
        filenames.append(file.name)
        filesizes.append(file_size)
        bitrate_basic.append(calculate_bitrate_basic(file))
        bitrate_adaptive.append(calculate_bitrate_adaptive(file))
        plot_histogram(file.name, file,
                       save_path=HISTOGRAMS.joinpath(file.stem))

        times_encode_basic.append(
            measure_time_encode_basic(
                file_target=file,
                file_destination=ENCODING_RESULTS.joinpath(file.name)
            )
        )
        file_size_basic = os.path.getsize(ENCODING_RESULTS.joinpath(file.name))
        filesizes_basic.append(file_size_basic)
        cr_basic.append(file_size_basic / file_size)
        times_decode_basic.append(
            measure_time_decode_basic(
                file_target=ENCODING_RESULTS.joinpath(file.name),
                file_destination=DECODING_RESULTS.joinpath(file.name),
            )
        )
        times_encode_adaptive.append(
            measure_time_encode_adaptive(
                file_target=file,
                file_destination=ENCODING_RESULTS.joinpath(file.name)
            )
        )
        file_size_adaptive = os.path.getsize(
            ENCODING_RESULTS.joinpath(file.name))
        filesizes_adaptive.append(file_size_adaptive)
        cr_adaptive.append(file_size_adaptive / file_size)
        times_decode_adaptive.append(
            measure_time_decode_adaptive(
                file_target=ENCODING_RESULTS.joinpath(file.name),
                file_destination=DECODING_RESULTS.joinpath(file.name),
            )
        )

        entropy_1B.append(calculate_entropy(local_count_symbols(file, 1)))
        entropy_2B.append(calculate_entropy(local_count_symbols(file, 2)))
        entropy_3B.append(calculate_entropy(local_count_symbols(file, 3)))

    times_data = {
        "Filename": filenames,
        "Encode basic [s]": times_encode_basic,
        "Decode basic [s]": times_decode_basic,
        "Encode adaptive [s]": times_encode_adaptive,
        "Decode adaptive [s]": times_decode_adaptive,
    }
    times = pd.DataFrame(times_data)

    entropy_data = {
        "Filename": filenames,
        "Entropy 1B": entropy_1B,
        "Entropy 2B": entropy_2B,
        "Entropy 3B": entropy_3B,
    }
    entr = pd.DataFrame(entropy_data)

    bitrate_data = {
        "Filename": filenames,
        "Entropy": entropy_1B,
        "Bitrate basic": bitrate_basic,
        "Bitrate adaptive": bitrate_adaptive,
    }
    bitrate = pd.DataFrame(bitrate_data)

    cr_data = {
        "Filename": filenames,
        "File size [B]": filesizes,
        "Size basic [B]": filesizes_basic,
        "Size adaptive [B]": filesizes_adaptive,
        "Compression rate basic": cr_basic,
        "Compression rate adaptive": cr_adaptive,
    }
    cr = pd.DataFrame(cr_data)

    with pd.ExcelWriter(
        path=RESULTS_DIR.joinpath("Huffman_results.xlsx"), engine="xlsxwriter"
    ) as writer:
        entr.to_excel(excel_writer=writer, sheet_name="entropy", index=False)
        bitrate.to_excel(excel_writer=writer, sheet_name="bitrate",
                         index=False)
        times.to_excel(excel_writer=writer, sheet_name="times", index=False)
        cr.to_excel(excel_writer=writer, sheet_name="cr", index=False)
