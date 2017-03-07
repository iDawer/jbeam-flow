from ..jb import jbeamParser, jbeamVisitor


class Json(jbeamVisitor):
    def visitBoolean(self, ctx: jbeamParser.BooleanContext):
        if ctx.exception is not None:
            return None
        return ctx.val.type == jbeamParser.TRUE

    def visitGenericString(self, ctx: jbeamParser.GenericStringContext):
        if ctx.exception is not None:
            return None
        return ctx.string_item

    def visitAtom(self, ctx: jbeamParser.AtomContext):
        if ctx.exception is not None:
            raise ValueError("bad atom value: '%s'" % ctx.getText())
        if ctx.NULL() is not None:
            return None
        node = ctx.NUMBER()
        if node is not None:
            return float(node.getText())
        node = ctx.boolean()
        if node is not None:
            return self.visitBoolean(node)

    def visitString(self, ctx: jbeamParser.StringContext):
        return self.visitGenericString(ctx.genericString())

    def visitArray(self, ctx: jbeamParser.ArrayContext):
        array = []
        append = array.append
        for valCtx in ctx.value():
            append(valCtx.accept(self))
        return array

    def visitArrayValue(self, ctx: jbeamParser.ArrayValueContext):
        return self.visitArray(ctx.array())

    def visitKeyVal(self, ctx: jbeamParser.KeyValContext):
        return ctx.key.accept(self), ctx.val.accept(self)

    def visitObj(self, ctx: jbeamParser.ObjContext):
        pairs = []
        append = pairs.append
        for keyValCtx in ctx.keyVal():
            append(keyValCtx.accept(self))
        obj = dict(pairs)
        return obj

    def visitObjectValue(self, ctx: jbeamParser.ObjectValueContext):
        return ctx.obj().accept(self)


class Helper:
    @staticmethod
    def lock_rot_scale(obj):
        obj.lock_rotation = (True, True, True)
        obj.lock_rotation_w = True
        obj.lock_rotations_4d = True
        obj.lock_scale = (True, True, True)

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
