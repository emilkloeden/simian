import enum

__all__ = ["Token", "TokenType", "lookup_ident"]


class TokenType(enum.Enum):
    # TokenType Constants
    ILLEGAL = "ILLEGAL"
    EOF = "EOF"

    # Identifiers + literals
    IDENT = "IDENT"  # add, foobar, x, y, ...
    INT = "INT"  # 123456
    STRING = "STRING"
    COMMENT = "COMMENT"

    # Operators
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    BANG = "!"
    ASTERISK = "*"
    SLASH = "/"
    MODULO = "%"
    AND = "&&"
    OR = "||"

    LT = "<"
    GT = ">"

    EQ = "=="
    NOT_EQ = "!="

    # Delimiters
    COLON = ":"
    COMMA = ","
    SEMICOLON = ";"

    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"

    # Keywords
    FUNCTION = "FUNCTION"
    LET = "LET"
    TRUE = "TRUE"
    FALSE = "FALSE"
    IF = "IF"
    ELSE = "ELSE"
    RETURN = "RETURN"
    IMPORT = "IMPORT"
    WHILE = "WHILE"


keywords = {
    "fn": TokenType.FUNCTION,
    "let": TokenType.LET,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "return": TokenType.RETURN,
    "import": TokenType.IMPORT,
    "while": TokenType.WHILE,
}


def lookup_ident(ident: str) -> str:
    # print(f"LOOKING UP IDENT: {ident} in keywords")
    if ident in keywords:
        # print(f"FOUND {keywords[ident]}")
        return keywords[ident]
    # print(f"{ident} NOT FOUND in keywords, treating as identifier")
    return TokenType.IDENT


class Token:
    def __init__(self, token_type: str, literal: str):
        self.token_type: str = token_type
        self.literal: str = literal

