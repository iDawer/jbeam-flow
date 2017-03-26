import collections
from itertools import islice
from typing import Iterator, Tuple

from .ext_json import ExtJSONParser, ExtJSONEvaluator
from .misc import Switch, visitor_mixins, ExtDict


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


class Table:
    class Prop:
        id = 0
        src = ""

    class PropList(list):
        def add(self):
            """

            :rtype: Table.Prop
            """
            prop = Table.Prop()
            self.append(prop)
            return prop

    def __init__(self):
        self.chain_list = self.PropList()
        self._pid_key = "prop_id"
        self.max_id = 0
        self.counter = collections.Counter()

    def add_prop(self, src):
        """
        Adds next shared property to and tracks it's id.
        Ids start from 1, default 0 is a root of the chain.
        """
        self.max_id += 1
        prop_item = self.chain_list.add()
        prop_item.id = self.max_id
        prop_item.src = src
        return prop_item

    def assign_to_last_prop(self, item):
        item[self._pid_key] = self.max_id
        self.counter[str(self.max_id)] += 1

    # @property
    # def pid_key(self):
    #     """Item's access key to shared property id"""
    #     return self._pid_key

    def update_counter(self, items: list):
        self.counter.clear()
        self.counter.update(items)


class JbeamBase(ExtJSONEvaluator, visitor_mixins.Helper):
    def table(self, rows_ctx: ExtJSONParser.ValuesContext, table: Table = None) -> Iterator[Tuple[ExtDict, str]]:
        table = table or Table()

        rows = rows_ctx.value()
        rows_iter = iter(rows)
        header = next(rows_iter).accept(self)
        assert isinstance(header, list)
        _ValueArrayContext = ExtJSONParser.ValueArrayContext
        _ValueObjectContext = ExtJSONParser.ValueObjectContext
        for row_ctx in rows_iter:
            self.process_comments_before(row_ctx, table)
            with Switch.Inst(row_ctx) as case:
                if case(_ValueArrayContext):
                    row = row_ctx.accept(self)
                    prop_map = self.row_to_map(header, row)
                    inlined_props_src = self.get_inlined_props_src(header, row_ctx)
                    yield (prop_map, inlined_props_src)
                elif case(_ValueObjectContext):
                    src = self.get_src_text_replaced(row_ctx)
                    table.add_prop(src)
                else:
                    # other types in the table not supported, ignore them
                    pass

    @staticmethod
    def process_comments_before(ctx, table):
        stream = ctx.parser.getTokenStream()
        for token in stream.getHiddenTokensToLeft(ctx.start.tokenIndex):
            if token.type == ExtJSONParser.COMMENT_LINE or token.type == ExtJSONParser.COMMENT_BLOCK:
                table.add_prop(token.text)

    @staticmethod
    def row_to_map(header: list, row: list) -> ExtDict:
        map_ = ExtDict(zip(header, row))
        sliced = islice(row, len(header), None)
        inlined_maps = (x for x in sliced if isinstance(x, dict))
        for imap in inlined_maps:
            map_.update(imap)
        return map_

    # override ExtJSONEvaluator.visitObject to use ExtDict instead of dict
    def visitObject(self, ctx: ExtJSONParser.ObjectContext) -> ExtDict:
        ctx_pairs = ctx.pairs()
        if ctx_pairs:
            pairs = self.visitPairs(ctx_pairs)
            return ExtDict(pairs)
        return ExtDict()

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
