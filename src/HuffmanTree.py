from typing import Union
from bitarray import bitarray
from src.node import ChildSide


class Node:
    def __init__(
        self,
        weight: int = 0,
        parent: Union["Node", None] = None,
        side: Union[ChildSide, None] = None,
        symbol: Union[bytes, None] = None,
    ):
        self.parent = parent
        self.pos = 0
        self.side = side
        self.weight = weight
        self.symbol = symbol
        self.children: list[Union["Node", None]] = [None, None]

    def __str__(self):
        prefix = "\\" if self.side else "-"
        suffix = f"({self.symbol})" if self.symbol else ""
        return f"{prefix}{self.weight} {suffix} pos={self.pos}"

    def set_child(self, child: "Node", side: ChildSide):
        self.children[side.value] = child
        child.parent = self
        child.side = side


class HuffmanTree:

    def __init__(self, eof=True):
        self.NYT = Node()
        self.nodes = [self.NYT]  # attribute
        if eof:
            self.EOF = Node()
            self._new_leaf(self.EOF)
            self._increment(self.EOF)
        self.active_node = self.nodes[0]
        self.leafs = {}

    def encode_eof(self):
        return self._encode_node(self.EOF)

    def encode(self, symbol):
        if symbol in self.leafs:
            node = self.leafs[symbol]
            code = self._encode_node(node)
        else:
            code = self._encode_node(self.NYT)
            code.frombytes(symbol)
            node = self._new_leaf(Node(0, symbol=symbol))
        self._increment(node)
        return code

    def _encode_node(self, n):
        code = ''
        while n.parent:
            code = str(n.side.value) + code
            n = n.parent
        return bitarray(code)

    def decode_symbol(self, encoding: bitarray) -> tuple[Union[bytes, bitarray, None], int, bool]:
        """
        Decodes a single encoded symbol
        Args:
            encoding (bitarray): Array of bits containing the encoded symbol
        Returns:
            tuple[bytes | bitarray | None, int, bool]: Tuple containing: decoded symbol, number of bits used in decoding, value of EOF flag
        """
        for cursor, child in enumerate(encoding):
            self.active_node = self.active_node.children[child]
            if self.active_node == self.EOF:
                return None, cursor, True

            cursor += 1

            if self.active_node == self.NYT:
                symbol = encoding[cursor: cursor + 8].tobytes()
                cursor += 8
                self._new_leaf(Node(0, symbol=symbol))
                self._increment(self.leafs[symbol])
                self.active_node = self.nodes[0]
                return symbol, cursor, False

            if self.active_node.symbol is not None:
                symbol = self.active_node.symbol
                self._increment(self.leafs[symbol])
                self.active_node = self.nodes[0]
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
        content = b""
        cursor = 0
        symbol, offset, is_eof = self.decode_symbol(chunk)
        while (symbol is not None):
            cursor += offset
            content += symbol
            symbol, offset, is_eof = self.decode_symbol(chunk[cursor:])
        return content, is_eof

    def _new_leaf(self, leaf):
        """
        Adds new leaf in the tree by replacing NYT node with a parent node, whose childs are the new leaf and the NYT node
        Args:
            leaf (Node): Leaf to add
        Returns:
            Node: The added leaf
        """
        nyt = self.nodes[-1]
        parent = Node(0)
        if nyt.parent:
            nyt.parent.set_child(parent, nyt.side)
        parent.set_child(nyt, ChildSide.LEFT)
        parent.set_child(leaf, ChildSide.RIGHT)
        parent.pos = nyt.pos
        leaf.pos = parent.pos + 1
        nyt.pos = parent.pos + 2
        self.nodes[-1] = parent
        self.nodes.append(leaf)
        self.nodes.append(nyt)
        if leaf.symbol:
            self.leafs[leaf.symbol] = leaf
        return leaf

    def _increment(self, node: Node):
        """
        Slides given node in the tree and increments it's weight
        Args:
            node (Node): Node to slide
        """
        root = self.nodes[0]
        while node != root:
            self._slide(node)
            node.weight += 1
            if node == root:
                return
            node = node.parent

    def _slide(self, node: Node):
        """
        Slides given node in the tree b finding the leader of it's block and swaps them
        Args:
            node (Node): Node to slide
        """
        leader = node
        for n in self.nodes[node.pos:0:-1]:
            if n == node.parent:
                continue
            if n.weight == node.weight:
                leader = n
            if n.weight > node.weight:
                break
        self._swap(node, leader)

    def _swap(self, a: Node, b: Node):
        """
        Swaps position of two node.
        Args:
            node (Node): First node to swap
            node (Node): First node to swap
        """

        if a == b:
            return
        if a.parent:
            a.parent.children[a.side.value] = b
        if b.parent:
            b.parent.children[b.side.value] = a
        a.parent, b.parent = b.parent, a.parent
        a.side, b.side = b.side, a.side
        i, j = a.pos, b.pos
        self.nodes[i], self.nodes[j] = self.nodes[j], self.nodes[i]
        a.pos, b.pos = j, i

    def print(self):
        level = [self.nodes[0]]
        while len(level):
            new_level = []
            for n in level:
                if n is None:
                    new_level.append(None)
                    new_level.append(None)
                else:
                    new_level.append(n.children[ChildSide.LEFT])
                    new_level.append(n.children[ChildSide.RIGHT])
                print(n, end='\t')
            level = new_level
            print()
            if all(n is None for n in level):
                break
        print("\n====================")
