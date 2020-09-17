from __future__ import annotations

import enum
from typing import List

import simian.ast as ast
from simian.lexer import Lexer
from simian.token import TokenType

__all__ = ["Parser", "Precedence"]


class Precedence(enum.Enum):
    LOWEST = 0
    OR = 1
    AND = 2
    EQUALS = 3
    LESSGREATER = 4
    SUM = 5
    PRODUCT = 6
    MODULO = 7
    PREFIX = 8
    CALL = 9
    INDEX = 10


precedences = {
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NOT_EQ: Precedence.EQUALS,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.SLASH: Precedence.PRODUCT,
    TokenType.ASTERISK: Precedence.PRODUCT,
    TokenType.MODULO: Precedence.MODULO,
    TokenType.AND: Precedence.AND,
    TokenType.OR: Precedence.OR,
    TokenType.LPAREN: Precedence.CALL,
    TokenType.LBRACKET: Precedence.INDEX,
}

# Hrmm...
# type (
# 	prefixParseFn func() ast.Expression
# 	infixParseFn  func(ast.Expression) ast.Expression
# )


class Parser:
    def __init__(self, lexer: Lexer, current_dir: str) -> None:
        self.lexer: Lexer = lexer
        self.current_dir: str = current_dir
        self.errors: [str] = []

        self.current_token: TokenType = self.lexer.next_token()
        self.peek_token: TokenType = self.lexer.next_token()

        self.prefix_parse_fns = {
            TokenType.IDENT: self.parse_identifier,
            TokenType.INT: self.parse_integer_literal,
            TokenType.BANG: self.parse_prefix_expression,
            TokenType.MINUS: self.parse_prefix_expression,
            TokenType.TRUE: self.parse_boolean,
            TokenType.FALSE: self.parse_boolean,
            TokenType.LPAREN: self.parse_grouped_expression,
            TokenType.IF: self.parse_if_expression,
            TokenType.FUNCTION: self.parse_function_literal,
            TokenType.STRING: self.parse_string_literal,
            TokenType.LBRACKET: self.parse_array_literal,
            TokenType.LBRACE: self.parse_hash_literal,
            TokenType.IMPORT: self.parse_import_expression,
        }

        self.infix_parse_fns = {
            TokenType.PLUS: self.parse_infix_expression,
            TokenType.MINUS: self.parse_infix_expression,
            TokenType.SLASH: self.parse_infix_expression,
            TokenType.ASTERISK: self.parse_infix_expression,
            TokenType.MODULO: self.parse_infix_expression,
            TokenType.EQ: self.parse_infix_expression,
            TokenType.NOT_EQ: self.parse_infix_expression,
            TokenType.AND: self.parse_infix_expression,
            TokenType.OR: self.parse_infix_expression,
            TokenType.LT: self.parse_infix_expression,
            TokenType.GT: self.parse_infix_expression,
            TokenType.LPAREN: self.parse_call_expression,
            TokenType.LBRACKET: self.parse_index_expression,
        }

    def next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def parse_program(self) -> ast.Program:
        program = ast.Program()

        while self.current_token.token_type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            self.next_token()

        return program

    # STATEMENTS
    def parse_statement(self) -> ast.Statement:
        if self.current_token.token_type == TokenType.COMMENT:
            return self.parse_comment_statement()
        if self.current_token.token_type == TokenType.LET:
            return self.parse_let_statement()
        elif self.current_token.token_type == TokenType.RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()

    def parse_comment_statement(self):
        return ast.Comment(self.current_token, self.current_token.literal)

    def parse_return_statement(self):
        stmt = ast.ReturnStatement(self.current_token)
        self.next_token()
        stmt.return_value = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return stmt

    def parse_expression_statement(self):
        stmt = ast.ExpressionStatement(self.current_token)
        stmt.expression = self.parse_expression(Precedence.LOWEST)
        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()
        return stmt

    def parse_let_statement(self) -> ast.LetStatement:
        stmt = ast.LetStatement(self.current_token)

        if not self.expect_peek(TokenType.IDENT):
            return None

        stmt.name = ast.Identifier(self.current_token, self.current_token.literal)

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        self.next_token()
        stmt.value = self.parse_expression(Precedence.LOWEST)

        if self.peek_token_is(TokenType.SEMICOLON):
            self.next_token()

        return stmt

    def parse_block_statement(self) -> ast.BlockStatement:
        block = ast.BlockStatement(self.current_token)
        block.statements: List[ast.Statement] = []
        self.next_token()

        while not self.current_token_is(TokenType.RBRACE) and not self.current_token_is(
            TokenType.EOF
        ):
            stmt = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)
            self.next_token()

        return block

    # EXPRESSIONS
    def parse_expression(self, precedence: int) -> ast.Expression:
        prefix = self.prefix_parse_fns.get(self.current_token.token_type, None)
        # print(f"`prefix`: {prefix.__name__ if prefix is not None else prefix}, current token: {str(self.current_token)}")
        if prefix is None:
            # print(f"`prefix` is none: self.current_token.token_type: {self.current_token.token_type}")
            self.no_prefix_parse_fn_error(self.current_token.token_type)
            return None
        left_exp = prefix()

        while (
            not self.peek_token_is(TokenType.SEMICOLON)
            and precedence.value < self.peek_precedence().value
        ):
            infix = self.infix_parse_fns.get(self.peek_token.token_type, None)
            # print(f"`infix`: {infix.__name__ if infix is not None else infix}, current token: {str(self.current_token)}")

            if infix is None:
                return left_exp
            self.next_token()

            left_exp = infix(left_exp)
        return left_exp

    def parse_boolean(self) -> ast.Boolean:
        return ast.Boolean(self.current_token, self.current_token_is(TokenType.TRUE))

    def parse_identifier(self) -> ast.Identifier:
        return ast.Identifier(self.current_token, self.current_token.literal)

    def parse_integer_literal(self) -> ast.Expression:
        lit = ast.IntegerLiteral(self.current_token)
        try:
            lit.value = int(self.current_token.literal)
            return lit
        except ValueError:
            self.errors.append(
                f"Could not parse {self.current_token.literal} as integer"
            )
            return None

    def parse_string_literal(self) -> ast.StringLiteral:
        return ast.StringLiteral(self.current_token, self.current_token.literal)

    def parse_array_literal(self) -> ast.Expression:
        array = ast.ArrayLiteral(self.current_token)
        array.elements = self.parse_expression_list(TokenType.RBRACKET)
        return array

    def parse_prefix_expression(self) -> ast.Expression:
        expression = ast.PrefixExpression(
            self.current_token, self.current_token.literal
        )
        self.next_token()
        expression.right = self.parse_expression(Precedence.PREFIX)
        return expression

    def parse_infix_expression(self, left: ast.Expression) -> ast.Expression:
        expression = ast.InfixExpression(
            self.current_token, self.current_token.literal, left
        )
        precedence = self.current_precedence()
        self.next_token()
        expression.right = self.parse_expression(precedence)
        return expression

    def parse_grouped_expression(self) -> ast.Expression:
        self.next_token()
        expression = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return expression

    def parse_if_expression(self) -> ast.Expression:
        expression = ast.IfExpression(self.current_token)
        if not self.expect_peek(TokenType.LPAREN):
            return None

        self.next_token()
        expression.condition = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        if not self.expect_peek(TokenType.LBRACE):
            return None

        expression.consequence = self.parse_block_statement()

        if self.peek_token_is(TokenType.ELSE):
            self.next_token()

            if not self.expect_peek(TokenType.LBRACE):
                return None

            expression.alternative = self.parse_block_statement()

        return expression

    def parse_function_literal(self):
        lit = ast.FunctionLiteral(self.current_token)

        if not self.expect_peek(TokenType.LPAREN):
            return None

        lit.parameters = self.parse_function_parameters()

        if not self.expect_peek(TokenType.LBRACE):
            return None

        lit.body = self.parse_block_statement()

        return lit

    def parse_function_parameters(self) -> List[ast.Identifier]:
        identifiers: List[ast.Identifier] = []

        if self.peek_token_is(TokenType.RPAREN):
            self.next_token()
            return identifiers

        self.next_token()

        ident = ast.Identifier(self.current_token, self.current_token.literal)
        identifiers.append(ident)

        while self.peek_token_is(TokenType.COMMA):
            self.next_token()
            self.next_token()
            ident = ast.Identifier(self.current_token, self.current_token.literal)
            identifiers.append(ident)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return identifiers

    def parse_call_expression(self, function: ast.Expression) -> ast.Expression:
        exp = ast.CallExpression(self.current_token, function)
        exp.arguments = self.parse_expression_list(TokenType.RPAREN)
        return exp

    def parse_index_expression(self, left: ast.Expression) -> ast.Expression:
        exp = ast.IndexExpression(self.current_token, left)
        self.next_token()
        exp.index = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RBRACKET):
            return None

        return exp

    def parse_hash_literal(self) -> ast.Expression:
        lit = ast.HashLiteral(self.current_token)

        while not self.peek_token_is(TokenType.RBRACE):
            self.next_token()
            key = self.parse_expression(Precedence.LOWEST)

            if not self.expect_peek(TokenType.COLON):
                return None

            self.next_token()
            value = self.parse_expression(Precedence.LOWEST)

            lit.pairs[key] = value

            if not self.peek_token_is(TokenType.RBRACE) and not self.expect_peek(
                TokenType.COMMA
            ):
                return None

        if not self.expect_peek(TokenType.RBRACE):
            return None

        return lit

    def parse_import_expression(self) -> ast.Expression:
        expression = ast.ImportExpression(self.current_token, self.current_dir)

        if not self.expect_peek(TokenType.LPAREN):
            return None

        self.next_token()

        expression.name = self.parse_expression(Precedence.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None

        return expression

    ###########
    # HELPERS #
    ###########
    def current_token_is(self, tokenType: TokenType) -> bool:
        return self.current_token.token_type == tokenType

    def current_precedence(self):
        return precedences.get(self.current_token.token_type, Precedence.LOWEST)

    def expect_peek(self, tokenType: TokenType) -> bool:
        if self.peek_token_is(tokenType):
            self.next_token()
            return True
        else:
            self.peek_error(tokenType)
            return False

    def peek_token_is(self, tokenType: TokenType) -> bool:
        return self.peek_token.token_type == tokenType

    def peek_error(self, tokenType: TokenType) -> None:
        error_message = f"Expected next token to be {tokenType}, got {self.peek_token.token_type} instead."
        # print(error_message)
        self.errors.append(error_message)

    def peek_precedence(self) -> int:
        return precedences.get(self.peek_token.token_type, Precedence.LOWEST)

    def no_prefix_parse_fn_error(self, tokenType: TokenType):
        self.errors.append(f"No prefix parse function for {tokenType} found.")

    def parse_expression_list(self, endTokenType: TokenType) -> List[ast.Expression]:
        expressions: List[ast.Expression] = []

        if self.peek_token_is(endTokenType):
            self.next_token()
            return expressions

        self.next_token()
        expressions.append(self.parse_expression(Precedence.LOWEST))

        while self.peek_token_is(TokenType.COMMA):
            self.next_token()
            self.next_token()
            expressions.append(self.parse_expression(Precedence.LOWEST))

        if not self.expect_peek(endTokenType):
            return None

        return expressions
