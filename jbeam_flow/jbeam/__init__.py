from itertools import islice

from .ext_json import ExtJSONParser, ExtJSONEvaluator
from .misc import Switch


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
    def table(self, rows_ctx: ExtJSONParser.ValuesContext) -> (list, list):
        rows = rows_ctx.value()
        rows_iter = iter(rows)
        header = next(rows_iter).accept(self)
        assert isinstance(header, list)
        return header, rows_iter

    @staticmethod
    def row_to_map(header: list, row: list) -> dict:
        map_ = dict(zip(header, row))
        sliced = islice(row, len(header), None)
        inlined_maps = filter(lambda x: isinstance(x, dict), sliced)
        for imap in inlined_maps:
            map_.update(imap)
        return map_

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
