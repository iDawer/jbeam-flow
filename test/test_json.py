import unittest

from antlr4 import *
from jb import jbeamLexer, jbeamParser, jbeamVisitor

try:
    from misc import visitor_mixins
except ValueError as ex:
    raise ImportError(r"to run the tests replace relative import '..jb' with 'jb' in misc\visitor_mixins.py") from ex

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

    def test_comment_line(self):
        parser = get_parser('//comment \n {"k": //inline\n1}')
        ctx = parser.obj()
        result = ctx.accept(visitor)
        self.assertIsInstance(result, object)
        self.assertEqual({"k": 1}, result)

    def test_comment_block(self):
        parser = get_parser('/*comment \n*/ {"k": /*inline*/ 1\n}')
        ctx = parser.obj()
        result = ctx.accept(visitor)
        self.assertIsInstance(result, object)
        self.assertEqual({"k": 1}, result)


if __name__ == '__main__':
    unittest.main()
