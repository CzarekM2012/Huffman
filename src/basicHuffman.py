from math import ceil
from pathlib import Path
import pickle
from bitarray import bitarray
from bitarray.util import int2ba, ba2int
from .node import Node, LEFT_CHILD, RIGHT_CHILD

#   encoded file structure:
#   header: 1 byte: 1 bit to specify algorithm, 3 bits to specify number of padding bits at the end of the file (x), rest is padding 0s
#           2 bytes to specify how many bytes are taken by symbol counts (n),
#           1 byte to specify how many bits are taken by encoded extension (m)
#   symbol counts: n bytes
#   encoded extension: ceil(m/8) bytes
#   encoded contents: until EOF - x


BASIC_HUFFMAN = 0


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
            yield chunk[i : i + 1]  # extraction with range doesn't convert to int


def _count_symbols(filepath: Path) -> dict[bytes, int]:
    counts: dict[bytes, int] = {}

    def count_byte(byte: bytes):
        if byte in counts:
            counts[byte] += 1
        else:
            counts[byte] = 1

    for character in filepath.suffix:
        count_byte(character.encode())
    for byte in read_bytes(filepath):
        count_byte(byte)
    return counts


def _build_tree(nodes: list[Node]) -> Node:
    nodes.sort(key=lambda node: node.weight)
    while len(nodes) > 1:
        left_child = nodes.pop(0)
        right_child = nodes.pop(0)
        new_node = Node(left_child.weight + right_child.weight)
        new_node.children[LEFT_CHILD] = left_child
        new_node.children[RIGHT_CHILD] = right_child
        left_child.side = LEFT_CHILD
        right_child.side = RIGHT_CHILD
        left_child.parent = new_node
        right_child.parent = new_node

        inserted = False
        for i, node in enumerate(nodes):
            if new_node.weight < node.weight:
                nodes.insert(i, new_node)
                inserted = True
                break
        if not inserted:
            nodes.append(new_node)
    return nodes[0]


def _encode_extension(filepath: Path, encodings: dict[bytes, bitarray]):
    code = bitarray()
    for character in filepath.suffix:
        code += encodings[character.encode()]
    return (code.tobytes(), len(code))


def _encode_contents(filepath: Path, encodings: dict[bytes, bitarray], chunk_size: int = 2**10):
    """
    Encode contents of file in chunks.

    Args:
        filepath (Path): Path to the file to encode
        encodings (dict[bytes, bitarray]): Dict of symbol: symbol_encoding pairs
        chunk_size (int, optional): Number of bytes to encode in every chunk. Defaults to 2**10 (1kB).

    Yields:
        tuple[bytes, int]: Pair of encoded chunk of data and number of bits in the chunk that
        encode original information. Number of bits is equal to length of the chunk multiplied
        by 8 for all chunks except for the last one.
    """
    code = bitarray()
    for byte in read_bytes(filepath):
        code += encodings[byte]
        if len(code) > chunk_size * 8:
            yield code[: chunk_size * 8].tobytes(), chunk_size * 8
            code = code[chunk_size * 8 :]
    yield code.tobytes(), len(code)


def encode(filepath: Path, new_filepath: Path):
    symbols_counts = _count_symbols(filepath)
    leaves = [Node(symbol=symbol, weight=count) for symbol, count in symbols_counts.items()]
    # Generates long bytes objects.
    # Custom encoding of symbol and weight only may significantly reduce overhead
    serialized_counts = pickle.dumps(symbols_counts)
    encoding_tree = _build_tree(leaves)
    encodings = encoding_tree.get_codings()

    extension, extension_len = _encode_extension(filepath, encodings)

    header_no_1st_byte = len(serialized_counts).to_bytes(length=2) + extension_len.to_bytes()

    with open(new_filepath, "wb") as file:
        file.seek(4)
        file.write(serialized_counts + extension)
        padding_bits = 0
        for chunk, code_len in _encode_contents(filepath, encodings):
            file.write(chunk)
            padding_bits = len(chunk) * 8 - code_len
        file.seek(0)
        header_1st_byte = (bitarray([BASIC_HUFFMAN]) + int2ba(padding_bits, 3)).tobytes()
        file.write(header_1st_byte + header_no_1st_byte)


def _decode_contents(contents: bitarray, decoding_tree: Node):
    decoded = bytes()
    code = contents
    temp = decoding_tree.get_codings()
    # needs to return remainder of code
    while True:
        node = decoding_tree
        i = 0
        while not all(child is None for child in node.children) and i < len(code):
            node = node.children[code[i]]
            i += 1
        if not all(child is None for child in node.children):
            break
        decoded += node.symbol
        code = code[i:]
    return decoded, code


def get_n_bits(data: bytes, index: int, n: int) -> bitarray:
    bits = bitarray()
    bits.frombytes(data)
    if index >= len(bits):
        raise ValueError("Index points behind the last bit od data")
    if index + n > len(bits):
        raise ValueError("Given n reaches behind the last bit of data")
    return bits[index : index + n]


def decode(filepath: Path):
    with open(filepath, "rb") as reader:
        header = reader.read(4)
        end_padding = ba2int(get_n_bits(header[0:1], 1, 3))
        counts_len = int.from_bytes(header[1:3])
        extension_len = header[-1]

        chunk = reader.read(counts_len + ceil(extension_len / 8))
        symbols_counts: dict[bytes, int] = pickle.loads(chunk[:counts_len])
        leaves = [Node(symbol=symbol, weight=count) for symbol, count in symbols_counts.items()]
        decoding_tree = _build_tree(leaves)

        encoded_extension = bitarray()
        encoded_extension.frombytes(chunk[counts_len:])
        encoded_extension = encoded_extension[:extension_len]
        extension, _ = _decode_contents(encoded_extension, decoding_tree)

        new_filepath = filepath.with_suffix(extension.decode())
        with open(new_filepath, "wb") as writer:
            remainder = bitarray()
            encoded = bitarray()
            decoded = bytes()
            # Iterator will stop when b"" is read (EOF)
            for chunk in iter(lambda: reader.read(2**10), b""):
                decoded, remainder = _decode_contents(encoded, decoding_tree)
                writer.write(decoded)
                # Operations up to this moment were executed data from chunk from previous iteration
                code = bitarray()
                code.frombytes(chunk)
                encoded = remainder + code
            # Encoded here is the last not-empty chunk from reader
            if end_padding > 0:
                encoded = encoded[:-end_padding]
            decoded, _ = _decode_contents(encoded, decoding_tree)
            writer.write(decoded)
