import unittest
from src.huffmanTree import HuffmanTree


class TestSimpleCoding(unittest.TestCase):

    def initTree(self):
        ht = HuffmanTree()
        [ht.code("B") for _ in range(12)]
        [ht.code("A") for _ in range(6)]
        [ht.code("D") for _ in range(5)]
        [ht.code("E") for _ in range(4)]
        [ht.code("C") for _ in range(4)]
        return ht

    def test_codings(self):
        ht = HuffmanTree()
        self.assertEqual(ht.code("a"), "a")
        self.assertEqual(ht.code("b"), "0b")
        self.assertEqual(ht.code("b"), "01")

    def test_aardvark(self):
        ht = HuffmanTree()
        self.assertEqual(ht.code("a"), "a")
        self.assertEqual(ht.code("a"), "1")
        self.assertEqual(ht.code("r"), "0r")
        self.assertEqual(ht.code("d"), "00d")
        self.assertEqual(ht.code("v"), "000v")
        self.assertEqual(ht.code("v"), "1101")

    def test_decode_known(self):
        coding_ht = self.initTree()
        decoding_ht = self.initTree()

        # self.assertEqual(decoding_ht.decode(coding_ht.code("C")), "C")
        for v in "ABCDE":
            self.assertEqual(decoding_ht.decode(coding_ht.code(v)), v)

    def test_decode_nyt(self):
        coding_ht = self.initTree()
        decoding_ht = self.initTree()
        for v in "N":
            self.assertEqual(decoding_ht.decode(coding_ht.code(v)), v)


if __name__ == '__main__':
    unittest.main()
