import enum
import typing
from typing import List

from simian import ast
from simian import objects

__all__ = [
    "ObjectType",
    "Object",
    "Boolean",
    "Integer",
    "String",
    "Hash",
    "HashKey",
    "HashPair",
    "Hashable",
    "Null",
    "Error",
    "ReturnValue",
    "Function",
    "Builtin",
    "Array",
    "Module",
]


class ObjectType(enum.Enum):
    INTEGER_OBJ = "INTEGER"
    BOOLEAN_OBJ = "BOOLEAN"
    NULL_OBJ = "NULL"
    RETURN_VALUE_OBJ = "RETURN_VALUE"
    ERROR_OBJ = "ERROR"
    FUNCTION_OBJ = "FUNCTION"
    STRING_OBJ = "STRING"
    BUILTIN_OBJ = "BUILTIN"
    ARRAY_OBJ = "ARRAY"
    HASH_OBJ = "HASH"
    MODULE = "MODULE"


class Object:
    def object_type(self) -> ObjectType:
        pass


class Hashable:
    def hash_key(self):
        raise NotImplementedError()


class Boolean(Object, Hashable):
    _false_instance: typing.Optional["Boolean"] = None
    _true_instance: typing.Optional["Boolean"] = None

    def __new__(cls, value: bool) -> "Boolean":
        if value:
            if cls._true_instance is not None:
                return cls._true_instance
            else:
                new_true_instance: "Boolean" = super().__new__(cls)
                cls._true_instance = new_true_instance
                return new_true_instance
        else:
            if cls._false_instance is not None:
                return cls._false_instance
            else:
                new_false_instance: "Boolean" = super().__new__(cls)
                cls._false_instance = new_false_instance
                return new_false_instance

    def __init__(self, value: bool):
        self.value = value

    def object_type(self):
        return ObjectType.BOOLEAN_OBJ

    def __str__(self):
        return str(self.value).lower()

    def hash_key(self):
        val = 1 if self.value else 0
        return HashKey(self.object_type(), val)


class Integer(Object, Hashable):
    def __init__(self, value: int):
        self.value = value

    def object_type(self):
        return ObjectType.INTEGER_OBJ

    def __str__(self):
        return str(self.value)

    def hash_key(self):
        return HashKey(self.object_type(), int(self.value))


class String(Object, Hashable):
    def __init__(self, value):
        self.value = value

    def object_type(self):
        return ObjectType.STRING_OBJ

    def hash_key(self):
        return HashKey(self.object_type(), hash(self.value))

    def __str__(self):
        return self.value


class HashKey(Object):
    def __init__(self, object_type: ObjectType, value: int):
        self.object_type = object_type
        self.value = value

    def __eq__(self, other: typing.Any) -> bool:
        if isinstance(other, HashKey):
            if other.object_type == self.object_type and other.value == self.value:
                return True
        return False

    def __ne__(self, other: typing.Any) -> bool:
        if isinstance(other, HashKey):
            if other.object_type == self.object_type and other.value == self.value:
                return False
        return True

    def __hash__(self) -> int:
        return hash(f"{self.object_type}-{self.value}")


class HashPair(Object):
    def __init__(self, key: Object, value: Object):
        self.key = key
        self.value = value


class Hash(Object):
    def __init__(self, pairs: typing.Dict[HashKey, HashPair]):
        self.pairs = pairs

    def object_type(self):
        return ObjectType.HASH_OBJ

    def __str__(self):
        ps = []
        for hash_key, hash_pair in self.pairs.items():
            key = hash_pair.key
            key = (
                '"' + str(key) + '"' if isinstance(hash_pair.key, String) else str(key)
            )
            value = str(hash_pair.value)
            ps.append(f"{key}: {value}")
        return f"""{{{", ".join(ps)}}}"""


class Null(Object):
    _instance: typing.Optional["Null"] = None

    def __new__(cls) -> "Null":
        if cls._instance is not None:
            return cls._instance
        else:
            new_null_instance: "Null" = super().__new__(cls)
            cls._instance = new_null_instance
            return new_null_instance

    def object_type(self):
        return ObjectType.NULL_OBJ

    def __str__(self):
        return "null"


class ReturnValue(Object):
    def __init__(self, value):
        self.value = value

    def object_type(self):
        return ObjectType.RETURN_VALUE_OBJ

    def __str__(self):
        return str(self.value)


class Error(Object):
    def __init__(self, message):
        self.message = message

    def object_type(self):
        return ObjectType.ERROR_OBJ

    def __str__(self):
        return f"ERROR: {self.message}"


class Function(Object):
    def __init__(
        self,
        parameters: List[ast.Identifier],
        body: ast.BlockStatement,
        env: "objects.Environment",
    ):
        self.parameters = parameters
        self.body = body
        self.env = env

    def object_type(self):
        return ObjectType.FUNCTION_OBJ

    def __str__(self):
        params = [str(p) for p in self.parameters]
        out = f"fn({', '.join(params)}) {{\n{str(self.body)}\n}}"
        return out


class BuiltinFunction(Object):
    def object_type(self):
        pass


class Builtin(Object):
    def __init__(self, fn: BuiltinFunction):
        self.fn = fn

    def object_type(self):
        return ObjectType.BUILTIN_OBJ

    def __str__(self):
        return "builtin function"


class Array(Object):
    def __init__(self, elements: List[Object]):
        self.elements = elements

    def object_type(self):
        return ObjectType.ARRAY_OBJ

    def __str__(self):
        els = [str(e) for e in self.elements]
        return f"[{', '.join(els)}]"


class Module(Object):
    def __init__(self, name: str, attrs: Object):
        self.name = name
        self.attrs = attrs

    # To Implement? Bool and Compare()?

    def object_type(self):
        return ObjectType.MODULE

    def __str__(self):
        return f"<module {self.name}: {self.attrs}>"
