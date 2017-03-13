from antlr4 import CommonTokenStream
from . import jbeamParser


def preprocess(stream: CommonTokenStream):
    stream.fill()
    token = stream.LT(1)
    while token.type != jbeamParser.EOF:
        # catch variables starting with '$'
        if token.type == jbeamParser.STRING and token.text.startswith('"$'):
            prev_t = stream.LB(1)
            if prev_t is None or prev_t.type != jbeamParser.LBRACK:
                # ToDo preprocess: rewrite var with default from variables section
                token.text = "0"
                token.type = jbeamParser.NUMBER
        stream.consume()
        token = stream.LT(1)

    stream.reset()
    return stream
