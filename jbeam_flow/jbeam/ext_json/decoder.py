from antlr4 import CommonTokenStream, InputStream
from antlr4.tree.Tree import TerminalNodeImpl

from . import ExtJSONVisitor, ExtJSONParser, ExtJSONLexer
from ..misc import Switch


def get_parse_tree(s: str) -> ExtJSONParser.JsonContext:
    lexer = ExtJSONLexer(InputStream(s))
    stream = CommonTokenStream(lexer)
    parser = ExtJSONParser(stream)
    return parser.json()


def load(s: str):
    json_ctx = get_parse_tree(s)
    result = json_ctx.accept(ExtJSONEvaluator())
    return result


class ExtJSONEvaluator(ExtJSONVisitor):
    def visitJson(self, ctx: ExtJSONParser.JsonContext):
        child_ctx = ctx.array()
        if child_ctx:
            return self.visitArray(child_ctx)
        child_ctx = ctx.object()
        if child_ctx:
            return self.visitObject(child_ctx)
        return None

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
