from pathlib import Path
from math import ceil
from bitarray import bitarray
from bitarray.util import int2ba
from src.HuffmanTree import HuffmanTree
import os

ADAPTIVE_HUFFMAN = 1


def encode(src: Path, dst: Path):
    tree = HuffmanTree()
    encoded = bitarray()
    file_size = os.path.getsize(src)
    # print("src size is :", file_size, "bytes")
    with open(dst, "wb") as dst_file:
        encoding = bitarray()
        for character in src.suffix:
            encoding += tree.encode(character.encode())
        # print("encoded suffix")
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
    dst_size = os.path.getsize(dst)
    # print("dst size is :", dst_size, "bytes")


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
        content_chunk, is_eof = tree.decode(ext_encoding)
        # print("decoded suffix", content_chunk)
        ext = content_chunk.tobytes()
        dst = src.with_suffix(ext.decode())

        # rest = bitarray()
        with open(dst, "wb") as dst_file:
            # print("tell", file.tell())
            while (chunk := file.read(2**10)) != b"":
                # print("rest: ", rest)
                encoded_chunk = bitarray()
                encoded_chunk.frombytes(chunk)
                # print("rest + encoding: ", rest + encoded_chunk)
                # print("encoded_chunk", encoded_chunk)
                content_chunk, is_eof = tree.decode(encoded_chunk)
                # print(content_chunk, bits_read, is_eof)
                # print("bits_read: ", bits_read)
                dst_file.write(content_chunk.tobytes())
                # rest = encoded_chunk[bits_read:]
                # tree.print()
                if is_eof:
                    print("got eof")
                    break


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
