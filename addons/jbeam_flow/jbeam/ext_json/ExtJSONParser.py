# Generated from C:/Users/Dawer/Documents/ANTLR playground\ExtJSON.g4 by ANTLR 4.6
# encoding: utf-8
from antlr4 import *
from io import StringIO

def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3\20")
        buf.write("<\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\3\2\3\2\3\2\3\2\3\2\3\2\5\2\27\n\2\3\3\3\3\5\3\33")
        buf.write("\n\3\3\3\3\3\3\4\6\4 \n\4\r\4\16\4!\3\5\3\5\3\5\3\5\3")
        buf.write("\6\3\6\5\6*\n\6\3\6\3\6\3\7\6\7/\n\7\r\7\16\7\60\3\b\3")
        buf.write("\b\3\b\3\b\3\b\3\b\3\b\5\b:\n\b\3\b\2\2\t\2\4\6\b\n\f")
        buf.write("\16\2\2?\2\26\3\2\2\2\4\30\3\2\2\2\6\37\3\2\2\2\b#\3\2")
        buf.write("\2\2\n\'\3\2\2\2\f.\3\2\2\2\169\3\2\2\2\20\21\5\4\3\2")
        buf.write("\21\22\7\2\2\3\22\27\3\2\2\2\23\24\5\n\6\2\24\25\7\2\2")
        buf.write("\3\25\27\3\2\2\2\26\20\3\2\2\2\26\23\3\2\2\2\27\3\3\2")
        buf.write("\2\2\30\32\7\6\2\2\31\33\5\6\4\2\32\31\3\2\2\2\32\33\3")
        buf.write("\2\2\2\33\34\3\2\2\2\34\35\7\7\2\2\35\5\3\2\2\2\36 \5")
        buf.write("\b\5\2\37\36\3\2\2\2 !\3\2\2\2!\37\3\2\2\2!\"\3\2\2\2")
        buf.write("\"\7\3\2\2\2#$\7\f\2\2$%\7\13\2\2%&\5\16\b\2&\t\3\2\2")
        buf.write("\2\')\7\b\2\2(*\5\f\7\2)(\3\2\2\2)*\3\2\2\2*+\3\2\2\2")
        buf.write("+,\7\t\2\2,\13\3\2\2\2-/\5\16\b\2.-\3\2\2\2/\60\3\2\2")
        buf.write("\2\60.\3\2\2\2\60\61\3\2\2\2\61\r\3\2\2\2\62:\7\f\2\2")
        buf.write("\63:\7\r\2\2\64:\5\4\3\2\65:\5\n\6\2\66:\7\3\2\2\67:\7")
        buf.write("\4\2\28:\7\5\2\29\62\3\2\2\29\63\3\2\2\29\64\3\2\2\29")
        buf.write("\65\3\2\2\29\66\3\2\2\29\67\3\2\2\298\3\2\2\2:\17\3\2")
        buf.write("\2\2\b\26\32!)\609")
        return buf.getvalue()


class ExtJSONParser ( Parser ):

    grammarFileName = "ExtJSON.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'null'", "'true'", "'false'", "'{'", 
                     "'}'", "'['", "']'", "'\"'", "':'" ]

    symbolicNames = [ "<INVALID>", "NULL", "TRUE", "FALSE", "LCURLY", "RCURLY", 
                      "LBRACK", "RBRACK", "QUOT", "COLON", "STRING", "NUMBER", 
                      "COMMENT_BLOCK", "COMMENT_LINE", "WS" ]

    RULE_json = 0
    RULE_object = 1
    RULE_pairs = 2
    RULE_pair = 3
    RULE_array = 4
    RULE_values = 5
    RULE_value = 6

    ruleNames =  [ "json", "object", "pairs", "pair", "array", "values", 
                   "value" ]

    EOF = Token.EOF
    NULL=1
    TRUE=2
    FALSE=3
    LCURLY=4
    RCURLY=5
    LBRACK=6
    RBRACK=7
    QUOT=8
    COLON=9
    STRING=10
    NUMBER=11
    COMMENT_BLOCK=12
    COMMENT_LINE=13
    WS=14

    def __init__(self, input:TokenStream):
        super().__init__(input)
        self.checkVersion("4.6")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class JsonContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def object(self):
            return self.getTypedRuleContext(ExtJSONParser.ObjectContext,0)


        def EOF(self):
            return self.getToken(ExtJSONParser.EOF, 0)

        def array(self):
            return self.getTypedRuleContext(ExtJSONParser.ArrayContext,0)


        def getRuleIndex(self):
            return ExtJSONParser.RULE_json

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitJson" ):
                return visitor.visitJson(self)
            else:
                return visitor.visitChildren(self)




    def json(self):

        localctx = ExtJSONParser.JsonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_json)
        try:
            self.state = 20
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ExtJSONParser.LCURLY]:
                self.enterOuterAlt(localctx, 1)
                self.state = 14
                self.object()
                self.state = 15
                self.match(ExtJSONParser.EOF)
                pass
            elif token in [ExtJSONParser.LBRACK]:
                self.enterOuterAlt(localctx, 2)
                self.state = 17
                self.array()
                self.state = 18
                self.match(ExtJSONParser.EOF)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ObjectContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pairs(self):
            return self.getTypedRuleContext(ExtJSONParser.PairsContext,0)


        def getRuleIndex(self):
            return ExtJSONParser.RULE_object

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitObject" ):
                return visitor.visitObject(self)
            else:
                return visitor.visitChildren(self)




    def object(self):

        localctx = ExtJSONParser.ObjectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_object)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22
            self.match(ExtJSONParser.LCURLY)
            self.state = 24
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ExtJSONParser.STRING:
                self.state = 23
                self.pairs()


            self.state = 26
            self.match(ExtJSONParser.RCURLY)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PairsContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExtJSONParser.PairContext)
            else:
                return self.getTypedRuleContext(ExtJSONParser.PairContext,i)


        def getRuleIndex(self):
            return ExtJSONParser.RULE_pairs

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPairs" ):
                return visitor.visitPairs(self)
            else:
                return visitor.visitChildren(self)




    def pairs(self):

        localctx = ExtJSONParser.PairsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_pairs)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 28
                self.pair()
                self.state = 31 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==ExtJSONParser.STRING):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PairContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.key = None # Token
            self.val = None # ValueContext

        def STRING(self):
            return self.getToken(ExtJSONParser.STRING, 0)

        def value(self):
            return self.getTypedRuleContext(ExtJSONParser.ValueContext,0)


        def getRuleIndex(self):
            return ExtJSONParser.RULE_pair

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPair" ):
                return visitor.visitPair(self)
            else:
                return visitor.visitChildren(self)




    def pair(self):

        localctx = ExtJSONParser.PairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 33
            localctx.key = self.match(ExtJSONParser.STRING)
            self.state = 34
            self.match(ExtJSONParser.COLON)
            self.state = 35
            localctx.val = self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ArrayContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def values(self):
            return self.getTypedRuleContext(ExtJSONParser.ValuesContext,0)


        def getRuleIndex(self):
            return ExtJSONParser.RULE_array

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArray" ):
                return visitor.visitArray(self)
            else:
                return visitor.visitChildren(self)




    def array(self):

        localctx = ExtJSONParser.ArrayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_array)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 37
            self.match(ExtJSONParser.LBRACK)
            self.state = 39
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ExtJSONParser.NULL) | (1 << ExtJSONParser.TRUE) | (1 << ExtJSONParser.FALSE) | (1 << ExtJSONParser.LCURLY) | (1 << ExtJSONParser.LBRACK) | (1 << ExtJSONParser.STRING) | (1 << ExtJSONParser.NUMBER))) != 0):
                self.state = 38
                self.values()


            self.state = 41
            self.match(ExtJSONParser.RBRACK)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ValuesContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ExtJSONParser.ValueContext)
            else:
                return self.getTypedRuleContext(ExtJSONParser.ValueContext,i)


        def getRuleIndex(self):
            return ExtJSONParser.RULE_values

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValues" ):
                return visitor.visitValues(self)
            else:
                return visitor.visitChildren(self)




    def values(self):

        localctx = ExtJSONParser.ValuesContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_values)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 44 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 43
                self.value()
                self.state = 46 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << ExtJSONParser.NULL) | (1 << ExtJSONParser.TRUE) | (1 << ExtJSONParser.FALSE) | (1 << ExtJSONParser.LCURLY) | (1 << ExtJSONParser.LBRACK) | (1 << ExtJSONParser.STRING) | (1 << ExtJSONParser.NUMBER))) != 0)):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ValueContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ExtJSONParser.RULE_value

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class ValueAtomContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExtJSONParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(ExtJSONParser.NUMBER, 0)
        def NULL(self):
            return self.getToken(ExtJSONParser.NULL, 0)
        def TRUE(self):
            return self.getToken(ExtJSONParser.TRUE, 0)
        def FALSE(self):
            return self.getToken(ExtJSONParser.FALSE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValueAtom" ):
                return visitor.visitValueAtom(self)
            else:
                return visitor.visitChildren(self)


    class ValueObjectContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExtJSONParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def object(self):
            return self.getTypedRuleContext(ExtJSONParser.ObjectContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValueObject" ):
                return visitor.visitValueObject(self)
            else:
                return visitor.visitChildren(self)


    class ValueStringContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExtJSONParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def STRING(self):
            return self.getToken(ExtJSONParser.STRING, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValueString" ):
                return visitor.visitValueString(self)
            else:
                return visitor.visitChildren(self)


    class ValueArrayContext(ValueContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a ExtJSONParser.ValueContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def array(self):
            return self.getTypedRuleContext(ExtJSONParser.ArrayContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValueArray" ):
                return visitor.visitValueArray(self)
            else:
                return visitor.visitChildren(self)



    def value(self):

        localctx = ExtJSONParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_value)
        try:
            self.state = 55
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [ExtJSONParser.STRING]:
                localctx = ExtJSONParser.ValueStringContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 48
                self.match(ExtJSONParser.STRING)
                pass
            elif token in [ExtJSONParser.NUMBER]:
                localctx = ExtJSONParser.ValueAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 49
                self.match(ExtJSONParser.NUMBER)
                pass
            elif token in [ExtJSONParser.LCURLY]:
                localctx = ExtJSONParser.ValueObjectContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 50
                self.object()
                pass
            elif token in [ExtJSONParser.LBRACK]:
                localctx = ExtJSONParser.ValueArrayContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 51
                self.array()
                pass
            elif token in [ExtJSONParser.NULL]:
                localctx = ExtJSONParser.ValueAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 52
                self.match(ExtJSONParser.NULL)
                pass
            elif token in [ExtJSONParser.TRUE]:
                localctx = ExtJSONParser.ValueAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 53
                self.match(ExtJSONParser.TRUE)
                pass
            elif token in [ExtJSONParser.FALSE]:
                localctx = ExtJSONParser.ValueAtomContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 54
                self.match(ExtJSONParser.FALSE)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





