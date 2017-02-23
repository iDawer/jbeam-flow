from ..jb import jbeamParser


class Json:
    def visitBoolean(self, ctx: jbeamParser.BooleanContext):
        return ctx.val.type == jbeamParser.TRUE


class Helper:
    @staticmethod
    def lock_rot_scale(obj):
        obj.lock_rotation = (True, True, True)
        obj.lock_rotation_w = True
        obj.lock_rotations_4d = True
        obj.lock_scale = (True, True, True)

    @staticmethod
    def get_src_text_replaced(ctx, subctx, placeholder):
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

