import unittest
from itertools import islice
from typing import List

if '.' in __name__:
    from .ext_json import ExtJSONParser, ExtJSONEvaluator
    from .misc import Switch
else:
    # for testing purpose
    from ext_json import ExtJSONParser, ExtJSONEvaluator
    from misc import Switch

# fast links
_ValuesContext = ExtJSONParser.ValuesContext
_ValueContext = ExtJSONParser.ValueContext
_ValueArrayContext = ExtJSONParser.ValueArrayContext
_ValueObjectContext = ExtJSONParser.ValueObjectContext
# ValueAtomContext = ExtJSONParser.ValueAtomContext
_ValueStringContext = ExtJSONParser.ValueStringContext


class JbeamVisitor(ExtJSONEvaluator):
    def visit_jbeam(self, ctx: ExtJSONParser.ObjectContext):
        return super().visitObject(ctx)

    def visit_parts(self, ctx: ExtJSONParser.PairsContext):
        return super().visitPairs(ctx)

    def visit_part(self, ctx: ExtJSONParser.PairContext):
        return super().visitPair(ctx)

    def visit_part_value(self, ctx: ExtJSONParser.ValueObjectContext):
        return super().visitValueObject(ctx)

    def visit_sections(self, ctx: ExtJSONParser.PairsContext):
        return super().visitPairs(ctx)

    def visit_section(self, ctx: ExtJSONParser.PairContext):
        return super().visitPair(ctx)

    def visit_section_value(self, ctx: ExtJSONParser.ValueObjectContext):
        return super().visitValueObject(ctx)


class JbeamBase(ExtJSONEvaluator):
    def table(self, rows_ctx: ExtJSONParser.ValuesContext):
        rows = rows_ctx.value()
        rows_iter = iter(rows)
        header = next(rows_iter).accept(self)
        assert isinstance(header, list)
        return header, rows_iter
        # for idx, row_ctx in rows_iter:
        #     row_handler(header, row_ctx, *args)

    @staticmethod
    def row_to_map(header: list, row: list) -> dict:
        map = dict(zip(header, row))
        sliced = islice(row, len(header), None)
        inlined_maps = filter(lambda x: isinstance(x, dict), sliced)
        for imap in inlined_maps:
            map.update(imap)
        return map

    pass

    # def visit(self, ctx: ExtJSONParser.ValueArrayContext):
    #     return self.visit_table(ctx)
    #
    # def visit_table(self, ctx: ExtJSONParser.ValueArrayContext):
    #     return super().visitValueArray(ctx)
    #
    # def visit_rows(self, ctx: ExtJSONParser.ValuesContext):
    #     return super().visitValues(ctx)
    #
    # def visit_property_row(self, ctx: ExtJSONParser.ValueObjectContext):
    #     return super().visitValueObject(ctx)
    #
    # def visit_value_row(self, ctx: ExtJSONParser.ValueArrayContext):
    #     return super().visitValueArray(ctx)


# define tests if on top level
# probably buggy hack
if '.' not in __name__:
    Parser = ExtJSONParser

    from ext_json.test_ExtJSON import get_parser

    jbv = JbeamVisitor()
    j_base = JbeamBase()


    def fast_res(src, parser_method, visitor_method):
        parser = get_parser(src)
        ctx = getattr(parser, getattr(parser_method, '__name__'))()
        return visitor_method(ctx)


    class JbeamVisitorTestCase(unittest.TestCase):
        def test_jbeam(self):
            result = fast_res('{"p1":{}, "p2":{}}', Parser.object, jbv.visit_jbeam)
            self.assertEqual({"p1": {}, "p2": {}}, result)

        def test_parts(self):
            result = fast_res('"p1":{}, "p2":{}', Parser.pairs, jbv.visit_parts)
            self.assertEqual([("p1", {}), ("p2", {})], result)

        def test_part(self):
            res = fast_res('"part": {}', Parser.pair, jbv.visit_part)
            self.assertEqual(("part", {}), res)

        def test_part_value(self):
            res = fast_res('{"slotType": "abc"}', Parser.value, jbv.visit_part_value)
            self.assertEqual({"slotType": "abc"}, res)
            pass


    class JbeamBaseTestCase(unittest.TestCase):
        @staticmethod
        def row_handler(header, row_ctx, array: list):
            with Switch.Inst(row_ctx) as case:
                if case(_ValueArrayContext):
                    row = row_ctx.accept(j_base)
                    map = j_base.row_to_map(header, row)
                elif case(_ValueObjectContext):
                    map = row_ctx.accept(j_base)
                else:
                    # other types in a table not supported, ignore them
                    return
            array.append(map)

        def test_table(self):
            parser = get_parser('''
            ["foo", "bar"],
            [1, 2, 3],
            ''')
            ctx = parser.values()
            rows = ctx.value()
            result = []
            j_base.table(rows, self.row_handler, (result,))
            self.assertEqual([{"foo": 1, "bar": 2}], result)

        def test_row_inlined_map(self):
            parser = get_parser('''
            ["foo", "bar"],
            [1, 2, {"zab": 3}],
            ''')
            ctx = parser.values()
            rows = ctx.value()
            result = []
            j_base.table(rows, self.row_handler, (result,))
            self.assertEqual([{"foo": 1, "bar": 2, "zab": 3}], result)

        def test_row(self):
            res = j_base.row_to_map(["foo", "bar"], [1, 2])
            self.assertEqual({"foo": 1, "bar": 2}, res)

        def test_row_inlined(self):
            res = j_base.row_to_map(["foo"], [1, {"bar": 2}])
            self.assertEqual({"foo": 1, "bar": 2}, res)


    if __name__ == '__main__':
        unittest.main()
