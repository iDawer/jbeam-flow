from antlr4.tree.Tree import TerminalNodeImpl
# from ..jb import jbeamParser, jbeamVisitor
from ..ext_json import ExtJSONVisitor, ExtJSONParser
from . import Switch


class Json(ExtJSONVisitor):
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

    def visitValueObject(self, ctx: ExtJSONParser.ValueObjectContext):
        return self.visitObject(ctx.object())

    def visitValueArray(self, ctx: ExtJSONParser.ValueArrayContext):
        return self.visitArray(ctx.array())

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


class Helper:
    @staticmethod
    def lock_rot_scale(obj):
        obj.lock_rotation = (True, True, True)
        obj.lock_rotation_w = True
        obj.lock_rotations_4d = True
        obj.lock_scale = (True, True, True)

    @staticmethod
    def lock_transform(obj):
        obj.lock_location = (True, True, True)
        Helper.lock_rot_scale(obj)

    @staticmethod
    def get_src_text_replaced(ctx, subctx=None, placeholder=None):
        src_int = ctx.getSourceInterval()
        src = []
        stream = ctx.parser.getTokenStream()
        if subctx is not None:
            sub_int = subctx.getSourceInterval()
            src.append(stream.getText((src_int[0], sub_int[0] - 1)).replace('$', '$$'))
            src.append(placeholder)
            src.append(stream.getText((sub_int[1] + 1, src_int[1])).replace('$', '$$'))
        else:
            src.append(stream.getText(src_int).replace('$', '$$'))
        return ''.join(src)
