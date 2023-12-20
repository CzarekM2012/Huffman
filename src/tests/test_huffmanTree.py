import unittest
from bitarray import bitarray
from src.HuffmanTree import HuffmanTree as Ahuf
# from src.huffman_tree_v2 import Ahuf


class TestSimpleCoding(unittest.TestCase):

    def assert_encoding(self, e, symbol, code, suffix=b""):
        encoding = e.encode(symbol)
        expected = bitarray(code)
        expected.frombytes(suffix)
        self.assertEqual(encoding, expected)

    def assert_decoding(self, e, d, symbol):
        encoding = e.encode(symbol)
        decoding, _, _ = d.decode(encoding)
        self.assertEqual(decoding, symbol)

    def test_codings(self):
        encoder = Ahuf()
        decoder = Ahuf()
        self.assert_decoding(encoder, decoder, b"a")
        self.assert_decoding(encoder, decoder, b"b")
        self.assert_decoding(encoder, decoder, b"b")

    def test_aardvark_encoding(self):
        encoder = Ahuf(eof=False)
        self.assert_encoding(encoder, b"a", "", b"a")
        self.assert_encoding(encoder, b"a", "1")
        self.assert_encoding(encoder, b"r", "0", b"r")
        self.assert_encoding(encoder, b"d", "00", b"d")
        self.assert_encoding(encoder, b"v", "000", b"v")
        self.assert_encoding(encoder, b"v", "1101")

    def test_aardvark_decoding(self):
        encoder = Ahuf()
        decoder = Ahuf()
        self.assert_decoding(encoder, decoder, b"a")
        self.assert_decoding(encoder, decoder, b"a")
        self.assert_decoding(encoder, decoder, b"r")
        self.assert_decoding(encoder, decoder, b"d")
        self.assert_decoding(encoder, decoder, b"v")
        self.assert_decoding(encoder, decoder, b"v")

    def test_eof(self):
        encoder = Ahuf()
        decoder = Ahuf()
        self.assert_decoding(encoder, decoder, b"a")
        self.assert_decoding(encoder, decoder, b"a")
        self.assert_decoding(encoder, decoder, b"r")
        self.assert_decoding(encoder, decoder, b"d")
        self.assert_decoding(encoder, decoder, b"v")
        self.assert_decoding(encoder, decoder, b"v")
        eof_encoding = encoder.encode_eof()
        symbol, read, is_eof = decoder.decode(eof_encoding)
        self.assertTrue(is_eof)

    def test_decode_chunk(self):
        encoder = Ahuf()
        decoder = Ahuf()

        encoding = bitarray()
        for character in "aardvv":
            encoding += encoder.encode(character.encode())
        decoding, is_eof = decoder.decode_chunk(encoding)
        self.assertEqual(decoding, b"aardvv")


if __name__ == '__main__':
    unittest.main()
