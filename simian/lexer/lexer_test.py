import pytest

from simian.lexer import new
from simian.token import TokenType


def test_next_token():
    input = """let five = 5;
    let ten = 10;
	
	let add = fn(x, y) {
		x + y;
	};
	
	let result = add(five, ten);
	!-/*5;
	5 < 10 > 5;
	
	if (5 < 10) {
		return true;
	} else {
		return false;
	}

	10 == 10;
	10 != 9;
	"foobar"
	"foo bar"
	[1, 2];
	{"foo": "bar"}
	3 % 2
	let a = 1; // bye
	let hello = import("./hello.mo");
	true || false && true;
    """

    tests = [
        (TokenType.LET, "let"),
        (TokenType.IDENT, "five"),
        (TokenType.ASSIGN, "="),
        (TokenType.INT, "5"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "ten"),
        (TokenType.ASSIGN, "="),
        (TokenType.INT, "10"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "add"),
        (TokenType.ASSIGN, "="),
        (TokenType.FUNCTION, "fn"),
        (TokenType.LPAREN, "("),
        (TokenType.IDENT, "x"),
        (TokenType.COMMA, ","),
        (TokenType.IDENT, "y"),
        (TokenType.RPAREN, ")"),
        (TokenType.LBRACE, "{"),
        (TokenType.IDENT, "x"),
        (TokenType.PLUS, "+"),
        (TokenType.IDENT, "y"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.RBRACE, "}"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "result"),
        (TokenType.ASSIGN, "="),
        (TokenType.IDENT, "add"),
        (TokenType.LPAREN, "("),
        (TokenType.IDENT, "five"),
        (TokenType.COMMA, ","),
        (TokenType.IDENT, "ten"),
        (TokenType.RPAREN, ")"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.BANG, "!"),
        (TokenType.MINUS, "-"),
        (TokenType.SLASH, "/"),
        (TokenType.ASTERISK, "*"),
        (TokenType.INT, "5"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.INT, "5"),
        (TokenType.LT, "<"),
        (TokenType.INT, "10"),
        (TokenType.GT, ">"),
        (TokenType.INT, "5"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.IF, "if"),
        (TokenType.LPAREN, "("),
        (TokenType.INT, "5"),
        (TokenType.LT, "<"),
        (TokenType.INT, "10"),
        (TokenType.RPAREN, ")"),
        (TokenType.LBRACE, "{"),
        (TokenType.RETURN, "return"),
        (TokenType.TRUE, "true"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.RBRACE, "}"),
        (TokenType.ELSE, "else"),
        (TokenType.LBRACE, "{"),
        (TokenType.RETURN, "return"),
        (TokenType.FALSE, "false"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.RBRACE, "}"),
        (TokenType.INT, "10"),
        (TokenType.EQ, "=="),
        (TokenType.INT, "10"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.INT, "10"),
        (TokenType.NOT_EQ, "!="),
        (TokenType.INT, "9"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.STRING, "foobar"),
        (TokenType.STRING, "foo bar"),
        (TokenType.LBRACKET, "["),
        (TokenType.INT, "1"),
        (TokenType.COMMA, ","),
        (TokenType.INT, "2"),
        (TokenType.RBRACKET, "]"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.LBRACE, "{"),
        (TokenType.STRING, "foo"),
        (TokenType.COLON, ":"),
        (TokenType.STRING, "bar"),
        (TokenType.RBRACE, "}"),
        (TokenType.INT, "3"),
        (TokenType.MODULO, "%"),
        (TokenType.INT, "2"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "a"),
        (TokenType.ASSIGN, "="),
        (TokenType.INT, "1"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.COMMENT, " bye"),
        (TokenType.LET, "let"),
        (TokenType.IDENT, "hello"),
        (TokenType.ASSIGN, "="),
        (TokenType.IMPORT, "import"),
        (TokenType.LPAREN, "("),
        (TokenType.STRING, "./hello.mo"),
        (TokenType.RPAREN, ")"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.TRUE, "true"),
        (TokenType.OR, "||"),
        (TokenType.FALSE, "false"),
        (TokenType.AND, "&&"),
        (TokenType.TRUE, "true"),
        (TokenType.SEMICOLON, ";"),
        (TokenType.EOF, ""),
    ]

    l = new(input)

    for i, tt in enumerate(tests):
        tok = l.next_token()
        assert tok.token_type == tt[0] and tok.literal == tt[1]

