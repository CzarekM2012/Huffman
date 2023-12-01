from src.node import Node


class HuffmanTree:
    def __init__(self):
        self.nodes = []  # attribute

        # example data (to remove)
        self.nodes.append(Node(31))
        self.nodes.insert(0, Node(19, self.nodes[-1], 1))
        self.nodes.insert(0, Node(12, self.nodes[-1], 0, "B"))
        self.nodes.insert(0, Node(11, self.nodes[-2], 1))
        self.nodes.insert(0, Node(8, self.nodes[-2], 0))
        self.nodes.insert(0, Node(6, self.nodes[-4], 1, "A"))
        self.nodes.insert(0, Node(5, self.nodes[-4], 0, "D"))
        self.nodes.insert(0, Node(4, self.nodes[-5], 1, "E"))
        self.nodes.insert(0, Node(4, self.nodes[-5], 0, "C"))
        for n in self.nodes:
            if n.parent:
                n.parent.children[n.side] = n

    def add(self, symbol):
        i = self._find_symbol(symbol)

        if i is None:
            sibling = self.nodes[0]
            parent = Node(sibling.weight, sibling.parent, sibling.side)
            if sibling.parent:
                sibling.parent.children[sibling.side] = parent
            parent.children[1] = sibling
            parent.children[0] = Node(0, parent, 0, symbol)
            sibling.parent = parent
            sibling.side = 1
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
        n = self.nodes[i]
        code = ""
        while n.parent:
            code = str(n.side) + code
            n = n.parent
        return code

    def decode(self, code):
        n = self.nodes[-1]
        for c in code:
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
