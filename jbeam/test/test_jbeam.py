import unittest

from jbeam import ExtJSONParser, JbeamVisitor, EvalBase, Switch, Table
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
_j_base = EvalBase()


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
    def test_table(self):
        parser = test_ExtJSON.get_parser('''
        ["foo", "bar"],
        [1, 2, 3],
        ''')
        ctx = parser.values()
        prop_map, inlined_src = next(_j_base.table(ctx, Table()))
        self.assertEqual({'foo': 1, 'bar': 2}, prop_map)
        # exra values treated as inlined props:
        self.assertEqual('3', inlined_src)

    def test_table_shared_prop(self):
        parser = test_ExtJSON.get_parser('''
        [/*header*/ "foo", "bar"],
        // #1 comment
        {/* #2 shared prop*/ "zab": "cat"}
        [1, 2, 3],
        ''')
        ctx = parser.values()
        table = Table()
        prop_map, inlined_src = next(_j_base.table(ctx, table))

        shared_prop = table.chain_list[0]
        self.assertEqual(1, shared_prop.id)
        self.assertEqual('// #1 comment', shared_prop.src)

        shared_prop = table.chain_list[1]
        self.assertEqual(2, shared_prop.id)
        self.assertEqual('{/* #2 shared prop*/ "zab": "cat"}', shared_prop.src)

        self.assertEqual({'foo': 1, 'bar': 2}, prop_map)
        self.assertEqual('3', inlined_src)

    def test_table_inlined_prop(self):
        parser = test_ExtJSON.get_parser('''
        ["foo", "bar"],
        [1, 2, {"zab": 3}],
        ''')
        ctx = parser.values()
        prop_map, inlined_src = next(_j_base.table(ctx, Table()))
        self.assertEqual({"foo": 1, "bar": 2, "zab": 3}, prop_map)
        self.assertEqual('{"zab": 3}', inlined_src)

    def test_row(self):
        res = _j_base.row_to_map(["foo", "bar"], [1, 2])
        self.assertEqual({"foo": 1, "bar": 2}, res)

    def test_row_inlined(self):
        res = _j_base.row_to_map(["foo"], [1, {"bar": 2}])
        self.assertEqual({"foo": 1, "bar": 2}, res)


from jbeam import Table


class TableTestCase(unittest.TestCase):
    def test(self):
        t = Table()
        item = {'foo': 1}
        t.assign_to_last_prop(item)
        pkey = t._pid_key
        self.assertEqual(0, item[pkey])
        t.add_prop('//comment row')
        item2 = {'bar': {}}
        t.assign_to_last_prop(item2)
        self.assertEqual(1, item2[pkey])
        pass

    def test_counter(self):
        t = Table()
        item = {'foo': 1}
        t.assign_to_last_prop(item)
        pkey = t._pid_key
        prop_id = item[pkey]
        self.assertEqual(0, prop_id)
        self.assertEqual(1, t.counter[str(prop_id)])

        t.add_prop('//comment row')
        item2 = {'bar': {}}
        t.assign_to_last_prop(item2)
        prop_id = item2[pkey]
        self.assertEqual(1, prop_id)
        self.assertEqual(1, t.counter[str(prop_id)])

        item3 = {'zab': 123}
        t.assign_to_last_prop(item3)
        prop_id = item3[pkey]
        self.assertEqual(1, prop_id)
        self.assertEqual(2, t.counter[str(prop_id)])
        pass


if __name__ == '__main__':
    unittest.main()
