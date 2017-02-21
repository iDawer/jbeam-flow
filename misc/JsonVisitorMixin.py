from ..jb import jbeamParser


class JsonVisitorMixin:
    def visitBoolean(self, ctx: jbeamParser.BooleanContext):
        return ctx.val.type == jbeamParser.TRUE
