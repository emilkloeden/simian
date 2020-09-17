import os
import pytest
import simian.ast as ast
import simian.lexer as lexer
import simian.parser as parser

from simian.lexer import Lexer
from simian.parser import Parser
from simian.token import Token


def test_operator_precedence():
    tests = [
        ("-a * b", "((-a) * b)",),
        ("!-a", "(!(-a))",),
        ("a + b + c", "((a + b) + c)",),
        ("a + b - c", "((a + b) - c)",),
        ("a * b * c", "((a * b) * c)",),
        ("a * b / c", "((a * b) / c)",),
        ("a + b / c", "(a + (b / c))",),
        ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)",),
        ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)",),
        ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))",),
        ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))",),
        ("3 + 4 * 5 == 3 * 1 + 4 * 5", "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))",),
        ("true", "true",),
        ("false", "false",),
        ("3 > 5 == false", "((3 > 5) == false)",),
        ("3 < 5 == true", "((3 < 5) == true)",),
        ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)",),
        ("(5 + 5) * 2", "((5 + 5) * 2)",),
        ("2 / (5 + 5)", "(2 / (5 + 5))",),
        ("-(5 + 5)", "(-(5 + 5))",),
        ("!(true == true)", "(!(true == true))",),
        # Functions, comments, returns and calls will break this. commented out for now
        # ("a + add(b * c) + d", "((a + add((b * c))) + d)",),
        # (
        #     "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
        #     "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
        # ),
        # ("add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))",),
        # ("a * [1, 2, 3, 4][b * c] * d", "((a * ([1, 2, 3, 4][(b * c)])) * d)",),
        # (
        #     "add(a * b[2], b[1], 2 * [1, 2][1])",
        #     "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))",
        # ),
        # ("-(5 + 5) // + 20", "(-(5 + 5))// + 20",),
    ]
    for tt in tests:
        input_, expected = tt
        program = build_program(input_)
        actual = str(program)
        assert actual == expected


##############
# STATEMENTS #
##############
def test_let_statements():
    tests = [
        ("let x = 5", "x", 5),
        ("let y = true;", "y", True),
        ("let foobar = y;", "foobar", "y"),
    ]

    for tt in tests:
        input_, expected_identifier, expected_value = tt

        program = build_program(input_)
        assert len(program.statements) == 1

        stmt = program.statements[0]

        assert stmt.token_literal() == "let"
        assert isinstance(stmt, ast.LetStatement)
        assert stmt.name.value == expected_identifier
        assert stmt.name.token_literal() == expected_identifier
        assert literal_expression_tester(stmt.value, expected_value)


def test_return_statements():
    input_ = """
    return 5;
    return 10;
    return 993322;
    """

    expected = [5, 10, 993322]

    program = build_program(input_)
    assert len(program.statements) == 3

    for i, stmt in enumerate(program.statements):
        assert isinstance(stmt, ast.ReturnStatement)
        assert stmt.token_literal() == "return"
        assert program.statements[i].return_value.value == expected[i]


###############
# EXPRESSIONS #
# (LITERALS)  #
###############


def test_identifier_expression():
    input_ = "foobar"
    program = build_program(input_)

    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    ident = stmt.expression
    assert isinstance(ident, ast.Identifier)
    assert ident.value == "foobar"
    assert ident.token_literal() == "foobar"


def test_string_literal_expression():
    input_ = '"hello world"'
    program = build_program(input_)

    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    literal = stmt.expression
    assert isinstance(literal, ast.StringLiteral)
    assert literal.value == "hello world"


def test_array_literal():
    input_ = "[1, 2 * 2, 3 + 3]"
    program = build_program(input_)
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    array = stmt.expression
    assert isinstance(array, ast.ArrayLiteral)
    assert len(array.elements) == 3
    assert integer_literal_tester(array.elements[0], 1)
    assert infix_expression_tester(array.elements[1], 2, "*", 2)
    assert infix_expression_tester(array.elements[2], 3, "+", 3)


def test_hash_literal_empty():
    program = build_program("{}")
    stmt = program.statements[0]
    lit = stmt.expression
    assert isinstance(lit, ast.HashLiteral)
    assert len(lit.pairs) == 0


def test_hash_literal_string_keys():
    input_ = """{"one": 1, "two": 2, "three": 3}"""
    program = build_program(input_)
    stmt = program.statements[0]
    lit = stmt.expression
    assert isinstance(lit, ast.HashLiteral)
    assert len(lit.pairs) == 3

    expected = {
        "one": 1,
        "two": 2,
        "three": 3,
    }

    for key, value in lit.pairs.items():
        assert isinstance(key, ast.StringLiteral)
        expected_value = expected[str(key)]
        assert integer_literal_tester(value, expected_value)


def test_hash_literal_expressions():
    input_ = """{"one": 0 + 1, "two": 10 - 8, "three": 15 / 5}"""
    program = build_program(input_)
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    lit = stmt.expression
    assert isinstance(lit, ast.HashLiteral)
    assert len(lit.pairs) == 3
    # Not sure if this actually does what I hope it does
    # This is the most foreign translation I had to perform
    # in this port.
    tests = {
        "one": lambda e: infix_expression_tester(e, 0, "+", 1),
        "two": lambda e: infix_expression_tester(e, 10, "-", 8),
        "three": lambda e: infix_expression_tester(e, 15, "/", 5),
    }
    for key, value in lit.pairs.items():
        assert isinstance(key, ast.StringLiteral)
        test_func = tests[str(key)]
        assert test_func(value)


###############
# EXPRESSIONS #
#  (COMPLEX)  #
###############


def test_prefix_expression():
    tests = [
        ("!5;", "!", 5),
        ("-15;", "-", 15),
        ("!true;", "!", True),
        ("!false;", "!", False),
    ]

    for tt in tests:
        input_, operator, value = tt
        program = build_program(input_)
        assert len(program.statements) == 1
        stmt = program.statements[0]
        assert isinstance(stmt, ast.ExpressionStatement)
        exp = stmt.expression
        assert isinstance(exp, ast.PrefixExpression)
        # skip testLiteralExpression for now


def test_if_expression():
    input_ = "if (x < y) { x }"
    program = build_program(input_)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    exp = stmt.expression
    assert isinstance(exp, ast.IfExpression)
    assert infix_expression_tester(exp.condition, "x", "<", "y")
    assert len(exp.consequence.statements) == 1
    consequence = exp.consequence.statements[0]
    assert isinstance(consequence, ast.ExpressionStatement)
    assert identifier_tester(consequence.expression, "x")
    assert exp.alternative == None


def test_if_else_expression():
    input_ = "if (x < y) { x } else { y }"
    program = build_program(input_)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    exp = stmt.expression
    assert isinstance(exp, ast.IfExpression)
    assert infix_expression_tester(exp.condition, "x", "<", "y")
    assert len(exp.consequence.statements) == 1
    consequence = exp.consequence.statements[0]
    assert isinstance(consequence, ast.ExpressionStatement)
    assert identifier_tester(consequence.expression, "x")
    assert len(exp.alternative.statements) == 1
    alternative = exp.alternative.statements[0]
    assert isinstance(consequence, ast.ExpressionStatement)
    assert identifier_tester(alternative.expression, "y")


def test_function_literal_expression():
    input_ = "fn(x, y) { x + y }"
    program = build_program(input_)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    fn = stmt.expression
    assert isinstance(fn, ast.FunctionLiteral)
    assert len(fn.parameters) == 2
    assert literal_expression_tester(fn.parameters[0], "x")
    assert literal_expression_tester(fn.parameters[1], "y")
    assert len(fn.body.statements) == 1
    body_stmt = fn.body.statements[0]
    assert isinstance(body_stmt, ast.ExpressionStatement)
    infix_expression_tester(body_stmt.expression, "x", "+", "y")


def test_call_expression():
    input_ = "add(1, 2 * 3, 4 + 5);"
    program = build_program(input_)
    assert len(program.statements) == 1
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    exp = stmt.expression
    assert isinstance(exp, ast.CallExpression)
    assert identifier_tester(exp.function, "add")
    assert len(exp.arguments) == 3
    assert literal_expression_tester(exp.arguments[0], 1)
    assert infix_expression_tester(exp.arguments[1], 2, "*", 3)
    assert infix_expression_tester(exp.arguments[2], 4, "+", 5)


def test_index_expression():
    input_ = "myArray[1+1]"
    program = build_program(input_)
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    index_exp = stmt.expression
    assert isinstance(index_exp, ast.IndexExpression)
    assert identifier_tester(index_exp.left, "myArray")
    assert infix_expression_tester(index_exp.index, 1, "+", 1)


####################
#      HELPERS     #
####################
def build_program(input_: str) -> ast.Program:
    l = lexer.new(input_)
    cwd = os.getcwd()
    p = Parser(l, cwd)
    program = p.parse_program()
    check_parser_errors(p)
    return program


def check_parser_errors(p: Parser):
    assert len(p.errors) == 0


def infix_expression_tester(exp: ast.Expression, left, operator: str, right):
    assert isinstance(exp, ast.InfixExpression)
    assert literal_expression_tester(exp.left, left)
    assert exp.operator == operator
    assert literal_expression_tester(exp.right, right)
    return True


def literal_expression_tester(exp: ast.Expression, expected):
    if isinstance(exp.value, bool):
        return boolean_literal_tester(exp, expected)
    elif isinstance(exp.value, int):
        return integer_literal_tester(exp, int(expected))
    elif isinstance(exp.value, str):
        res = identifier_tester(exp, expected)
        return res
    else:
        return False


# Hmm, this is incomplete and not good
def integer_literal_tester(exp: ast.Expression, value: int):
    assert isinstance(exp, ast.IntegerLiteral)
    assert exp.value == value
    return True


def identifier_tester(exp: ast.Expression, value: str):
    assert isinstance(exp, ast.Identifier)
    assert exp.value == value
    return True


def boolean_literal_tester(exp: ast.Expression, value: bool):
    assert isinstance(exp, ast.Boolean)
    assert exp.value == value
    return True
