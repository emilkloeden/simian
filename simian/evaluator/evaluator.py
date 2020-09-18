from typing import List, Dict, Union
from pathlib import Path

import simian.ast as ast
import simian.lexer as lexer
import simian.objects as objects
from simian.token import TokenType
from simian.objects import ObjectType
from simian.parser import Parser

__all__ = ["evaluate"]


def evaluate(node: ast.Node, env: objects.Environment) -> objects.Object:
    # print(f"EVALUATING: node:<{node}>, type: <{type(node)}>")
    if isinstance(node, ast.Program):
        return evaluate_program(node, env)
    elif isinstance(node, ast.ExpressionStatement):
        return evaluate(node.expression, env)
    elif isinstance(node, ast.BlockStatement):
        return evaluate_block_statement(node, env)
    elif isinstance(node, ast.ReturnStatement):
        value = evaluate(node.return_value, env)
        if is_error(value):
            return value
        return objects.ReturnValue(value)
    elif isinstance(node, ast.LetStatement):
        val = evaluate(node.value, env)
        if is_error(val):
            return val
        env.set(node.name.value, val)
    elif isinstance(node, ast.IntegerLiteral):
        return objects.Integer(node.value)
    elif isinstance(node, ast.StringLiteral):
        return objects.String(node.value)
    elif isinstance(node, ast.ArrayLiteral):
        elements = evaluate_expressions(node.elements, env)
        if len(elements) == 1 and is_error(elements[0]):
            return elements[0]
        return objects.Array(elements)
    elif isinstance(node, ast.HashLiteral):
        return evaluate_hash_literal(node, env)
    elif isinstance(node, ast.Boolean):
        if node.value:
            return objects.Boolean(True)
        return objects.Boolean(False)
    elif isinstance(node, ast.PrefixExpression):
        right = evaluate(node.right, env)
        if is_error(right):
            return right
        return evaluate_prefix_expression(node.operator, right)
    elif isinstance(node, ast.InfixExpression):
        left = evaluate(node.left, env)
        if is_error(left):
            return left
        right = evaluate(node.right, env)
        if is_error(right):
            return right
        return evaluate_infix_expression(node.operator, left, right)
    elif isinstance(node, ast.IfExpression):
        return evaluate_if_expression(node, env)
    elif isinstance(node, ast.Identifier):
        return evaluate_identifier(node, env)
    elif isinstance(node, ast.FunctionLiteral):
        params = node.parameters
        body = node.body
        return objects.Function(params, body, env)
    elif isinstance(node, ast.CallExpression):
        function = evaluate(node.function, env)
        if is_error(function):
            return function
        args = evaluate_expressions(node.arguments, env)
        if len(args) == 1 and is_error(args[0]):
            return args[0]
        return apply_function(function, args)
    elif isinstance(node, ast.IndexExpression):
        left = evaluate(node.left, env)
        if is_error(left):
            return left
        index = evaluate(node.index, env)
        if is_error(index):
            return index
        return evaluate_index_expression(left, index)
    elif isinstance(node, ast.ImportExpression):
        return evaluate_import_expression(node, env)
    elif isinstance(node, ast.WhileStatement):
        return evaluate_while_statement(node, env)
    return None


def evaluate_program(program: ast.Program, env: objects.Environment) -> objects.Object:
    result: objects.Object = None

    for statement in program.statements:
        result = evaluate(statement, env)
        if isinstance(result, objects.ReturnValue):
            return result.value
        elif isinstance(result, objects.Error):
            return result
    return result


def evaluate_block_statement(
    block: ast.BlockStatement, env: objects.Environment
) -> objects.Object:
    result: objects.Object = None
    for statement in block.statements:
        result = evaluate(statement, env)
        if result is not None:
            rt = result.object_type()
            if rt in [ObjectType.RETURN_VALUE_OBJ, ObjectType.ERROR_OBJ]:
                return result
    return result


def evaluate_while_statement(stmt: ast.WhileStatement, env: objects.Environment):
    while True:
        evaluated = evaluate(stmt.condition, env)
        if is_error(evaluated) or evaluated is None:
            return evaluated
        if is_truthy(evaluated):
            consequence = evaluate(stmt.body, env)
            if is_error(consequence):
                return consequence
        else:
            break

    return None


def evaluate_expressions(
    expressions: List[ast.Expression], env: objects.Environment
) -> List[objects.Object]:
    result: List[objects.Object] = []
    for expression in expressions:
        evaluated = evaluate(expression, env)
        if is_error(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result


def evaluate_hash_literal(
    node: ast.HashLiteral, env: objects.Environment
) -> objects.Object:
    pairs: Dict[objects.HashKey, objects.HashPair] = {}

    for key_node, value_node in node.pairs.items():
        key = evaluate(key_node, env)
        if is_error(key):
            return key

        if not isinstance(key, objects.Hashable):
            return new_error(f"unusable as hash key: {key.object_type().value}")

        value = evaluate(value_node, env)
        if is_error(value):
            return value

        hashed = key.hash_key()
        pairs[hashed] = objects.HashPair(key, value)
    return objects.Hash(pairs)


def evaluate_prefix_expression(operator: str, right: objects.Object) -> objects.Object:
    if operator == "!":
        return evaluate_bang_operator_expression(right)
    elif operator == "-":
        return evaluate_minus_prefix_operator_expression(right)
    else:
        return new_error(
            f"unknown operator: {operator.value}{right.object_type().value.value}"
        )


def evaluate_infix_expression(
    operator: str, left: objects.Object, right: objects.Object
) -> objects.Object:
    if left.object_type() == right.object_type() == ObjectType.INTEGER_OBJ:
        return evaluate_integer_infix_expression(operator, left, right)
    elif left.object_type() == right.object_type() == ObjectType.STRING_OBJ:
        return evaluate_string_infix_expression(operator, left, right)
    elif left.object_type() == right.object_type() == ObjectType.ARRAY_OBJ:
        return evaluate_array_infix_expression(operator, left, right)
    elif operator == "==":
        return native_bool_to_boolean_object(left == right)
    elif operator == "!=":
        return native_bool_to_boolean_object(left != right)
    elif operator == "&&":
        if left.object_type() == right.object_type() == ObjectType.BOOLEAN_OBJ:
            return native_bool_to_boolean_object(left.value and right.value)
    elif operator == "||":
        if left.object_type() == right.object_type() == ObjectType.BOOLEAN_OBJ:
            return native_bool_to_boolean_object(left.value or right.value)

    elif left.object_type() != right.object_type():
        return new_error(
            f"type mismatch: {left.object_type().value} {operator} {right.object_type().value}"
        )
    return new_error(
        f"unknown operator: {left.object_type().value} {operator} {right.object_type().value}"
    )


def evaluate_if_expression(
    expression: ast.IfExpression, env: objects.Environment
) -> objects.Object:
    condition = evaluate(expression.condition, env)
    if is_error(condition):
        return condition
    if is_truthy(condition):
        return evaluate(expression.consequence, env)
    if expression.alternative is not None:
        return evaluate(expression.alternative, env)
    return objects.Null()


def evaluate_identifier(
    node: ast.Identifier, env: objects.Environment
) -> objects.Object:
    val = env.get(node.value)

    if val is not None:
        return val

    builtin = objects.BUILTINS.get(node.value, None)
    if builtin is not None:
        return builtin

    return new_error(f"identifier not found: {node.value}")


def evaluate_index_expression(
    left: objects.Object, index: objects.Object
) -> objects.Object:
    if (
        left.object_type() == ObjectType.ARRAY_OBJ
        and index.object_type() == ObjectType.INTEGER_OBJ
    ):
        return evaluate_array_index_expression(left, index)
    elif left.object_type() == ObjectType.HASH_OBJ:
        return evaluate_hash_index_expression(left, index)
    elif left.object_type() == ObjectType.MODULE:
        return evaluate_module_index_expression(left, index)
    return new_error(f"index operator not supported: {left.object_type().value}")


def evaluate_bang_operator_expression(right: objects.Object) -> objects.Object:
    if right is objects.Boolean(True):
        return objects.Boolean(False)
    elif right is objects.Boolean(False):
        return objects.Boolean(True)
    elif right is objects.Null():
        return objects.Boolean(True)
    else:
        return objects.Boolean(False)


def evaluate_minus_prefix_operator_expression(right: objects.Object) -> objects.Object:
    if right.object_type() != ObjectType.INTEGER_OBJ:
        return new_error(f"unknown operator: -{right.object_type().value}")

    return objects.Integer(-right.value)


def evaluate_integer_infix_expression(
    operator: str, left: objects.Object, right: objects.Object
) -> objects.Object:
    left_value = left.value
    right_value = right.value

    if operator == "+":
        return objects.Integer(left_value + right_value)
    elif operator == "-":
        return objects.Integer(left_value - right_value)
    elif operator == "*":
        return objects.Integer(left_value * right_value)
    elif operator == "/":
        return objects.Integer(left_value / right_value)
    elif operator == "%":
        return objects.Integer(left_value % right_value)
    elif operator == "<":
        return native_bool_to_boolean_object(left_value < right_value)
    elif operator == ">":
        return native_bool_to_boolean_object(left_value > right_value)
    elif operator == "==":
        return native_bool_to_boolean_object(left_value == right_value)
    elif operator == "!=":
        return native_bool_to_boolean_object(left_value != right_value)
    return new_error(
        f"unknown operator: {left.object_type().value} {operator} {right.object_type().value}"
    )


def evaluate_string_infix_expression(
    operator: str, left: objects.Object, right: objects.Object
) -> objects.Object:
    if operator != "+":
        return new_error(
            f"unknown operator: {left.object_type().value} {operator} {right.object_type().value}"
        )

    return objects.String(left.value + right.value)


def evaluate_array_infix_expression(
    operator: str, left: objects.Object, right: objects.Object
) -> objects.Object:
    if operator != "+":
        return new_error(
            f"unknown operator: {left.object_type().value} {operator} {right.object_type().value}"
        )

    return objects.Array(left.elements + right.elements)


def evaluate_array_index_expression(
    array: objects.Object, index: objects.Object
) -> objects.Object:
    idx = index.value

    if idx < 0 or idx > len(array.elements) - 1:
        return objects.Null()

    return array.elements[idx]


def evaluate_hash_index_expression(
    hash_obj: objects.Object, index: objects.Object
) -> objects.Object:
    if not isinstance(index, objects.Hashable):
        return new_error(f"unusable as hash key: {index.object_type().value}")

    pair = hash_obj.pairs.get(index.hash_key(), None)
    if pair is None:
        return objects.Null()

    return pair.value


def evaluate_module_index_expression(
    hash_obj: objects.Object, index: objects.Object
) -> objects.Object:
    return evaluate_hash_index_expression(hash_obj.attrs, index)


def evaluate_import_expression(
    exp: ast.ImportExpression, env: objects.Environment
) -> objects.Object:
    if not isinstance(exp.name, ast.StringLiteral):
        return new_error(
            f"Import Error: Unable to cast ImportExpression.name to ast.StringLiteral"
        )
    module_path = exp.name.value
    path = Path(module_path)
    requestor_path = Path(exp.requestor)

    # if import(/absolute/path)
    if path.is_absolute():
        module_name = module_path
    # else join with requesting file's path
    else:
        module_name = requestor_path.joinpath(module_path).resolve()
    module_location_obj = ast.StringLiteral(TokenType.STRING, module_name)

    # (Finally) evaluate module location node
    evaluated = evaluate(module_location_obj, env)
    if is_error(evaluated):
        return evaluated
    if not isinstance(evaluated, objects.String):
        return new_error(f'Import Error: invalid import path"{evaluated}""')
    attrs = evaluate_module(evaluated.value)
    if is_error(attrs):
        return attrs
    return objects.Module(evaluated.value, attrs)


def evaluate_module(name: str) -> objects.Object:
    path = Path(name)
    directory = path.parents[0].resolve()
    with open(path, "r") as f:
        text = f.read()
    l = lexer.new(text)
    p = Parser(l, directory)

    module = p.parse_program()

    if len(p.errors) != 0:
        return new_error(f"Parser Error: {p.errors}")

    env = objects.new_environment()
    evaluate(module, env)
    return env.exported_hash()


####################
#      HELPERS     #
####################
def is_error(obj: objects.Object):
    if obj is not None:
        return obj.object_type() == ObjectType.ERROR_OBJ
    return False


def new_error(message: str) -> objects.Error:
    return objects.Error(message)


def native_bool_to_boolean_object(input_: bool) -> objects.Boolean:
    if input_:
        return objects.Boolean(True)
    return objects.Boolean(False)


def is_truthy(obj: objects.Object) -> bool:
    if obj is objects.Null():
        return False
    elif obj is objects.Boolean(True):
        return True
    elif obj is objects.Boolean(False):
        return False
    return True


def apply_function(fn: objects.Object, args: List[objects.Object]) -> objects.Object:
    if isinstance(fn, objects.Function):
        extended_env = extend_function_env(fn, args)
        if isinstance(extended_env, objects.Error):
            return extended_env

        evaluated = evaluate(fn.body, extended_env)
        if evaluated is None:
            return evaluated

        return unwrap_return_value(evaluated)
    elif isinstance(fn, objects.Builtin):
        return fn.fn(args)
    return new_error(f"not a function {fn.object_type().value}")


def extend_function_env(
    fn: objects.Function, args: List[objects.Object]
) -> Union[objects.Environment, objects.Error]:
    env = objects.Environment({}, fn.env)

    for i, param in enumerate(fn.parameters):
        try:
            env.set(param.value, args[i])
        except IndexError:
            return objects.Error(f"{param.value} not supplied")
    return env


def unwrap_return_value(obj: objects.Object) -> objects.Object:
    if isinstance(obj, objects.ReturnValue):
        return obj.value
    return obj
