import unittest

from jbeam import ExtJSONParser, JbeamVisitor, JbeamBase, Switch
from jbeam.test import test_ExtJSON

# fast links
# ValueAtomContext = ExtJSONParser.ValueAtomContext
_ValuesContext = ExtJSONParser.ValuesContext
_ValueContext = ExtJSONParser.ValueContext
_ValueArrayContext = ExtJSONParser.ValueArrayContext
_ValueObjectContext = ExtJSONParser.ValueObjectContext
_ValueStringContext = ExtJSONParser.ValueStringContext

_Parser = ExtJSONParser
_jbv = JbeamVisitor()
_j_base = JbeamBase()


def _fast_res(src, parser_method, visitor_method):
    parser = test_ExtJSON.get_parser(src)
    ctx = getattr(parser, getattr(parser_method, '__name__'))()
    return visitor_method(ctx)


class _JbeamVisitorTestCase(unittest.TestCase):
    def test_jbeam(self):
        result = _fast_res('{"p1":{}, "p2":{}}', _Parser.object, _jbv.visit_jbeam)
        self.assertEqual({"p1": {}, "p2": {}}, result)

    def test_parts(self):
        result = _fast_res('"p1":{}, "p2":{}', _Parser.pairs, _jbv.visit_parts)
        self.assertEqual([("p1", {}), ("p2", {})], result)

    def test_part(self):
        res = _fast_res('"part": {}', _Parser.pair, _jbv.visit_part)
        self.assertEqual(("part", {}), res)

    def test_part_value(self):
        res = _fast_res('{"slotType": "abc"}', _Parser.value, _jbv.visit_part_value)
        self.assertEqual({"slotType": "abc"}, res)
        pass


class _JbeamBaseTestCase(unittest.TestCase):
    @staticmethod
    def row_handler(header, row_ctx, array: list):
        with Switch.Inst(row_ctx) as case:
            if case(_ValueArrayContext):
                row = row_ctx.accept(_j_base)
                map = _j_base.row_to_map(header, row)
            elif case(_ValueObjectContext):
                map = row_ctx.accept(_j_base)
            else:
                # other types in a table not supported, ignore them
                return
        array.append(map)

    def test_table(self):
        parser = test_ExtJSON.get_parser('''
        ["foo", "bar"],
        [1, 2, 3],
        ''')
        ctx = parser.values()
        rows = ctx.value()
        result = []
        _j_base.table(rows, self.row_handler, (result,))
        self.assertEqual([{"foo": 1, "bar": 2}], result)

    def test_row_inlined_map(self):
        parser = test_ExtJSON.get_parser('''
        ["foo", "bar"],
        [1, 2, {"zab": 3}],
        ''')
        ctx = parser.values()
        rows = ctx.value()
        result = []
        _j_base.table(rows, self.row_handler, (result,))
        self.assertEqual([{"foo": 1, "bar": 2, "zab": 3}], result)

    def test_row(self):
        res = _j_base.row_to_map(["foo", "bar"], [1, 2])
        self.assertEqual({"foo": 1, "bar": 2}, res)

    def test_row_inlined(self):
        res = _j_base.row_to_map(["foo"], [1, {"bar": 2}])
        self.assertEqual({"foo": 1, "bar": 2}, res)


if __name__ == '__main__':
    unittest.main()
