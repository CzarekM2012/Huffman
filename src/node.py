from typing import Union
from bitarray import bitarray

LEFT_CHILD = 0
RIGHT_CHILD = 1


class Node:
    def __init__(
        self,
        weight: int = 0,
        parent: Union["Node", None] = None,
        side: Union[int, None] = None,
        symbol: Union[bytes, None] = None,
    ):
        self.parent = parent
        self.side = side
        self.weight = weight
        self.symbol = symbol
        self.children: list[Union["Node", None]] = [None, None]

    def __str__(self):
        prefix = "\\" if self.side else "-"
        suffix = f"({self.symbol})" if self.symbol else ""
        return f"{prefix}{self.weight} {suffix}"

    def print(self, pad=1):
        print(self, end="\t")
        left = self.children[LEFT_CHILD]
        if left is not None:
            left.print(pad + 1)
        print("\n" + "\t" * pad, end="")
        right = self.children[RIGHT_CHILD]
        if right is not None:
            right.print(pad + 1)

    def get_codings(self) -> dict[bytes, bitarray]:
        codings: dict[bytes, bitarray] = {}

        def explore(node: Node, code_prefix=bitarray()):
            for side in [LEFT_CHILD, RIGHT_CHILD]:
                child = node.children[side]
                if child is not None:
                    explore(child, code_prefix + bitarray([side]))
            if all(child is None for child in node.children):
                if node.symbol is None:
                    raise ValueError("Leaf node does not contain symbol")
                codings[node.symbol] = code_prefix

        explore(self)
        return codings
