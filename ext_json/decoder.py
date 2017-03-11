from antlr4.tree.Tree import TerminalNodeImpl
from ext_json import ExtJSONVisitor, ExtJSONParser
from misc import Switch


class ExtJSONEvaluator(ExtJSONVisitor):
    def visitObject(self, ctx: ExtJSONParser.ObjectContext):
        ctx_pairs = ctx.pairs()
        if ctx_pairs:
            pairs = self.visitPairs(ctx_pairs)
            return dict(pairs)
        return {}

    def visitPairs(self, ctx: ExtJSONParser.PairsContext):
        pairs = []
        append = pairs.append
        for pairCtx in ctx.pair():
            append(pairCtx.accept(self))
        return pairs

    def visitPair(self, ctx: ExtJSONParser.PairContext):
        return ctx.STRING().accept(self), ctx.val.accept(self)

    def visitArray(self, ctx: ExtJSONParser.ArrayContext):
        ctx_values = ctx.values()
        if ctx_values:
            return self.visitValues(ctx_values)
        return []

    def visitValues(self, ctx: ExtJSONParser.ValuesContext):
        array = []
        append = array.append
        for val_ctx in ctx.value():
            append(val_ctx.accept(self))
        return array

    def visitTerminal(self, tnode: TerminalNodeImpl):
        token = tnode.symbol
        with Switch(token.type) as case:
            if case(ExtJSONParser.STRING):
                return token.text.strip('"')
            elif case(ExtJSONParser.NUMBER):
                return float(token.text)
            elif case(ExtJSONParser.TRUE):
                return True
            elif case(ExtJSONParser.FALSE):
                return False
            elif case(ExtJSONParser.NULL):
                return None
        return super().visitTerminal(tnode)
