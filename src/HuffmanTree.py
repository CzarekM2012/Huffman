from src.node import Node, RIGHT_CHILD, LEFT_CHILD


class HuffmanTree:
    def __init__(self):
        self.NYT = Node()
        self.nodes = [self.NYT]  # attribute

    def code(self, symbol):
        i = self._find_symbol(symbol)
        n = self.NYT if i is None else self.nodes[i]
        code = ""
        while n.parent:
            code = str(n.side) + code
            n = n.parent
        self._add(symbol)
        return code + symbol if i is None else code

    def decode(self, code):
        n = self.nodes[-1]
        for i, c in enumerate(code):
            if n == self.NYT:
                self._add(code[i:])
                return code[i:]
            n = n.children[int(c)]

        self._add(n.symbol)
        return n.symbol

    def _add(self, symbol):
        i = self._find_symbol(symbol)

        if i is None:
            parent = Node(0)
            new_leaf = Node(0, symbol=symbol)
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
