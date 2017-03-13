import unittest

from antlr4 import *
from decoder import ExtJSONLexer, ExtJSONParser, ExtJSONEvaluator, load

visitor = ExtJSONEvaluator()


def get_stream(str: str):
    lexer = ExtJSONLexer(InputStream(str))
    stream = CommonTokenStream(lexer)
    stream.fill()  # force lazy init
    return stream


def get_parser(str: str):
    stream = get_stream(str)
    parser = ExtJSONParser(stream)
    return parser


class JsonVisitorTestCase(unittest.TestCase):
    def test_json(self):
        parser = get_parser('{"foo": 42}')
        ctx = parser.json()
        result = ctx.accept(visitor)
        self.assertEqual({"foo": 42}, result)

    def test_boolean(self):
        p = get_parser('true')
        ctx = p.value()
        result = ctx.accept(visitor)
        self.assertEqual(True, result)
        result = get_parser('false').value().accept(visitor)
        self.assertEqual(False, result)

    def test_string(self):
        parser = get_parser('"some text"')
        ctx = parser.value()
        result = ctx.accept(visitor)
        self.assertEqual("some text", result)

    def test_obj(self):
        parser = get_parser('{"key": -12e-3, "array": []}')
        ctx = parser.object()
        self.assertIsInstance(ctx, ExtJSONParser.ObjectContext)
        result = ctx.accept(visitor)
        self.assertIn("key", result)
        self.assertEqual(-12e-3, result["key"])
        self.assertIn("array", result)
        self.assertIsInstance(result["array"], list)

    def test_atom(self):
        parser = get_parser('234')
        ctx = parser.value()
        self.assertIsInstance(ctx, ExtJSONParser.ValueAtomContext)
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
        ctx = parser.object()
        result = ctx.accept(visitor)
        self.assertIsInstance(result, object)
        self.assertEqual({"k": 1}, result)

    def test_comment_block(self):
        parser = get_parser('/*comment \n*/ {"k": /*inline*/ 1\n}')
        ctx = parser.object()
        result = ctx.accept(visitor)
        self.assertIsInstance(result, object)
        self.assertEqual({"k": 1}, result)

    def test_bad_object(self):
        parser = get_parser('{123: "abc"}')
        ctx = parser.object()
        from antlr4.error.Errors import InputMismatchException
        self.assertIsNotNone(ctx.exception)
        self.assertIsInstance(ctx.exception, InputMismatchException)

    def test_recover_bad_middle_pair(self):
        parser = get_parser('{"foo": "bar", 123: null "key": "abc"}')
        ctx = parser.object()
        result = ctx.accept(visitor)
        self.assertEqual({"foo": "bar", "key": "abc"}, result)

    @unittest.skip('need proper recovery')
    def test_recover_array_bad_first_object(self):
        parser = get_parser('[{123: null "key": "abc"}, {}]')
        ctx = parser.array()
        result = ctx.accept(visitor)
        self.assertEqual([{"key": "abc"}, {}], result)


class LoadTestCase(unittest.TestCase):
    def test_empty(self):
        res = load('')
        self.assertIsNone(res)

    def test_object(self):
        result = load('{"foo": 1e4 "bar":null}')
        self.assertEqual({"foo": 1e4, "bar": None}, result)

    def test_object_empty(self):
        result = load('{}')
        self.assertEqual({}, result)

    def test_array(self):
        result = load('[{"foo": -1e-4 "bar":null}{}, true]')
        self.assertEqual([{"foo": -1e-4, "bar": None}, {}, True], result)

    def test_array_empty(self):
        result = load('[  \n\t\n ]')
        self.assertEqual([], result)


if __name__ == '__main__':
    unittest.main()
