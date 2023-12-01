import unittest
from src.huffmanTree import HuffmanTree


class TestSimpleCoding(unittest.TestCase):

    def initTree(self):
        ht = HuffmanTree()
        [ht.add("B") for _ in range(12)]
        [ht.add("A") for _ in range(1)]
        [ht.add("D") for _ in range(5)]
        [ht.add("E") for _ in range(4)]
        [ht.add("C") for _ in range(4)]
        return ht

    def test_decode_known(self):
        coding_ht = self.initTree()
        decoding_ht = self.initTree()
        for v in "ABCDE":
            self.assertEqual(decoding_ht.decode(coding_ht.code(v)), v)

    def test_decode_nyt(self):
        coding_ht = self.initTree()
        decoding_ht = self.initTree()
        for v in "N":
            self.assertEqual(decoding_ht.decode(coding_ht.code(v)), v)


if __name__ == '__main__':
    unittest.main()
