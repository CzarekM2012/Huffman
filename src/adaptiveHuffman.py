from pathlib import Path
from bitarray import bitarray
from src.HuffmanTree import HuffmanTree
import os


def encode(src: Path, dst: Path):
    tree = HuffmanTree()
    encoded = bitarray()
    file_size = os.path.getsize(src)
    print("src size is :", file_size, "bytes")
    with open(dst, "wb") as dst_file:
        dst_file.seek(0, os.SEEK_END)
        print(dst_file.tell())
        dst_file.seek(0, 0)

        counter = 0
        for byte in read_bytes(src):
            counter += 1
            if (counter % 100 == 0):
                print(f"byte {counter} from {file_size}")
            e = tree.encode(byte)
            encoded += e

        encoded += tree.encode_eof()
        dst_file.write(encoded)
    dst_size = os.path.getsize(dst)
    print("dst size is :", dst_size, "bytes")

    #     ...
    # for byte in read_bytes(src):
    #     return tree.code(byte)
    # symbols_counts = _count_symbols(filepath)
    # leaves = [Node(symbol=symbol, weight=count)
    #           for symbol, count in symbols_counts.items()]
    #
    # serialized_counts = pickle.dumps(symbols_counts)
    # encoding_tree = _build_tree(leaves)
    # encodings = encoding_tree.get_codings()
    #
    # extension, extension_len = _encode_extension(filepath, encodings)
    #
    # header_no_1st_byte = len(serialized_counts).to_bytes(
    #     length=2) + extension_len.to_bytes()
    #
    # with open(new_filepath, "wb") as file:
    #     file.seek(4)
    #     file.write(serialized_counts + extension)
    #     padding_bits = 0
    #     for chunk, code_len in _encode_contents(filepath, encodings):
    #         file.write(chunk)
    #         padding_bits = len(chunk) * 8 - code_len
    #     file.seek(0)
    #     header_1st_byte = (
    #         bitarray([BASIC_HUFFMAN]) + int2ba(padding_bits, 3)).tobytes()
    #     file.write(header_1st_byte + header_no_1st_byte)

# 276616
# 262182


def decode(src: Path):
    tree = HuffmanTree()
    with open(src, "rb") as file:
        with open("decoded.png", "wb") as dst_file:
            encoded = bitarray()
            encoded.fromfile(file)
            decoded = tree.decode(encoded)
            dst_file.write(decoded)
    ...
    # with open(filepath, "rb") as reader:
    #     header = reader.read(4)
    #     end_padding = ba2int(get_n_bits(header[0:1], 1, 3))
    #     counts_len = int.from_bytes(header[1:3])
    #     extension_len = header[-1]
    #
    #     chunk = reader.read(counts_len + ceil(extension_len / 8))
    #     symbols_counts: dict[bytes, int] = pickle.loads(chunk[:counts_len])
    #     leaves = [Node(symbol=symbol, weight=count)
    #               for symbol, count in symbols_counts.items()]
    #     decoding_tree = _build_tree(leaves)
    #
    #     encoded_extension = bitarray()
    #     encoded_extension.frombytes(chunk[counts_len:])
    #     encoded_extension = encoded_extension[:extension_len]
    #     extension, _ = _decode_contents(encoded_extension, decoding_tree)
    #
    #     new_filepath = filepath.with_suffix(extension.decode())
    #     with open(new_filepath, "wb") as writer:
    #         remainder = bitarray()
    #         encoded = bitarray()
    #         decoded = bytes()
    #         # Iterator will stop when b"" is read (EOF)
    #         for chunk in iter(lambda: reader.read(2**10), b""):
    #             decoded, remainder = _decode_contents(encoded, decoding_tree)
    #             writer.write(decoded)
    #             # Operations up to this moment were executed data from chunk from previous iteration
    #             code = bitarray()
    #             code.frombytes(chunk)
    #             encoded = remainder + code
    #         # Encoded here is the last not-empty chunk from reader
    #         if end_padding > 0:
    #             encoded = encoded[:-end_padding]
    #         decoded, _ = _decode_contents(encoded, decoding_tree)
    #         writer.write(decoded)


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
