import unittest
from src.huffmanTree import HuffmanTree


class TestSimpleCoding(unittest.TestCase):

    def assertCoding(self, ht, values):
        for v in values:
            self.assertEqual(ht.decode(ht.code(v)), v)

    def test_example_a(self):
        ht = HuffmanTree()
        self.assertCoding(ht, "ABCDE")

    def test_example_b(self):
        ht = HuffmanTree()
        ht.add("C")
        self.assertCoding(ht, "ABCDE")

    def test_example_c(self):
        ht = HuffmanTree()
        ht.add("C")
        ht.add("C")
        self.assertCoding(ht, "ABCDE")

    def test_example_d(self):
        ht = HuffmanTree()
        ht.add("C")
        ht.add("C")
        ht.add("C")
        self.assertCoding(ht, "ABCDE")

    def test_example_e(self):
        ht = HuffmanTree()
        ht.add("C")
        ht.add("C")
        ht.add("C")
        ht.add("C")
        ht.add("C")
        ht.add("C")
        ht.add("N")
        self.assertCoding(ht, "ABCDEN")


if __name__ == '__main__':
    unittest.main()
