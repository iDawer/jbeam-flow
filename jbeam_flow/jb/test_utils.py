import unittest

from antlr4 import *
from jb import jbeamLexer, jbeamParser, jbeamVisitor
from jb.utils import preprocess


def get_preprocessed(data):
    data_stream = InputStream(data)
    lexer = jbeamLexer(data_stream)
    stream = CommonTokenStream(lexer)
    return preprocess(stream)


class PreprocessTests(unittest.TestCase):
    def test_simple(self):
        stream = get_preprocessed('"$var"')
        t = stream.LT(1)
        self.assertEqual(jbeamLexer.NUMBER, t.type)
        self.assertEqual("0", t.text)

    def test_mixed(self):
        stream = get_preprocessed('1 "$some", "string" [ "$definition" ]')
        t = stream.LT(1)
        self.assertEqual(jbeamLexer.NUMBER, t.type)
        self.assertEqual("1", t.text)
        stream.consume()
        t = stream.LT(1)
        self.assertEqual(jbeamLexer.NUMBER, t.type)
        self.assertEqual("0", t.text)
        stream.consume()
        t = stream.LT(1)
        self.assertEqual(jbeamLexer.STRING, t.type)
        self.assertEqual('"string"', t.text)
        stream.consume()
        t = stream.LT(2)
        self.assertEqual(jbeamLexer.STRING, t.type)
        self.assertEqual('"$definition"', t.text)
        stream.consume()


if __name__ == '__main__':
    unittest.main()
