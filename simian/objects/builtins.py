import sys
from typing import List
from simian import objects
from simian.objects import ObjectType
from simian.token import TokenType

__all__ = ["BUILTINS"]


def len_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    if isinstance(args[0], objects.Array):
        return objects.Integer(len(args[0].elements))
    elif isinstance(args[0], objects.String):
        return objects.Integer(len(args[0].value))
    return objects.Error(
        f"argument to `len` not supported, got {args[0].object_type().value}"
    )


def first_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    if args[0].object_type() != ObjectType.ARRAY_OBJ:
        return objects.Error(
            f"argument to `first` must be ARRAY, got {args[0].object_type().value}"
        )
    arr = args[0]
    if len(arr.elements):
        return arr.elements[0]
    return objects.Null()


def last_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    if args[0].object_type() != ObjectType.ARRAY_OBJ:
        return objects.Error(
            f"argument to `last` must be ARRAY, got {args[0].object_type().value}"
        )
    arr = args[0]
    if len(arr.elements):
        return arr.elements[-1]
    return objects.Null()


def rest_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    if args[0].object_type() != ObjectType.ARRAY_OBJ:
        return objects.Error(
            f"argument to `rest` must be ARRAY, got {args[0].object_type().value}"
        )
    arr = args[0]
    if len(arr.elements):
        return objects.Array(arr.elements[1:])
    return objects.Array([])


def push_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 2:
        return wrong_number_of_args(actual=len(args), expected=2)
    if args[0].object_type() != ObjectType.ARRAY_OBJ:
        return objects.Error(
            f"first argument to `push` must be ARRAY, got {args[0].object_type().value}"
        )
    arr = args[0]
    new_elements = list(arr.elements)
    new_elements.append(args[1])
    return objects.Array(new_elements)


def puts_fn(args: List[objects.Object]) -> objects.Object:
    for arg in args:
        print(str(arg))
    return objects.Null()


def exit_fn(args: List[objects.Object]) -> None:
    if len(args) not in [0, 1]:
        return objects.Error(f"wrong number of arguments. got={len(args)}, want=0 or 1")
    if len(args) == 1:
        if args[0].object_type() != ObjectType.INTEGER_OBJ:
            return objects.Error(
                f"argument to `exit` must be INTEGER, got {args[0].object_type().value}"
            )
        else:
            sys.exit(args[0].value)
    else:
        sys.exit(0)


def join_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 2:
        return wrong_number_of_args(actual=len(args), expected=2)
    if args[0].object_type() != ObjectType.ARRAY_OBJ:
        return objects.Error(
            f"first argument to `join` must be ARRAY, got {args[0].object_type().value}"
        )

    if args[1].object_type() != ObjectType.STRING_OBJ:
        return objects.Error(
            f"second argument to `join` must be STRING, got {args[1].object_type().value}"
        )

    elements = args[0].elements
    if len(elements) == 0:
        return objects.String("")
    if len(elements) == 1:
        return objects.String(str(elements[0]))

    max_ = len(elements) - 1

    out = f""

    for i, el in enumerate(elements):
        out += str(el)
        if i < max_:
            out += str(args[1])

    return objects.String(out)


def split_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 2:
        return wrong_number_of_args(actual=len(args), expected=2)

    string = args[0]
    delimiter = args[1]
    if not isinstance(string, objects.String):
        return objects.Error(
            f"first argument to `split` must be STRING, got {string.object_type().value}({args[0]})"
        )
    if not isinstance(delimiter, objects.String):
        return objects.Error(
            f"second argument to `split` must be STRING, got {delimiter.object_type().value}({args[1]})"
        )

    elements = string.value.split(delimiter.value)
    strElements = [objects.String(el) for el in elements]

    return objects.Array(strElements)


def keys_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    src = args[0]
    if src.object_type() == ObjectType.HASH_OBJ:
        hash_ = src
    elif src.object_type() == ObjectType.MODULE:
        if not isinstance(src, objects.Module):
            return objects.Error(
                f"argument to `keys` must be HASH or MODULE, got {src.object_type().value}({src})"
            )
        hash_ = module.attrs
    else:
        return objects.Error(
            f"argument to `keys` must be HASH or MODULE, got {src.object_type().value}({src})"
        )

    keys = [hash_pair.key for hash_key, hash_pair in hash_.pairs.items()]

    return objects.Array(keys)


def values_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    src = args[0]
    if src.object_type() == ObjectType.HASH_OBJ:
        hash_ = src
    elif src.object_type() == ObjectType.MODULE:
        if not isinstance(src, objects.Module):
            return objects.Error(
                f"argument to `values` must be HASH or MODULE, got {src.object_type().value}({src})"
            )
        hash_ = module.attrs
    else:
        return objects.Error(
            f"argument to `values` must be HASH or MODULE, got {src.object_type().value}({src})"
        )

    values = [hash_pair.value for hash_key, hash_pair in hash_.pairs.items()]

    return objects.Array(values)


def type_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    return objects.String(args[0].object_type().value)


def str_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    return object.String(str(args[0]))


def int_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    src = args[0]
    if src.object_type() == ObjectType.INTEGER_OBJ:
        return src
    elif src.object_type() == ObjectType.STRING_OBJ:
        print(src)
        try:
            i = int(src.value)
            ix = objects.Integer(TokenType.INT)
            ix.value = i
            return ix
        except ValueError:
            return objects.Error(
                f"Cannot cast {src.object_type().value}({src}) to INTEGER"
            )
    return objects.Error(f"Cannot cast {src.object_type().value}({src}) to INTEGER")


def reverse_fn(args: List[objects.Object]) -> objects.Object:
    if len(args) != 1:
        return wrong_number_of_args(actual=len(args), expected=1)
    src = args[0]
    if src.object_type() == ObjectType.ARRAY_OBJ:
        reversed_elements = src.elements[::-1]
        return objects.Array(reversed_elements)
    elif src.object_type() == ObjectType.STRING_OBJ:
        return object.String(src.value[::-1])
    return new_error("argument to `reverse` must be ARRAY or STRING.")


####################
#      HELPERS     #
####################


def wrong_number_of_args(actual, expected=1):
    return objects.Error(f"wrong number of arguments. got={actual}, want={expected}")


BUILTINS = {
    "len": objects.Builtin(len_fn),
    "first": objects.Builtin(first_fn),
    "last": objects.Builtin(last_fn),
    "rest": objects.Builtin(rest_fn),
    "push": objects.Builtin(push_fn),
    "puts": objects.Builtin(puts_fn),
    "exit": objects.Builtin(exit_fn),
    "join": objects.Builtin(join_fn),
    "split": objects.Builtin(split_fn),
    "keys": objects.Builtin(keys_fn),
    "values": objects.Builtin(values_fn),
    "type": objects.Builtin(type_fn),
    "str": objects.Builtin(str_fn),
    "reverse": objects.Builtin(reverse_fn),
    "int": objects.Builtin(int_fn),
}
