from typing import Union
from bitarray import bitarray
from src.node import Node, ChildSide


class HuffmanTree:
    buffer: bitarray
    decoding_node: Node

    def __init__(self):
        self.buffer = bitarray()
        self.NYT = Node()
        self.EOF = Node()
        self.nodes = [self.NYT]  # attribute
        self._add_new_leaf(self.EOF, None)
        self.working_node = self.nodes[-1]

    def encode_eof(self):
        n = self.EOF
        code = bitarray()
        while n.parent:
            code.append(n.side.value)
            n = n.parent
        code.reverse()
        return code

    def encode(self, symbol):
        i = self._find_symbol(symbol)
        n = self.NYT if i is None else self.nodes[i]
        code = bitarray()
        while n.parent:
            code.append(n.side.value)
            n = n.parent
        code.reverse()

        self._add(symbol)
        if i is None:
            code.frombytes(symbol)
        return code

    def decode_symbol(self, encoding: bitarray) -> tuple[Union[bytes, bitarray, None], int, bool]:
        """
        Decodes a single encoded symbol

        Args:
            encoding (bitarray): Array of bits containing the encoded symbol

        Returns:
            tuple[bytes | bitarray | None, int, bool]: Tuple containing: decoded symbol, number of bits used in decoding, value of EOF flag
        """
        cursor = 0
        while cursor != len(encoding):
            child = encoding[cursor]
            self.working_node = self.working_node.children[child]
            cursor += 1

            if self.working_node == self.NYT:
                symbol = encoding[cursor : cursor + 8]
                cursor += 8
                self._add(symbol)
                self.working_node = self.nodes[-1]
                return symbol, cursor, False
            if self.working_node == self.EOF:
                return None, cursor, True
            if self.working_node.symbol is not None:
                symbol = self.working_node.symbol
                self._add(symbol)
                self.working_node = self.nodes[-1]
                return symbol, cursor, False
        return None, 0, False

    def decode_chunk(self, chunk: bitarray):
        """
        Decodes encoded symbols

        Args:
            chunk (bitarray): Array of bits containing encoded symbols

        Returns:
            tuple[bitarray, bool]: Tuple containing: decoded symbols, value of EOF flag
        """
        content = bitarray()
        cursor = 0
        symbol, offset, is_eof = self.decode_symbol(chunk)
        while symbol is not None:
            cursor += offset
            content.extend(symbol)
            symbol, offset, is_eof = self.decode_symbol(chunk[cursor:])
        return content, is_eof

    def _add(self, symbol):
        i = self._find_symbol(symbol)
        self._add_new_leaf(Node(0, symbol=symbol), i)

    def _add_new_leaf(self, new_leaf, i):
        if i is None:
            parent = Node(0)
            if self.NYT.parent:
                self.NYT.parent.set_child(parent, self.NYT.side)
            parent.set_child(self.NYT, ChildSide.LEFT)
            parent.set_child(new_leaf, ChildSide.RIGHT)
            self.nodes.insert(1, parent)
            self.nodes.insert(1, new_leaf)
            i = 1
        node = None
        while node != self.nodes[-1]:
            node = self.nodes[i]
            j = self._find_max_in_a_block(i)
            if i != j:
                self._swap_nodes(i, j)
                i = j
            node.weight += 1
            if i == len(self.nodes) - 1:
                return
            i = self._find_parent_number(i)

    def _find_max_in_a_block(self, i: int):
        node = self.nodes[i]
        max_in_block = i
        for j in range(i, len(self.nodes)):
            if self.nodes[j] == node.parent:
                continue
            if self.nodes[j].weight == node.weight:
                max_in_block = j
            if self.nodes[j].weight > node.weight:
                break
        return max_in_block

    def _find_symbol(self, symbol):
        for i, n in enumerate(self.nodes):
            if n.symbol == symbol:
                return i
        return None  # more readable

    def _find_parent_number(self, i: int):
        for j in range(i + 1, len(self.nodes)):
            if self.nodes[j] == self.nodes[i].parent:
                return j
        return len(self.nodes) - 1

    def _swap_nodes(self, i: int, j: int):
        a, b = self.nodes[i], self.nodes[j]
        if a.parent:
            a.parent.children[a.side.value] = b
        if b.parent:
            b.parent.children[b.side.value] = a
        a.parent, b.parent = b.parent, a.parent
        a.side, b.side = b.side, a.side
        self.nodes[i], self.nodes[j] = self.nodes[j], self.nodes[i]

    def print(self):
        self.nodes[-1].print()
        print("\n====================")
