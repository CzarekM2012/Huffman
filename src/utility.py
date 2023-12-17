from pathlib import Path
from bitarray import bitarray


def read_chunks(filepath: Path, chunk_size: int = 2**10):
    with open(filepath, "rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            yield chunk


def read_bytes(filepath: Path, chunk_size: int = 2**10):
    """
    Reads specified byte file in chunks and iterates over them byte by byte

    Args:
        filepath (Path): path to a file
        chunk_size (int, optional): size of chunks read from the file. Defaults to 2**10 (1kB).

    Yields:
        bytes: a single byte read from file
    """
    for chunk in read_chunks(filepath, chunk_size):
        for i in range(len(chunk)):
            # extraction with range doesn't convert to int
            yield chunk[i : i + 1]


def get_n_bits(data: bytes, index: int, n: int) -> bitarray:
    bits = bitarray()
    bits.frombytes(data)
    if index >= len(bits):
        raise ValueError("Index points behind the last bit od data")
    if index + n > len(bits):
        raise ValueError("Given n reaches behind the last bit of data")
    return bits[index : index + n]
