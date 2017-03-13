import unittest
from antlr4 import InputStream, CommonTokenStream
from ExtJSONLexer import ExtJSONLexer as Lexer
from ExtJSONParser import ExtJSONParser as Parser


def get_stream(str: str) -> CommonTokenStream:
    lexer = Lexer(InputStream(str))
    stream = CommonTokenStream(lexer)
    stream.fill()  # force lazy init
    return stream


class TestLexer(unittest.TestCase):
    def test_string(self):
        str = '"2this \\n is string"'
        token = get_stream(str).LT(1)
        self.assertEqual(token.type, Lexer.STRING)
        self.assertEqual(token.text, str)

    # def test_string_keyword(self):
    #     str = '"nodes"'
    #     token = get_stream(str).LT(1)
    #     self.assertEqual(token.type, Lexer.Str_nodes)

    def test_number(self):
        stream = get_stream('0 -1 23 3.4 -5.666')
        token = stream.LT(1)
        self.assertEqual(token.type, Lexer.NUMBER)
        self.assertEqual(token.text, '0')

        token = stream.LT(2)
        self.assertEqual(token.type, Lexer.NUMBER)
        self.assertEqual(token.text, '-1')

        token = stream.LT(3)
        self.assertEqual(token.type, Lexer.NUMBER)
        self.assertEqual(token.text, '23')

        token = stream.LT(4)
        self.assertEqual(token.type, Lexer.NUMBER)
        self.assertEqual(token.text, '3.4')

        token = stream.LT(5)
        stream.consume()
        self.assertEqual(token.type, Lexer.NUMBER)
        self.assertEqual(token.text, '-5.666')

    # @unittest.skip('Number specials is not implemented')
    # def test_number_specials(self):
    #     stream = get_stream('0 -1 23 3.4 -5.666 FLT_MAX MINUS_FLT_MAX')
    #     token = stream.LT(6)
    #     self.assertEqual(token.type, Lexer.NUMBER)
    #     self.assertEqual(token.text, 'FLT_MAX')
    #
    #     token = stream.LT(7)
    #     self.assertEqual(token.type, Lexer.NUMBER)
    #     self.assertEqual(token.text, 'MINUS_FLT_MAX')

    def test_comment_line(self):
        stream = get_stream(' 76//comment 8 \n-4')
        hidden_tokens = stream.getHiddenTokensToRight(1)
        self.assertGreaterEqual(len(hidden_tokens), 1, 'Hidden tokens not found')
        comment_token = hidden_tokens[0]
        self.assertEqual(comment_token.type, Lexer.COMMENT_LINE)
        self.assertEqual(comment_token.text, '//comment 8 ')

    def test_comment_block(self):
        stream = get_stream(' 1.2345/*"commented\n{} string"*/67')
        hidden_tokens = stream.getHiddenTokensToRight(1)
        self.assertGreaterEqual(len(hidden_tokens), 1, 'Hidden tokens not found')
        comment_token = hidden_tokens[0]
        self.assertEqual(comment_token.type, Lexer.COMMENT_BLOCK)
        self.assertEqual(stream.LA(2), Lexer.NUMBER, 'NUMBER was consumed by comment')


def get_parser(str: str) -> Parser:
    stream = get_stream(str)
    parser = Parser(stream)

    return parser


class TestParser(unittest.TestCase):
    def test_json(self):
        parser = get_parser('\n\r{\t"part1":{} \r\n"part2"\n:\n{\n}} ')
        tree = parser.json()
        self.assertEqual(tree.getText(), '{"part1":{}"part2":{}}<EOF>')

    def test_section_slotType(self):
        parser = get_parser('''
{
    "example_part": {
        "information":{
        }
        "slotType" : "main",
        "slots": [
            ["type", "default", "description"]
        ],
        "refNodes":[
            ["ref:", "back:", "left:", "up:"]
        ],
        "flexbodies": [
             ["mesh", "[group]:", "nonFlexMaterials"],
        ],
        "nodes": [
            ["id", "posX", "posY", "posZ"],
        ],
        "beams": [
            ["id1:", "id2:"],
        ],
        "triangles": [
            ["id1:","id2:","id3:"],
        ],
    }
}
        ''')
        tree = parser.json()
        part = tree.object().pairs().getChild(0, Parser.PairContext)
        self.assertIsNotNone(part)
        self.assertEqual('"example_part"', part.key.text)
        sections = part.val.object().pairs()
        self.assertIsNotNone(sections)
        section_slotType = sections.getChild(1, Parser.PairContext)
        self.assertIsNotNone(section_slotType)
        self.assertIsNotNone(section_slotType.val)
        self.assertEqual('"main"', section_slotType.val.getText())

    def test_SecHydros(self):
        parser = get_parser('''
            {"part1":{
                "hydros": [
                    ["id1:","id2:"],
                    {"beamDamp":2080}
                    ["t4","t11",{"inputSource":"brake"}],
                ],
            } }
        ''')
        tree = parser.json()
        self.assertEqual(
            '{"part1":{"hydros":[["id1:""id2:"]{"beamDamp":2080}["t4""t11"{"inputSource":"brake"}]]}}<EOF>',
            tree.getText())

    def test_keyword(self):
        parser = get_parser('"nodes":[[]]')
        ctx = parser.pair()
        self.assertIsInstance(ctx, Parser.PairContext)
        self.assertEqual(ctx.getText(), '"nodes":[[]]')

    def test_gemeric_string_keyword(self):
        parser = get_parser('"some key": "nodes"')
        ctx = parser.pair()
        self.assertIsNone(ctx.val.exception)
        self.assertIsInstance(ctx.val, Parser.ValueStringContext)

    def test_genericString(self):
        parser = get_parser('"simple text"')
        ctx = parser.value()
        self.assertIsInstance(ctx, Parser.ValueStringContext)
        token = ctx.STRING()
        self.assertIsNotNone(token)
        self.assertEqual('"simple text"', token.getText())


if __name__ == '__main__':
    unittest.main()
