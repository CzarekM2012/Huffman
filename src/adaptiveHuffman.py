from pathlib import Path
from math import ceil
from bitarray import bitarray
from bitarray.util import int2ba, ba2int
from src.HuffmanTree import HuffmanTree

ADAPTIVE_HUFFMAN = 1

#   encoded file structure:
#   header: 1 byte: 1 bit to specify algorithm, 7 bits to specify how many bits are taken by encoded extension (n)
#   encoded extension: ceil(n/8) bytes
#   encoded contents: until EOF


def encode(src: Path, dst: Path):
    tree = HuffmanTree()
    encoded = bitarray()
    with open(dst, "wb") as dst_file:
        encoding = bitarray()
        for character in src.suffix:
            encoding += tree.encode(character.encode())
        header = bitarray([ADAPTIVE_HUFFMAN])
        header.extend(int2ba(len(encoding), 7))
        dst_file.write(header)
        dst_file.write(encoding)
        encoding.clear()

        for byte in read_bytes(src):
            encoded += tree.encode(byte)
            if len(encoded) >= 2**10:
                dst_file.write(encoded[:2**10])
                encoded = encoded[2**10:]

        encoded += tree.encode_eof()
        dst_file.write(encoded)


def decode(src: Path):
    tree = HuffmanTree()
    with open(src, "rb") as file:
        ext_len = int.from_bytes(file.read(1)) & 127
        ext_enc = file.read(ceil(ext_len / 8))
        ext_enc = bytes2ba(ext_enc)[:ext_len]
        ext_chunk, is_eof = tree.decode_chunk(ext_enc)
        ext = ext_chunk.tobytes()
        dst = src.with_suffix(ext.decode())

        with open(dst, "wb") as dst_file:
            while not is_eof and (chunk := file.read(2**10)) != b"":
                encoded_chunk = bitarray()
                encoded_chunk.frombytes(chunk)
                ext_chunk, is_eof = tree.decode_chunk(encoded_chunk)
                dst_file.write(ext_chunk.tobytes())


def bytes2ba(data):
    ba = bitarray()
    ba.frombytes(data)
    return ba


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
