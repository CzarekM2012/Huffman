from collections import defaultdict
from io import BytesIO
from math import ceil
from pathlib import Path

import numpy as np
from bitarray import bitarray
from bitarray.util import ba2int, int2ba

from src.node import ChildSide, Node
from src.utility import bytes2ba, get_n_bits, read_n_bytes, subsequences

#   encoded file structure:
#   header: 1 byte: 1 bit to specify algorithm, 3 bits to specify number of padding bits at the end of the file (x), rest is padding 0s
#           4 bytes to specify how many bytes are taken by symbol counts (n),
#           1 byte to specify how many bits are taken by encoded extension (m)
#   symbol counts: n bytes
#   encoded extension: ceil(m/8) bytes
#   encoded contents: until EOF - x


BASIC_HUFFMAN = 0


def count_symbols(filepath: Path, symbol_size: int = 1):
    """
    Counts symbols in given file

    Args:
        filepath (Path): File to count symbols in
        symbol_size (int, optional): Desired size of symbol in bytes. Defaults to 1.

    Returns:
        NDArray: Numpy array with columns `symbol` and `count`. `Symbol` contains arrays of bytes
        of length equal `symbol_size` found in file at `filepath`, `count` - number of times
        corresponding symbols appears in that file
    """
    counts = defaultdict[bytes, int](int)

    for symbol in subsequences(filepath.suffix.encode(), symbol_size):
        if len(symbol) < symbol_size:
            symbol = symbol.ljust(symbol_size, b"\x00")
        counts[symbol] += 1
    for symbol in read_n_bytes(filepath, symbol_size):
        counts[symbol] += 1

    def dict_to_nparray():
        max_count = max(counts.values())
        count_dtype = np.min_scalar_type(max_count)
        array = np.array(
            list(counts.items()),
            dtype=[("symbol", f"V{symbol_size}"), ("count", count_dtype)],
        )
        return array

    array = dict_to_nparray()
    return array


def np_serialize(array: np.ndarray):
    serialization_proxy = BytesIO()
    np.save(serialization_proxy, array)
    return serialization_proxy.getvalue()


def np_deserialize(serialized: bytes):
    deserialization_proxy = BytesIO(serialized)
    return np.load(deserialization_proxy)


def counts_to_nodes(symbols_counts: np.ndarray):
    nodes: list[Node] = []
    for symbol, count in symbols_counts:
        symbol = bytes(symbol)
        weight = int(count)
        nodes.append(Node(symbol=symbol, weight=weight))
    return nodes


def build_tree(nodes: list[Node]) -> Node:
    """
    Builds encoding tree for basic Huffman algorithm

    Args:
        nodes (list[Node]): List of leaf nodes of the newly constructed tree

    Returns:
        Node: Root node of the tree
    """
    nodes.sort(key=lambda node: node.weight)
    while len(nodes) > 1:
        left_child = nodes.pop(0)
        right_child = nodes.pop(0)
        new_node = Node(left_child.weight + right_child.weight)
        new_node.set_child(left_child, ChildSide.LEFT)
        new_node.set_child(right_child, ChildSide.RIGHT)

        inserted = False
        for i, node in enumerate(nodes):
            if new_node.weight < node.weight:
                nodes.insert(i, new_node)
                inserted = True
                break
        if not inserted:
            nodes.append(new_node)
    return nodes[0]


def _encode_extension(filepath: Path, encodings: dict[bytes, bitarray], symbol_size: int):
    code = bitarray()
    for symbol in subsequences(filepath.suffix.encode(), symbol_size):
        if len(symbol) < symbol_size:
            symbol = symbol.ljust(symbol_size, b"\x00")
        code += encodings[symbol]
    return (code.tobytes(), len(code))


def _encode_contents(
    filepath: Path, encodings: dict[bytes, bitarray], symbol_size: int, chunk_size: int = 2**10
):
    """
    Encode contents of file in chunks.

    Args:
        filepath (Path): Path to the file to encode
        encodings (dict[bytes, bitarray]): Dict of symbol: symbol_encoding pairs
        chunk_size (int, optional): Number of bytes to encode in every chunk. Defaults to 2**10 (1kB).

    Yields:
        tuple[bytes, int]: Pair of encoded chunk of data and number of bits in the chunk that
        encode original information. Number of bits is equal to length of the chunk multiplied
        by 8 for all chunks except for the last one due to it being padded to full bytes.
    """
    code = bitarray()
    for symbol in read_n_bytes(filepath, symbol_size, chunk_size):
        code += encodings[symbol]
        if len(code) > chunk_size * 8:
            yield code[: chunk_size * 8].tobytes(), chunk_size * 8
            code = code[chunk_size * 8 :]
    yield code.tobytes(), len(code)


def encode(filepath: Path, new_filepath: Path, symbol_size: int = 1):
    symbols_counts = count_symbols(filepath, symbol_size)

    leaves = counts_to_nodes(symbols_counts)

    encoding_tree = build_tree(leaves)
    encodings = encoding_tree.get_codings()

    serialized_counts = np_serialize(symbols_counts)

    extension, extension_len = _encode_extension(filepath, encodings, symbol_size)

    header_no_1st_byte = len(serialized_counts).to_bytes(length=4) + extension_len.to_bytes()

    with open(new_filepath, "wb") as file:
        file.seek(6)
        file.write(serialized_counts + extension)
        padding_bits = 0
        for chunk, code_len in _encode_contents(filepath, encodings, symbol_size):
            file.write(chunk)
            padding_bits = len(chunk) * 8 - code_len
        file.seek(0)
        header_1st_byte = (bitarray([BASIC_HUFFMAN]) + int2ba(padding_bits, 3)).tobytes()
        file.write(header_1st_byte + header_no_1st_byte)


def _decode_codeblock(codeblock: bitarray, decoding_tree: Node):
    """
    Decodes given block of code

    Args:
        codeblock (bitarray): A block of code to be decoded
        decoding_tree (Node): Tree of codes to be used in decoding

    Returns:
        tuple[bytes, bitarray]: Decoded symbols and remainder at the end of the codeblock that
        could not be mapped to any symbol
    """
    decoded = bytes()
    code = codeblock
    while True:
        node: Node = decoding_tree
        i = 0
        while not node.is_leaf() and i < len(code):
            # Presence of children is examined while checking if node is a leaf
            node = node.children[code[i]]  # type: ignore
            i += 1
        if not node.is_leaf():
            break
        # Symbol is inspected while checking if node is a leaf
        decoded += node.symbol  # type: ignore
        code = code[i:]
    return decoded, code


def decode(filepath: Path, destination: Path):
    with open(filepath, "rb") as reader:
        header = reader.read(6)
        end_padding = ba2int(get_n_bits(header[0:1], 1, 3))
        counts_len = int.from_bytes(header[1:5])
        extension_len = header[-1]

        chunk = reader.read(counts_len + ceil(extension_len / 8))

        symbols_counts = np_deserialize(chunk[:counts_len])

        leaves = counts_to_nodes(symbols_counts)
        decoding_tree = build_tree(leaves)

        encoded_extension = bytes2ba(chunk[counts_len:])
        encoded_extension = encoded_extension[:extension_len]
        extension, _ = _decode_codeblock(encoded_extension, decoding_tree)
        while extension[-1:] == b"\x00":
            extension = extension[:-1]

        destination = destination.with_suffix(extension.decode())
        with open(destination, "wb") as writer:
            remainder = bitarray()
            encoded = bitarray()
            decoded = bytes()
            # Iterator will stop when b"" is read (EOF)
            for chunk in iter(lambda: reader.read(2**10), b""):
                decoded, remainder = _decode_codeblock(encoded, decoding_tree)
                writer.write(decoded)
                # Operations up to this moment were executed data from chunk from previous iteration
                code = bitarray()
                code.frombytes(chunk)
                encoded = remainder + code
            # Encoded here is the last not-empty chunk from reader
            if end_padding > 0:
                encoded = encoded[:-end_padding]
            decoded, _ = _decode_codeblock(encoded, decoding_tree)
            while decoded[-1:] == b"\x00":
                decoded = decoded[:-1]
            writer.write(decoded)
