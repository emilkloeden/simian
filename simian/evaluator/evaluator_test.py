import os
import simian.lexer as lexer
import simian.parser as parser
import simian.objects as objects
import simian.evaluator as evaluator
from simian.objects import String, Integer, Boolean

##############
# STATEMENTS #
##############
def test_let_statements():
    tests = [
        ("let a = 5; a;", 5),
        ("let a = 5 * 5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
    ]

    for tt in tests:
        input_, expected = tt
        assert integer_object_tester(evaluate_input(input_), expected)


def evaluate_return_statements():
    tests = [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2 * 5; 9;", 10),
        ("9; return 2 * 5; 9;", 10),
        (
            """
			if (10 > 1) {
			if (10 > 1) {
			return 10;
			}
			return 1;
			}
			""",
            10,
        ),
    ]
    for tt in tests:
        input_: str
        expected: int
        evaluated: objects.Object

        evaluated = evaluate_input(input_)
        assert integer_object_tester(evaluated, expected)


def test_while_statements():
    tests = [
        (
            """
            let i = 0; 
            let myArr = []; 
            while (i < 5) { 
                push(myArr, i); let i = i+1; 
            }; 
            return myArr;
            """,
            [0, 1, 2, 3, 4],
        )
    ]
    for tt in tests:
        input_, expected = tt
        evaluated = evaluate_input(input_)
        for i, el in enumerate(evaluated.elements):
            assert integer_object_tester(el, expected[i])


###############
# EXPRESSIONS #
# (LITERALS)  #
###############
def test_evaluate_integer_expression():
    tests = [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("-50 + 100 + -50", 0),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("20 + 2 * -10", 0),
        ("50 / 2 * 2 + 10", 60),
        ("2 * (5 + 10)", 30),
        ("3 * 3 * 3 + 10", 37),
        ("3 * (3 * 3) + 10", 37),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
    ]
    for tt in tests:
        input_: str
        expected: int
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        assert integer_object_tester(evaluated, expected)


def test_evaluate_string_literal():
    input_ = '"Hello World!'
    evaluated = evaluate_input(input_)
    assert isinstance(evaluated, objects.String)
    assert evaluated.value == "Hello World!"


def test_evaluate_boolean_expression():
    tests = [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1 != 2", True),
        ("true == true", True),
        ("false == false", True),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
        ('"Hello World" == "Hello World!"', False),
        ('"Hello World" == "Hello World"', True),
        ('"Hello World" != "Hello World!"', True),
        ('"Hello World" != "Hello World"', False),
    ]

    for tt in tests:
        input_: str
        expected: bool
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        assert boolean_object_tester(evaluated, expected)


def test_function_application():
    tests = [
        ("let identity = fn(x) { x; }; identity(5);", 5),
        ("let identity = fn(x) { return x; }; identity(5);", 5),
        ("let double = fn(x) { x * 2; }; double(5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
        ("fn(x) { x; }(5)", 5),
    ]

    for tt in tests:
        input_: str
        expected: int
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        assert integer_object_tester(evaluated, expected)


def test_evaluate_array_literals():
    input_ = "[1, 2 * 2, 3 + 3]"
    evaluated = evaluate_input(input_)
    assert isinstance(evaluated, objects.Array)
    assert len(evaluated.elements) == 3
    assert integer_object_tester(evaluated.elements[0], 1)
    assert integer_object_tester(evaluated.elements[1], 4)
    assert integer_object_tester(evaluated.elements[2], 6)


def test_evaluate_hash_literals():
    input_ = """
    let two = "two";
	{
	"one": 10 - 9,
	two: 1 + 1,
	"thr" + "ee": 6 / 2,
	4: 4,
	true: 5,
	false: 6
	}
    """
    evaluated = evaluate_input(input_)
    assert isinstance(evaluated, objects.Hash)
    expected = {
        String("one").hash_key(): 1,
        String("two").hash_key(): 2,
        String("three").hash_key(): 3,
        Integer(4).hash_key(): 4,
        Boolean(True).hash_key(): 5,
        Boolean(False).hash_key(): 6,
    }
    assert len(evaluated.pairs) == len(expected)

    for expected_key, expected_value in expected.items():
        pair = evaluated.pairs.get(expected_key, None)
        assert pair is not None
        assert integer_object_tester(pair.value, expected_value)


def test_evaluate_array_indexes():
    tests = [
        ("[1, 2, 3][0]", 1,),
        ("[1, 2, 3][1]", 2,),
        ("[1, 2, 3][2]", 3,),
        ("let i = 0; [1][i];", 1,),
        ("[1, 2, 3][1 + 1];", 3,),
        ("let myArray = [1, 2, 3]; myArray[2];", 3,),
        ("let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6,),
        ("let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2,),
        ("[1, 2, 3][3]", None,),
        ("[1, 2, 3][-1]", None,),
    ]
    for tt in tests:
        input_: str
        expected: typing.Optional[int]
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        if expected is None:
            null_object_tester(evaluated)
        else:
            integer_object_tester(evaluated, expected)


def test_evaluate_hash_indexes():
    tests = [
        ('{"foo": 5}["foo"]', 5,),
        ('{"foo": 5}["bar"]', None,),
        ('let key = "foo"; {"foo": 5}[key]', 5,),
        ('{}["foo"]', None,),
        ("{5: 5}[5]", 5,),
        ("{true: 5}[true]", 5,),
        ("{false: 5}[false]", 5,),
    ]
    for tt in tests:
        input_: str
        expected: typing.Optional[int]
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        if expected is None:
            null_object_tester(evaluated)
        else:
            integer_object_tester(evaluated, expected)


def test_evaluate_hash_selectors():
    tests = [
        ('{"foo": 5}.foo', 5),
        ('{"foo": 5}.bar', None),
        ('let key = "foo"; {"foo": 5}.key', None),
        ("{}.foo", None),
        ("{5: 5}.5", 5),
        # ("{true: 5}.true", 5),
        # ("{false: 5}.false", 5),
    ]
    for tt in tests:
        input_: str
        expected: typing.Optional[int]
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        if expected is None:
            null_object_tester(evaluated)
        else:
            integer_object_tester(evaluated, expected)


###############
# EXPRESSIONS #
#  (COMPLEX)  #
###############
def test_bang_operator():
    tests = [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
    ]
    for tt in tests:
        input_: str
        expected: bool
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        assert boolean_object_tester(evaluated, expected)


def test_if_else_expressions():
    tests = [
        ("if (true) { 10 }", 10),
        ("if (false) { 10 }", None),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 > 2) { 10 }", None),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 < 2) { 10 } else { 20 }", 10),
    ]
    for tt in tests:
        input_: str
        expected: typing.Optional[int]
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        if isinstance(expected, int):
            assert integer_object_tester(evaluated, expected)
        else:
            assert null_object_tester(evaluated)


def test_closure_evaluation():
    input_ = """
	let newAdder = fn(x) {
		fn(y) { x + y };
	};
	let addTwo = newAdder(2);
	addTwo(2);
	"""
    assert integer_object_tester(evaluate_input(input_), 4)


def test_string_concatenation():
    input_ = '"Hello" + " " + "World!"'
    evaluated = evaluate_input(input_)
    assert isinstance(evaluated, objects.String)
    assert evaluated.value == "Hello World!"


def test_array_concatenation():
    input_ = "[1,2,3] + [0, 10];"
    expected = [1, 2, 3, 0, 10]
    evaluated = evaluate_input(input_)
    assert isinstance(evaluated, objects.Array)

    for i, el in enumerate(evaluated.elements):
        assert integer_object_tester(el, expected[i])


def test_error_handling():
    tests = [
        ("5 + true;", "type mismatch: INTEGER + BOOLEAN",),
        ("5 + true; 5;", "type mismatch: INTEGER + BOOLEAN",),
        ("-true", "unknown operator: -BOOLEAN",),
        ("true + false;", "unknown operator: BOOLEAN + BOOLEAN",),
        ("5; true + false; 5", "unknown operator: BOOLEAN + BOOLEAN",),
        ("if (10 > 1) { true + false; }", "unknown operator: BOOLEAN + BOOLEAN",),
        (
            """
			if (10 > 1) {
			if (10 > 1) {
			return true + false;
			}
			return 1;
			}
			""",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        ("foobar", "identifier not found: foobar",),
        ('"Hello" - "World"', "unknown operator: STRING - STRING",),
        ('{"name": "Monkey"}[fn(x) { x }];', "unusable as hash key: FUNCTION",),
    ]
    for tt in tests:
        input_: str
        expected: str
        evaluated: objects.Error

        input_, expected = tt
        evaluated = evaluate_input(input_)
        assert isinstance(evaluated, objects.Error)
        assert evaluated.message == expected


def test_builtin_function_returning_ints_or_errors():
    tests = [
        ('len("")', 0),
        ('len("four")', 4),
        ('len("hello world")', 11),
        ("len(1)", "argument to `len` not supported, got INTEGER"),
        ('len("one", "two")', "wrong number of arguments. got=2, want=1"),
        ('first([11, 2, "a"])', 11),
        ("first(1)", "argument to `first` must be ARRAY, got INTEGER"),
        ('first([11, 2, "a"], "two")', "wrong number of arguments. got=2, want=1"),
        ('last([11, 2, "a", 11])', 11),
        ("last(1)", "argument to `last` must be ARRAY, got INTEGER"),
        ('last([11, 2, "a"], "two")', "wrong number of arguments. got=2, want=1"),
        ("exit(1, 2)", "wrong number of arguments. got=2, want=0 or 1"),
        ("exit([11, 2, 13])", "argument to `exit` must be INTEGER, got ARRAY",),
        ('int("1")', 1),
        ("int(1)", 1),
        ("int(-1)", -1),
        ("int(0)", 0),
        ("int(-0)", 0),
        ('int("-0")', 0),
        ("int([1,2])", "Cannot cast ARRAY([1, 2]) to INTEGER"),
        ('int("a")', "Cannot cast STRING(a) to INTEGER"),
        ('int("1", "2")', "wrong number of arguments. got=2, want=1"),
    ]

    for tt in tests:
        input_: str
        expected: typing.Union[int, str, typing.List[int]]
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        if isinstance(expected, int):
            assert integer_object_tester(evaluated, expected)
        elif isinstance(expected, list):
            for i, el in enumerate(evaluated.elements):
                assert integer_object_tester(el, expected[i])
        else:
            assert isinstance(evaluated, objects.Error)
            assert evaluated.message == expected


def test_builtin_function_returning_strings_or_errors():
    tests = [
        ('join(["Hello", "World!"])', True, "wrong number of arguments. got=1, want=2"),
        (
            'join(1, ["Hello", "World!"])',
            True,
            "first argument to `join` must be ARRAY, got INTEGER",
        ),
        (
            'join(["Hello", "World!"], 1)',
            True,
            "second argument to `join` must be STRING, got INTEGER",
        ),
        ('join(["Hello", "World!"], " ")', False, "Hello World!"),
        (
            'type(["Hello", "World!"], "again.")',
            True,
            "wrong number of arguments. got=2, want=1",
        ),
        ('type(["Hello", "World!"])', False, "ARRAY"),
        ('type("Hello")', False, "STRING"),
        ("type(1000)", False, "INTEGER"),
        ('type({"a":1})', False, "HASH"),
        ("type(type)", False, "BUILTIN"),
        ("type(type(type))", False, "STRING"),
        ("let a = fn(x) {x}; type(a)", False, "FUNCTION"),
        ('reverse("123456")', False, "654321"),
        (
            'reverse({"1": "2"})',
            True,
            "argument to `reverse` must be ARRAY or STRING, got HASH",
        ),
        ("str(123)", False, "123"),
        ("str(fn(x) {x})", False, "fn(x) {\nx\n}"),
        ("str(true)", False, "true"),
        ("str(false)", False, "false"),
        ('str("abc")', False, "abc"),
        ("str([1, 2 * 2 , 3])", False, "[1, 4, 3]"),
        ('str({"a": 1})', False, '{"a": 1}'),
    ]

    for tt in tests:
        input_: str
        expected: str
        expected_an_error: bool
        evaluated: objects.Object

        input_, expected_an_error, expected = tt
        evaluated = evaluate_input(input_)
        if expected_an_error:
            assert isinstance(evaluated, objects.Error)
            assert evaluated.message == expected
        else:
            assert isinstance(evaluated, objects.String)
            assert evaluated.value == expected


def test_builtin_function_returning_arrays_or_errors():
    tests = [
        ('split("Hello World!")', "wrong number of arguments. got=1, want=2"),
        (
            'split(1, "Hello World!")',
            "first argument to `split` must be STRING, got INTEGER(1)",
        ),
        (
            'split("Hello World!", 1)',
            "second argument to `split` must be STRING, got INTEGER(1)",
        ),
        ('split("Hello World!", " ")', ["Hello", "World!"]),
        ('keys({"a": 1, "b": 2}, 1)', "wrong number of arguments. got=2, want=1"),
        (
            'keys("Hello")',
            "argument to `keys` must be HASH or MODULE, got STRING(Hello)",
        ),
        ('keys({"a": 1, "b": 2})', ["a", "b"]),
        ('values({"a": 1, "b": 2}, 1)', "wrong number of arguments. got=2, want=1"),
        (
            'values("Hello")',
            "argument to `values` must be HASH or MODULE, got STRING(Hello)",
        ),
        ('values({1: "a", 2: "b"})', ["a", "b"]),
        ('reverse("1", "2")', "wrong number of arguments. got=2, want=1"),
        ('reverse(["1", "2"])', ["2", "1"]),
    ]

    for tt in tests:
        input_: str
        expected: typing.Union[str, typing.List[str]]
        evaluated: objects.Object

        input_, expected = tt
        evaluated = evaluate_input(input_)
        if isinstance(expected, str):
            assert isinstance(evaluated, objects.Error)
            assert evaluated.message == expected
        elif isinstance(expected, list):
            for i, el in enumerate(evaluated.elements):
                assert isinstance(el, objects.String)
                assert el.value == expected[i]
        else:
            return False


####################
#      HELPERS     #
####################
def evaluate_input(input_: str) -> objects.Object:
    l = lexer.new(input_)
    p = parser.Parser(l, os.getcwd())
    program = p.parse_program()
    env = objects.new_environment()
    return evaluator.evaluate(program, env)


def integer_object_tester(obj: objects.Object, expected: int) -> bool:
    assert isinstance(obj, objects.Integer)
    assert obj.value == expected
    return True


def boolean_object_tester(obj: objects.Object, expected: int) -> bool:
    assert isinstance(obj, objects.Boolean)
    assert obj.value == expected
    return True


def null_object_tester(obj: objects.Object) -> bool:
    return isinstance(obj, objects.Null)
