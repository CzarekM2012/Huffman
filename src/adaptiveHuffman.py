from pathlib import Path
from math import ceil
from bitarray import bitarray
from bitarray.util import int2ba
from src.HuffmanTree import HuffmanTree

ADAPTIVE_HUFFMAN = 1


def encode(src: Path, dst: Path):
    tree = HuffmanTree()
    encoded = bitarray()
    with open(dst, "wb") as dst_file:
        encoding = bitarray()
        for character in src.suffix:
            encoding += tree.encode(character.encode())
        header = (bitarray([ADAPTIVE_HUFFMAN])).tobytes()
        zero = bitarray('0').tobytes()
        extention_len = int2ba(len(encoding), 8)
        full_header = header + zero + zero + extention_len
        dst_file.write(full_header)
        dst_file.write(encoding)
        encoding.clear()

        for byte in read_bytes(src):
            encoded += tree.encode(byte)

        encoded += tree.encode_eof()
        dst_file.write(encoded)


def decode(src: Path):
    tree = HuffmanTree()
    with open(src, "rb") as file:
        header = file.read(4)
        counts_len = int.from_bytes(header[1:3])
        extention_len = header[-1]
        chunk = file.read(counts_len + ceil(extention_len / 8))
        ext_encoding = bitarray()
        ext_encoding.frombytes(chunk)
        ext_encoding = ext_encoding[counts_len:counts_len + extention_len]
        content_chunk, is_eof = tree.decode_chunk(ext_encoding)
        ext = content_chunk.tobytes()
        dst = src.with_suffix(ext.decode())

        with open(dst, "wb") as dst_file:
            while not is_eof and (chunk := file.read(2**10)) != b"":
                encoded_chunk = bitarray()
                encoded_chunk.frombytes(chunk)
                content_chunk, is_eof = tree.decode_chunk(encoded_chunk)
                dst_file.write(content_chunk.tobytes())


def get_n_bits(data: bytes, index: int, n: int) -> bitarray:
    bits = bitarray()
    bits.frombytes(data)
    if index >= len(bits):
        raise ValueError("Index points behind the last bit od data")
    if index + n > len(bits):
        raise ValueError("Given n reaches behind the last bit of data")
    return bits[index: index + n]


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
            yield chunk[i: i + 1]


if __name__ == "__main__":
    my_test = "src/tests/files/obrazy_testowe/mytest.png"
    barbara = "src/tests/files/obrazy_testowe/barbara.pgm"

    encode(my_test, "test_output")
    decode("test_output")
