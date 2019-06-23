// Extended version of JSON format.
// Comments: C-style, multi-line, and single-line comments are supported: //... and /* ... */
// Commas: All commas are optional, but it is advised to only omit the commas at the end of lines.
grammar ExtJSON;

json
    :   object EOF
    |   array EOF
    ;

object
    :   '{' pairs? '}'
    ;

pairs
    :   pair+
    ;

pair
    :   key=STRING ':' val=value
    ;

array
    :   '[' values? ']'
    ;

values
    :   value+
    ;

value
    :   STRING		# ValueString
    |   NUMBER		# ValueAtom
    |   object     	# ValueObject
    |   array  		# ValueArray
    |   NULL		# ValueAtom
    |   TRUE		# ValueAtom
    |   FALSE		# ValueAtom
    ;

NULL :  'null' ;
TRUE :  'true' ;
FALSE : 'false' ;

LCURLY : '{' ;  RCURLY : '}' ;
LBRACK : '[' ;  RBRACK : ']' ;
QUOT : '"' ;
COLON : ':' ;

STRING : '"' (ESC | ~["\\])* '"' ;
fragment ESC :   '\\' (["\\/bfnrt] | UNICODE) ;
fragment UNICODE : 'u' HEX HEX HEX HEX ;
fragment HEX : [0-9a-fA-F] ;
NUMBER
    :   '-'? INT '.' INT EXP?   // 1.35, 1.35E-9, 0.3, -4.5
    |   '-'? INT EXP            // 1e10 -3e4
    |   '-'? INT                // -3, 45
    ;
fragment INT :   '0' | '0'..'9' '0'..'9'* ;
fragment EXP :   [Ee] [+\-]? INT ;
COMMENT_BLOCK
    :   '/*' .*? '*/' -> channel(HIDDEN)
    ;
COMMENT_LINE
    :   '//' ~[\r\n]* -> channel(HIDDEN)
    ;
WS  :   [ ,\t\n\r]+  -> channel(HIDDEN)
    ;
