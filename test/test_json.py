import unittest

from antlr4 import *
from jb import jbeamLexer, jbeamParser, jbeamVisitor
from misc import visitor_mixins

# class Visitor(visitor_mixins.Json, jbeamVisitor): pass
visitor = visitor_mixins.Json()


def get_stream(str: str):
    lexer = jbeamLexer(InputStream(str))
    stream = CommonTokenStream(lexer)
    stream.fill()  # force lazy init
    return stream


def get_parser(str: str):
    stream = get_stream(str)
    parser = jbeamParser(stream)
    return parser


class JsonTestCase(unittest.TestCase):
    def test_boolean(self):
        p = get_parser('true')
        ctx = p.boolean()
        result = ctx.accept(visitor)
        self.assertEqual(True, result)
        result = get_parser('false').boolean().accept(visitor)
        self.assertEqual(False, result)
        bad_res = get_parser('bad').boolean().accept(visitor)
        self.assertIsNone(bad_res)

    def test_genericString(self):
        parser = get_parser('"some text"')
        ctx = parser.genericString()
        result = ctx.accept(visitor)
        self.assertEqual("some text", result)

    def test_obj(self):
        parser = get_parser('{"key": -12e-3, "array": []}')
        ctx = parser.obj()
        self.assertIsInstance(ctx, jbeamParser.ObjContext)
        result = ctx.accept(visitor)
        self.assertIn("key", result)
        self.assertEqual(-12e-3, result["key"])
        self.assertIn("array", result)
        self.assertIsInstance(result["array"], list)

    def test_atom(self):
        parser = get_parser('234')
        ctx = parser.value()
        self.assertIsInstance(ctx, jbeamParser.AtomContext)
        self.assertEqual(234, ctx.accept(visitor))
        ctx = get_parser('false').value()
        self.assertEqual(False, ctx.accept(visitor))

    def test_array(self):
        parser = get_parser('["text", [42, {}]]')
        ctx = parser.array()
        result = ctx.accept(visitor)
        self.assertIsInstance(result, list)
        self.assertEqual(["text", [42, {}]], result)


if __name__ == '__main__':
    unittest.main()
