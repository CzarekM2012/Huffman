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
        """
        Constructs codes for symbols based on structure of the tree

        Returns:
            dict[bytes, bitarray]: codes for symbols present in tree
        """
        codings: dict[bytes, bitarray] = {}

        def explore(node: Node, code_prefix=bitarray()):
            for side_index in [side.value for side in ChildSide]:
                child = node.children[side_index]
                if child is not None:
                    explore(child, code_prefix + bitarray([side_index]))
            if node.is_leaf():
                # Symbol is inspected while checking if node is a leaf
                codings[node.symbol] = code_prefix  # type: ignore

        explore(self)
        return codings

    def set_child(self, child: "Node", side: ChildSide):
        """
        Performs all operations for setting a child of the node

        Args:
            child (Node): Node that is going to be set as a child
            side (ChildSide): Side of the subtree child will be put in
        """
        self.children[side.value] = child
        child.parent = self
        child.side = side

    def is_leaf(self):
        """
        Check if node is a leaf (has symbol and no children) or a internal node (has no symbol and both children)

        Raises:
            RuntimeError: Raised if node is not a proper leaf or internal node (has both children and symbol or neither of them)

        Returns:
            bool: True if is a leaf, False if a internal node
        """
        has_symbol = not self.symbol is None
        has_children = not all(child is None for child in self.children)
        if has_symbol and not has_children:
            return True
        if not has_symbol and has_children:
            return False
        raise RuntimeError(
            "This node does not meet the requirements for either internal or leaf node"
        )
