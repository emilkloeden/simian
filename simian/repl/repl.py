import os
import sys
import traceback
from random import choice

import simian
import simian.lexer as lexer
import simian.parser as parser
from simian import objects
from simian.token import TokenType
from simian.evaluator import evaluate

__all__ = ["Rlpl", "Rppl", "Repl", "print_errors"]

prompts = [
    "(/*-*)/",
    "(((o(*°▽°*)o)))",
    "(≧◡≦)",
    "(◕‿◕)",
    "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
]
salutations = [
    "K, thx, bye!",
    "See you later!" "Farvel!",
    "Tot ziens!",
    "Näkemiin!",
    "Au Revoir!",
    "Auf Wiedersehen!",
    "Yasou!",
    "Aloha!",
    "Viszlát!",
    "Arrivederci!",
    "Uz redzēšanos!",
    "Ha det bra!",
    "Żegnaj!",
    "Adeus!",
    "La revedere!",
    "Adios!",
    "Adjö!",
    "Görüşürüz!",
    "Do pobachennia!",
    "Khuda hafiz!",
    "Tạm biệt!",
    "Hwyl fawr!",
    "Hamba kahle!",
]
SALUTATION = choice(salutations)
PROMPT = f"{choice(prompts)} >"
MONKEY_IMAGE = """            __,__
   .--.  .-"     "-.  .--.
  / .. \/  .-. .-.  \/ .. \\
 | |  '|  /   Y   \  |'  | |
 | \   \  \ 0 | 0 /  /   / |
  \ '- ,\.-\"\"\"\"\"\"-./, -' /
   ''-' /_   ^ ^   _\\ '-''
       |  \._   _./  |
       \   \ '~' /   /
        '._ '-=-' _.'
           '-----'
"""


class Rlpl:
    def start(self):
        print_header(mode="LEXING")
        while True:
            try:
                scanned = input(PROMPT)
                if scanned == "exit()":
                    sys.exit()
                l = lexer.new(scanned)

                token = l.next_token()
                while token.token_type != TokenType.EOF:
                    print(
                        f"Token: {{{token.token_type}}}, Literal: {{{token.literal}}}"
                    )
                    token = l.next_token()

            except KeyboardInterrupt:
                print(f"\nNow exiting... {SALUTATION}")
                sys.exit(0)


class Rppl:
    def start(self):
        print_header(mode="LEXING AND PARSING")
        while True:
            try:
                scanned = input(PROMPT)
                if scanned == "exit()":
                    sys.exit()
                l = lexer.new(scanned)
                p = parser.Parser(l, os.getcwd())
                program = p.parse_program()
                if len(p.errors) != 0:
                    print_errors(p.errors)
                    continue

                print(str(program))
            except KeyboardInterrupt:
                print(f"\nNow exiting... {SALUTATION}")
                sys.exit(0)


class Repl:
    def start(self):
        print_header(mode="EVALUATION")
        env = objects.new_environment()

        while True:
            try:
                scanned = input(PROMPT)
                l = lexer.new(scanned)
                p = parser.Parser(l, os.getcwd())
                program = p.parse_program()
                if len(p.errors) != 0:
                    print_errors(p.errors)
                    continue

                evaluated = evaluate(program, env)
                if evaluated is not None:
                    print(str(evaluated))
            except KeyboardInterrupt:
                print(f"\nNow exiting... {SALUTATION}")
                sys.exit(0)


def print_errors(errors):
    for error in errors:
        print(f"\t{error}")


def print_header(mode="EVALUATION"):
    print(MONKEY_IMAGE)
    print(f"Welcome to Simian a monkey-lang interpreter written for Python >= 3.6")
    print(f"Version: {simian.__version__}")
    print(f"Author: {simian.__author__}")
    print(f"License: {simian.__license__}")
    print(f"Repository and Credits: {simian.__url__}")
    print(f"Running in {mode} mode.\n")
