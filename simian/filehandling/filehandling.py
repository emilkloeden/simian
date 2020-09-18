import sys
from pathlib import Path

from simian import lexer
from simian import parser
from simian.evaluator import evaluate
from simian.objects import new_environment
from simian.token import TokenType
from simian.repl import print_errors

__all__ = [
    "lex_file",
    "parse_file",
    "evaluate_file",
]


def lex_file(filepath: str) -> None:
    try:
        with open(filepath, "r") as f:
            scanned = f.read()
            l = lexer.new(scanned)
            token = l.next_token()
            while token.token_type != TokenType.EOF:
                print(f"Token: {{{token.token_type}}}, Literal: {{{token.literal}}}")
                token = l.next_token()
    except FileNotFoundError:
        print(f'\tERROR: File: "{filepath}" does not exist.')
    except IsADirectoryError:
        print(f'\tERROR: File: "{filepath}" is a directory.')
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)


def parse_file(filepath: str) -> None:
    try:
        with open(filepath, "r") as f:
            scanned = f.read()
            l = lexer.new(scanned)
            path = Path(filepath)
            p = parser.Parser(l, path.parents[0])
            program = p.parse_program()
            if len(p.errors) != 0:
                print_errors(p.errors)
            else:
                print(str(program))

    except FileNotFoundError:
        print(f'\tERROR: File: "{filepath}" does not exist.')
    except IsADirectoryError:
        print(f'\tERROR: File: "{filepath}" is a directory.')
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)


def evaluate_file(filepath: str) -> None:
    try:
        env = new_environment()
        with open(filepath, "r") as f:
            scanned = f.read()
            l = lexer.new(scanned)
            path = Path(filepath)
            p = parser.Parser(l, path.parents[0])
            program = p.parse_program()
            if len(p.errors) != 0:
                print_errors(p.errors)
            else:
                evaluated = evaluate(program, env)
                if evaluated is not None:
                    print(str(evaluated))

    except FileNotFoundError:
        print(f'\tERROR: File: "{filepath}" does not exist.')
    except IsADirectoryError:
        print(f'\tERROR: File: "{filepath}" is a directory.')
    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
