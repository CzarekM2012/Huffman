from collections import defaultdict
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

from utility import read_n_bytes
from src.basicHuffman import encode as basic_encode
from src.adaptiveHuffman import encode as adaptive_encode
from src.basicHuffman import decode as basic_decode, BASIC_HUFFMAN
from src.adaptiveHuffman import decode as adaptive_decode, ADAPTIVE_HUFFMAN


def calculate_entropy(symbols: dict) -> float:
    vals = symbols.values()
    all_symbols = sum(symbols.values())
    entropy = 0
    for val in vals:
        entropy += val/all_symbols * np.log2(val/all_symbols)
    return -entropy


def count_symbols(filepath: Path, block_size: int = 1) -> dict:
    symbols = defaultdict(int)
    for block in read_n_bytes(filepath=filepath, n=block_size):
        symbols[block] += 1
    return symbols


def measure_time_encode_basic(file_target: Path, file_destination: Path) -> float:
    time = 0
    for _ in range(5):
        time_start = datetime.now()
        basic_encode(filepath=Path(file_target),
                     new_filepath=Path(file_destination),
                     symbol_size=1)
        time_end = datetime.now()
        time += (time_end-time_start).total_seconds()
    return time / 5


def measure_time_decode_basic(file_target: Path, file_destination: Path) -> float:
    time = 0
    for _ in range(5):
        time_start = datetime.now()
        basic_decode(filepath=Path(file_target),
                     destination=Path(file_destination))
        time_end = datetime.now()
        time += (time_end-time_start).total_seconds()
    return time / 5


def measure_time_encode_adaptive(file_target: Path, file_destination: Path) -> float:
    time = 0
    for _ in range(5):
        time_start = datetime.now()
        adaptive_encode(src=Path(file_target),
                        dst=Path(file_destination))
        time_end = datetime.now()
        time += (time_end-time_start).total_seconds()
    return time / 5


def measure_time_decode_adaptive(file_target: Path, file_destination: Path) -> float:
    time = 0
    for _ in range(5):
        time_start = datetime.now()
        adaptive_decode(src=Path(file_target),
                        dst=Path(file_destination))
        time_end = datetime.now()
        time += (time_end-time_start).total_seconds()
    return time / 5


def calculate_bitrate():
    pass


if __name__ == "__main__":
    filenames = []
    times_encode_basic = []
    times_encode_adaptive = []
    times_decode_basic = []
    times_decode_adaptive = []

    entropy_1B = []
    entropy_2B = []
    entropy_3B = []

    directory = 'data'
    files = Path(directory).glob('*.pgm')
    for file in files:
        print(file.name)
        filenames.append(file.name)
        # times_encode_basic.append(measure_time_encode_basic(file_target=file,
        #                           file_destination=f'results/encoded/{file.name}'))
        # times_decode_basic.append(measure_time_decode_basic(file_target=f'results/encoded/{file.name}',
        #                           file_destination=f'results/decoded/{file.name}'))
        times_encode_adaptive.append(measure_time_encode_adaptive(file_target=file,
                                     file_destination=f'results/encoded/{file.name}'))
        times_decode_adaptive.append(measure_time_decode_adaptive(file_target=f'results/encoded/{file.name}',
                                     file_destination=f'results/decoded/{file.name}'))

        entropy_1B.append(calculate_entropy(count_symbols(file, 1)))
        entropy_2B.append(calculate_entropy(count_symbols(file, 2)))
        entropy_3B.append(calculate_entropy(count_symbols(file, 3)))

    times_data = {"Filename": filenames,
                  "Encode adaptive [s]": times_encode_adaptive,
                  "Decode adaptive [s]": times_decode_adaptive}
    times = pd.DataFrame(times_data)

    entropy_data = {"Filename": filenames,
                    "Entropy 1B": entropy_1B,
                    "Entropy 2B": entropy_2B,
                    "Entropy 3B": entropy_3B}
    entr = pd.DataFrame(entropy_data)

    with pd.ExcelWriter(path="Huffman_results.xlsx", engine='xlsxwriter') as writer:
        entr.to_excel(excel_writer=writer, sheet_name="entropy", index=False)
        times.to_excel(excel_writer=writer, sheet_name="times", index=False)
