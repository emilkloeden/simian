from simian.token import TokenType, Token

__all__ = [
    "Node",
    "Statement",
    "Expression",
    "Program",
    "LetStatement",
    "ReturnStatement",
    "Identifier",
    "ExpressionStatement",
    "IntegerLiteral",
    "Boolean",
    "StringLiteral",
    "FunctionLiteral",
    "PrefixExpression",
    "InfixExpression",
    "IfExpression",
    "BlockStatement",
    "CallExpression",
    "ArrayLiteral",
    "IndexExpression",
    "HashLiteral",
    "ImportExpression",
    "Comment",
    "WhileStatement",
]


class Node:
    def token_literal(self):
        raise NotImplementedError()

    def __str__(self):
        return ""


class Statement(Node):
    pass


class Expression(Node):
    pass


class Program(Node):
    def __init__(self):
        self.statements = []

    def token_literal(self):
        if len(self.statements):
            return self.statements[0].token_literal()
        else:
            return ""

    def __str__(self):
        return "".join([str(s) for s in self.statements])


######################
#     STATEMENTS     #
######################
class LetStatement(Statement):
    def __init__(self, token: TokenType):
        self.token = token
        self.name = None
        self.value = None

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        out = f"{self.token_literal()} {str(self.name)} = "
        if self.value is not None:
            out += str(self.value)
        out += ";"
        return out


class ReturnStatement(Statement):
    def __init__(self, token: Token):
        self.token = token
        self.return_value: Expression

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return f"{self.token.literal} {self.return_value};"


class WhileStatement(Statement):
    def __init__(self, token: Token):
        self.token = token
        self.condition: Expression
        self.body: Expression

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return f"{self.token.literal} ({self.condition}) {{{str(self.body)}}};"


class Comment(Statement):
    def __init__(self, token: Token, value: Expression):
        self.token = token
        self.value = value

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return f"//{self.value};"


class ExpressionStatement(Statement):
    def __init__(self, token: Token):
        self.token = token
        self.expression: Expression

    def __str__(self):
        return str(self.expression) if self.expression is not None else ""

    def statement_node(self):
        pass

    def token_literal(self):
        return self.token.literal


class BlockStatement(Statement):
    def __init__(self, token: Token):
        self.token = token
        self.statements: List[Statement] = []

    def __str__(self):
        out = f""
        for stmt in self.statements:
            out += str(stmt)
        return out

    def token_literal(self):
        return self.token.literal


#######################
#     EXPRESSIONS     #
#######################
class Identifier(Expression):
    def __init__(self, token: Token, value: str):
        self.token = token
        self.value = value

    def __str__(self):
        return self.value

    def expression_node(self):
        pass

    def token_literal(self):
        return self.token.literal


class IntegerLiteral(Expression):
    def __init__(self, token: Token):
        self.token = token
        self.value: int

    def __str__(self):
        return str(self.value) if self.value is not None else ""

    def token_literal(self):
        return self.token.literal


class Boolean(Expression):
    def __init__(self, token: Token, value: bool):
        self.token = token
        self.value = value

    def __str__(self):
        return str(self.token.literal)

    def token_literal(self):
        return self.token.literal


class StringLiteral(Expression):
    def __init__(self, token: Token, value: str):
        self.token = token
        self.value = value

    def __str__(self):
        return str(self.value)

    def token_literal(self):
        return self.token.literal


class FunctionLiteral(Expression):
    def __init__(self, token: Token):
        self.token = token
        self.parameters: List[Identifier] = []
        self.body: BlockStatement = None  # see if can make not None

    def __str__(self):
        return f"""{self.token_literal()}({", ".join([str(p) for p in self.parameters])}) {{{str(self.body)}}}"""

    def token_literal(self):
        return self.token.literal


class ArrayLiteral(Expression):
    def __init__(self, token: Token):
        self.token = token
        self.elements: List[Expression] = []

    def __str__(self):
        return f"""[{", ".join([str(e) for e in self.elements])}]"""

    def token_literal(self):
        return self.token.literal


class HashLiteral(Expression):
    def __init__(self, token: Token):
        self.token = token
        self.pairs = {}

    def __str__(self):
        pairs = []
        for key, val in self.pairs.items():
            pairs.append(f"{str(key)}:{str(val)}")
        return f"""{{{", ".join(pairs)}}}"""

    def token_literal(self):
        return self.token.literal


class PrefixExpression(Expression):
    def __init__(self, token: Token, operator: str):
        self.token = token
        self.operator = operator
        self.right: Expression

    def __str__(self):
        return f"({self.operator}{str(self.right)})"

    def token_literal(self):
        return self.token.literal


class InfixExpression(Expression):
    def __init__(self, token: Token, operator: str, left: Expression):
        self.token = token
        self.operator = operator
        self.left = left
        self.right: Expression

    def __str__(self):
        return f"({str(self.left)} {self.operator} {str(self.right)})"

    def token_literal(self):
        return self.token.literal


class IfExpression(Expression):
    def __init__(self, token: Token):
        self.token = token
        self.condition: Expression
        self.consequence: BlockStatement = None  # TODO: check if can get rid of both these = None statements
        self.alternative: BlockStatement = None

    def __str__(self):
        out = f"if{str(self.condition)} {{ {str(self.consequence)} }}"
        if self.alternative is not None:
            out += f"else {str(self.alternative)}"
        return out

    def token_literal(self):
        return self.token.literal


class CallExpression(Expression):
    def __init__(self, token: Token, function: Expression):
        self.token = token
        self.function = function
        self.arguments: List[Expression] = []

    def __str__(self):
        args = [str(arg) for arg in self.arguments]
        return f"{str(self.function)}({', '.join(args)})"

    def token_literal(self):
        return self.token.literal


class IndexExpression(Expression):
    def __init__(self, token: Token, left: Expression, index: Expression):
        self.token = token
        self.left = left
        self.index = index

    def __str__(self):
        if self.index is None:
            return f"({str(self.left)}[None])"
        return f"({str(self.left)}[{str(self.index)}])"

    def token_literal(self):
        return self.token.literal


class ImportExpression(Expression):
    def __init__(self, token: Token, requestor: Expression):
        self.token = token
        self.requestor = requestor
        self.name: Expression

    def token_literal(self):
        return self.token.literal

    def __str__(self):
        return f'{self.token_literal()}("{self.name}")'

