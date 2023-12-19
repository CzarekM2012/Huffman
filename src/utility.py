from pathlib import Path
from bitarray import bitarray


def read_chunks(filepath: Path, chunk_size: int = 2**10):
    with open(filepath, "rb") as file:
        for chunk in iter(lambda: file.read(chunk_size), b""):
            yield chunk


def read_n_bytes(filepath: Path, n: int = 1, chunk_size: int = 2**10):
    """
    Reads specified byte file in chunks and iterates over them in n bytes sized blocks

    Args:
        filepath (Path): path to a file
        chunk_size (int, optional): size of chunks read from the file. Defaults to 2**10 (1kB).
        n (int, optional): number of bytes per block. Defaults to 1.

    Yields:
        bytes: A single block of n bytes read from file. The last block will be shorter if the size
        of file is not divisible by n
    """
    last_block = bytes()
    for chunk in read_chunks(filepath, chunk_size):
        cat_chunks = last_block + chunk
        last_block = bytes()
        for block in subsequences(cat_chunks, n):
            if len(block) < n:
                last_block = block
                break
            yield block
    if len(last_block) > 0:
        yield last_block


def get_n_bits(data: bytes, index: int, n: int) -> bitarray:
    bits = bitarray()
    bits.frombytes(data)
    if index >= len(bits):
        raise ValueError("Index points behind the last bit od data")
    if index + n > len(bits):
        raise ValueError("Given n reaches behind the last bit of data")
    return bits[index : index + n]


def subsequences(sequence, length: int):
    """
    Iterates over sequence with its subsequences of given length

    Args:
        sequence: sequence to iterate over
        length (int): length of subsequences

    Yields:
        Subsequences of given length consisting of next elements of `sequence`. Last subsequence
        will be shorter if length of sequence is not divisible by `length`
    """
    while length < len(sequence):
        yield sequence[:length]
        sequence = sequence[length:]
    yield sequence
