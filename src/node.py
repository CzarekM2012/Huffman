from typing import Union
from enum import Enum
from bitarray import bitarray


class ChildSide(Enum):
    LEFT = 0
    RIGHT = 1


class Node:
    def __init__(
        self,
        weight: int = 0,
        parent: Union["Node", None] = None,
        side: Union[ChildSide, None] = None,
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
        right = self.children[ChildSide.RIGHT.value]
        if right is not None:
            right.print(pad + 1)
        print("\n" + "\t" * pad, end="")
        left = self.children[ChildSide.LEFT.value]
        if left is not None:
            left.print(pad + 1)

    def get_codings(self) -> dict[bytes, bitarray]:
        codings: dict[bytes, bitarray] = {}

        def explore(node: Node, code_prefix=bitarray()):
            for side_index in [side.value for side in ChildSide]:
                child = node.children[side_index]
                if child is not None:
                    explore(child, code_prefix + bitarray([side_index]))
            if all(child is None for child in node.children):
                if node.symbol is None:
                    raise ValueError("Leaf node does not contain symbol")
                codings[node.symbol] = code_prefix

        explore(self)
        return codings

    def set_child(self, child: "Node", side: ChildSide):
        self.children[side.value] = child
        child.parent = self
        child.side = side
