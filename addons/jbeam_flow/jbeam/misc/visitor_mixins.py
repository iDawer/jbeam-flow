from itertools import islice


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

    @staticmethod
    def get_inlined_props_src(header: list, row_ctx):
        val_ctxs = row_ctx.array().values().value()
        inl_prop_ctxs = list(islice(val_ctxs, len(header), None))
        if inl_prop_ctxs:
            first = inl_prop_ctxs[0]
            last = inl_prop_ctxs[-1]
            src_int = first.start.tokenIndex, last.stop.tokenIndex
            stream = row_ctx.parser.getTokenStream()
            src = stream.getText(src_int).replace('$', '$$')
            return src
        return None
