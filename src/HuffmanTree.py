from src.node import Node, RIGHT_CHILD, LEFT_CHILD
from bitarray import bitarray


class HuffmanTree:
    buffer: bitarray
    decoding_node: Node

    def __init__(self):
        self.buffer = bitarray()
        self.NYT = Node()
        self.EOF = Node()
        self.nodes = [self.NYT]  # attribute
        self._add_new_leaf(self.EOF, None)
        self.decoding_node = self.nodes[-1]

    def encode_eof(self):
        n = self.EOF
        code = bitarray()
        while n.parent:
            code.append(n.side)
            n = n.parent
        code.reverse()
        # print('encoded eof', code)
        return code

    def encode(self, symbol):
        i = self._find_symbol(symbol)
        n = self.NYT if i is None else self.nodes[i]
        e = bitarray()
        e.frombytes(symbol)
        # print("encoded: ", e)
        code = bitarray()
        while n.parent:
            code.append(n.side)
            n = n.parent
        code.reverse()
        self._add(symbol)
        if i is None:
            code.frombytes(symbol)
        return code

    def decode(self, bits):
        content = bitarray()
        while len(bits) != 0:
            while (self.decoding_node != self.NYT
                   and self.decoding_node != self.EOF
                   and self.decoding_node.symbol is None
                   and len(bits) != 0):
                child = bits.pop(0)
                self.decoding_node = self.decoding_node.children[child]

            if self.decoding_node == self.NYT:
                symbol = bits[:8]
                [bits.pop(0) for _ in range(8)]
                self._add(symbol)
                self.decoding_node = self.nodes[-1]
                # print('decoded: ', symbol)
                content.extend(symbol)
            elif self.decoding_node == self.EOF:
                # print('decoded eof')
                return content
            elif self.decoding_node.symbol is not None:
                symbol = self.decoding_node.symbol
                self.decoding_node = self.nodes[-1]
                # print('decoded: ', symbol)
                self._add(symbol)
                content.extend(symbol)

        return content
        # for b in self.buffer:
        #     if self.decoding_node == self.NYT:
        #         symbol = bitarray(self.buffer[:8])
        #         return symbol
        #     self.decoding_node = self.decoding_node.children[b]
        # return
        # n = self.nodes[-1]
        # for i, c in enumerate(code):
        #     if n == self.NYT:
        #         self._add(code[i:])
        #         return code[i:]
        #     n = n.children[int(c)]
        #
        # self._add(n.symbol)
        # return n.symbol

    def _add(self, symbol):
        i = self._find_symbol(symbol)
        self._add_new_leaf(Node(0, symbol=symbol), i)

    def _add_new_leaf(self, new_leaf, i):
        if i is None:
            parent = Node(0)
            if self.NYT.parent:
                self.NYT.parent.set_child(parent, self.NYT.side)
            parent.set_child(self.NYT, LEFT_CHILD)
            parent.set_child(new_leaf, RIGHT_CHILD)
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

    def _find_max_in_a_block(self, i):
        node = self.nodes[i]
        max_in_block = i
        for i in range(i, len(self.nodes)):
            if self.nodes[i] == node.parent:
                continue
            if self.nodes[i].weight == node.weight:
                max_in_block = i
            if self.nodes[i].weight > node.weight:
                break
        return max_in_block

    def _find_symbol(self, symbol):
        for i, n in enumerate(self.nodes):
            if n.symbol == symbol:
                return i
        return None  # more readable

    def _find_parent_number(self, i):
        for j in range(i + 1, len(self.nodes)):
            if self.nodes[j] == self.nodes[i].parent:
                return j
        return len(self.nodes) - 1

    def _swap_nodes(self, i, j):
        a, b = self.nodes[i], self.nodes[j]
        if a.parent:
            a.parent.children[a.side] = b
        if b.parent:
            b.parent.children[b.side] = a
        a.parent, b.parent = b.parent, a.parent
        a.side, b.side = b.side, a.side
        self.nodes[i], self.nodes[j] = self.nodes[j], self.nodes[i]

    def print(self):
        self.nodes[-1].print()
        print("\n====================")
