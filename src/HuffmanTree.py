from bitarray import bitarray
from typing import Union

LEFT_CHILD = 0
RIGHT_CHILD = 1

ChildSide = Union[LEFT_CHILD, RIGHT_CHILD]


class Node:
    def __init__(
        self,
        weight: int = 0,
        parent: Union["Node", None] = None,
        side: Union[int, None] = None,
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
        self.children[side] = child
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
            code = str(n.side) + code
            n = n.parent
        return bitarray(code)

    def decode(self, encoding: bitarray):
        """ Returns decoded symbol, number of used bits and eof flag """
        for cursor, child in enumerate(encoding):
            self.active_node = self.active_node.children[child]

            if self.active_node == self.EOF:
                return None, cursor, True
            elif self.active_node == self.NYT:
                cursor += 1
                symbol = encoding[cursor:cursor+8].tobytes()
                cursor += 8
                self._new_leaf(Node(0, symbol=symbol))
            elif self.active_node.symbol is not None:
                cursor += 1
                symbol = self.active_node.symbol
            else:
                continue

            self._increment(self.leafs[symbol])
            self.active_node = self.nodes[0]
            return symbol, cursor, False
        return None, 0, False

    def decode_chunk(self, chunk) -> (bytearray, bool):
        """ Returns decoded symbols and eof flag """
        content = b""
        cursor = 0
        symbol, offset, is_eof = self.decode(chunk)
        while (symbol is not None):
            cursor += offset
            content += symbol
            symbol, offset, is_eof = self.decode(chunk[cursor:])
        return content, is_eof

    def _new_leaf(self, leaf):
        nyt = self.nodes[-1]
        parent = Node(0)
        if nyt.parent:
            nyt.parent.set_child(parent, nyt.side)
        parent.set_child(nyt, LEFT_CHILD)
        parent.set_child(leaf, RIGHT_CHILD)
        parent.pos = nyt.pos
        leaf.pos = parent.pos + 1
        nyt.pos = parent.pos + 2
        self.nodes[-1] = parent
        self.nodes.append(leaf)
        self.nodes.append(nyt)
        if leaf.symbol:
            self.leafs[leaf.symbol] = leaf
        return leaf

    def _increment(self, node):
        root = self.nodes[0]
        while node != root:
            self._slide(node)
            node.weight += 1
            if node == root:
                return
            node = node.parent

    def _slide(self, node):
        leader = node
        for n in self.nodes[node.pos:0:-1]:
            if n == node.parent:
                continue
            if n.weight == node.weight:
                leader = n
            if n.weight > node.weight:
                break
        self._swap(node, leader)
        return leader

    def _swap(self, a, b):
        if a == b:
            return
        if a.parent:
            a.parent.children[a.side] = b
        if b.parent:
            b.parent.children[b.side] = a
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
                    new_level.append(n.children[LEFT_CHILD])
                    new_level.append(n.children[RIGHT_CHILD])
                print(n, end='\t')
            level = new_level
            print()
            if all(n is None for n in level):
                break

        print("\n====================")
