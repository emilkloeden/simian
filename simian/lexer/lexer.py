import string
from simian.token import Token, TokenType, lookup_ident

__all__ = ["Lexer", "new"]


class Lexer:
    def __init__(self, input_: str) -> None:
        self.input_ = input_
        self.position = 0
        self.read_position = 0
        self.ch = ""

    def read_char(self) -> None:
        if self.read_position >= len(self.input_):
            self.ch = "\0"
        else:
            self.ch = self.input_[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> str:
        if self.read_position >= len(self.input_):
            return 0
        else:
            return self.input_[self.read_position]

    def skip_whitespace(self):
        while self.ch in [" ", "\t", "\n", "\r"]:
            self.read_char()

    def next_token(self) -> TokenType:
        tok: Token
        self.skip_whitespace()
        if self.ch == "=":
            if self.peek_char() == "=":
                ch = self.ch
                self.read_char()
                literal = str(ch) + str(self.ch)
                tok = Token(TokenType.EQ, literal)
            else:
                tok = Token(TokenType.ASSIGN, self.ch)

        elif self.ch == "+":
            tok = Token(TokenType.PLUS, self.ch)
        elif self.ch == "-":
            tok = Token(TokenType.MINUS, self.ch)
        elif self.ch == "!":
            if self.peek_char() == "=":
                ch = self.ch
                self.read_char()
                literal = str(ch) + str(self.ch)
                tok = Token(TokenType.NOT_EQ, literal)
            else:
                tok = Token(TokenType.BANG, self.ch)

        elif self.ch == "/":
            if self.peek_char() == "/":
                self.read_char()  # skip over the next '/' char
                tok = Token(TokenType.COMMENT, self.read_line())
            else:
                tok = Token(TokenType.SLASH, self.ch)

        elif self.ch == "*":
            tok = Token(TokenType.ASTERISK, self.ch)
        elif self.ch == "%":
            tok = Token(TokenType.MODULO, self.ch)
        elif self.ch == "&":
            if self.peek_char() == "&":
                ch = self.ch
                self.read_char()
                literal = str(ch) + str(self.ch)
                tok = Token(TokenType.AND, literal)
            else:
                tok = Token(TokenType.ILLEGAL, self.ch)

        elif self.ch == "|":
            if self.peek_char() == "|":
                ch = self.ch
                self.read_char()
                literal = str(ch) + str(self.ch)
                tok = Token(TokenType.OR, literal)
            else:
                tok = Token(TokenType.ILLEGAL, self.ch)

        elif self.ch == "<":
            tok = Token(TokenType.LT, self.ch)
        elif self.ch == ">":
            tok = Token(TokenType.GT, self.ch)
        elif self.ch == ";":
            tok = Token(TokenType.SEMICOLON, self.ch)
        elif self.ch == "(":
            tok = Token(TokenType.LPAREN, self.ch)
        elif self.ch == ")":
            tok = Token(TokenType.RPAREN, self.ch)
        elif self.ch == ",":
            tok = Token(TokenType.COMMA, self.ch)
        elif self.ch == "{":
            tok = Token(TokenType.LBRACE, self.ch)
        elif self.ch == "}":
            tok = Token(TokenType.RBRACE, self.ch)
        elif self.ch == '"':
            tok = Token(TokenType.STRING, self.read_string())
        elif self.ch == "[":
            tok = Token(TokenType.LBRACKET, self.ch)
        elif self.ch == "]":
            tok = Token(TokenType.RBRACKET, self.ch)
        elif self.ch == ":":
            tok = Token(TokenType.COLON, self.ch)
        elif self.ch == "\0":
            tok = Token(TokenType.EOF, "")
        else:
            if is_letter(self.ch):
                ident = self.read_identifier()
                tok = Token(lookup_ident(ident), ident)
                return tok
            elif is_digit(self.ch):
                tok = Token(TokenType.INT, self.read_number())
                return tok
            else:
                tok = Token(TokenType.ILLEGAL, self.ch)
        self.read_char()
        return tok

    def read_identifier(self) -> str:
        position = self.position
        while is_letter(self.ch):
            self.read_char()
            if self.ch == "\0":
                break

        return self.input_[position : self.position]

    def read_number(self) -> str:
        position = self.position
        while is_digit(self.ch):
            self.read_char()
            if self.ch == "\0":
                break
        return self.input_[position : self.position]

    def read_line(self) -> str:
        position = self.position + 1
        while True:
            self.read_char()
            if self.ch in ["\r", "\n", "\0"]:
                break
        return self.input_[position : self.position]

    def read_string(self) -> str:
        position = self.position + 1
        while True:
            self.read_char()
            if self.ch in ['"', "\0"]:
                break
        return self.input_[position : self.position]


def is_letter(ch: str) -> bool:
    return ch in string.ascii_letters or ch == "_"


def is_digit(ch: str) -> bool:
    return ch in string.digits


def new(input_: str) -> Lexer:
    l = Lexer(input_)
    l.read_char()
    return l
