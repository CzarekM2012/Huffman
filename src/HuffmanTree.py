from src.node import Node


class HuffmanTree:
    def __init__(self):
        self.NYT = Node()
        self.nodes = [self.NYT]  # attribute

    def add(self, symbol):
        i = self._find_symbol(symbol)

        if i is None:
            parent = Node(1, self.NYT.parent, self.NYT.side)
            if self.NYT.parent:
                self.NYT.parent.children[self.NYT.side] = parent
            parent.children[1] = self.NYT
            parent.children[0] = Node(0, parent, 0, symbol)
            self.NYT.parent = parent
            self.NYT.side = 1
            self.nodes.insert(1, parent)
            self.nodes.insert(0, parent.children[0])
            return

        while True:
            self.nodes[i].weight += 1
            if self.nodes[i].parent is None:
                break

            j = i
            while self.nodes[j + 1].weight == (self.nodes[i].weight - 1):
                j += 1
            self._swap_nodes(i, j)
            i = j

            for j in range(i + 1, len(self.nodes)):
                if self.nodes[j] == self.nodes[i].parent:
                    i = j
                    break

    def code(self, symbol):
        i = self._find_symbol(symbol)
        n = self.NYT if i is None else self.nodes[i]
        code = ""
        while n.parent:
            code = str(n.side) + code
            n = n.parent
        return code + symbol if i is None else code

    def decode(self, code):
        n = self.nodes[-1]
        for i, c in enumerate(code):
            if n == self.NYT:
                return code[i:]
            n = n.children[int(c)]

        return n.symbol

    def _find_symbol(self, symbol):
        for i, n in enumerate(self.nodes):
            if n.symbol == symbol:
                return i
        return None  # more readable

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
