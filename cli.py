import argparse

from simian.filehandling import lex_file, parse_file, evaluate_file
from simian.repl import Rppl, Rlpl, Repl, print_errors
from simian.evaluator import evaluate


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("FILE", nargs="?")
    group = argparser.add_mutually_exclusive_group()
    group.add_argument(
        "--lex",
        "-l",
        action="store_true",
        help="Lex input only. Do not parse, evaluate or collect $200.",
    )
    group.add_argument(
        "--parse",
        "-p",
        action="store_true",
        help="Lex and parse input. Do not evaluate.",
    )
    args = argparser.parse_args()

    if args.FILE:
        if args.lex:
            lex_file(args.FILE)
        elif args.parse:
            parse_file(args.FILE)
        else:
            evaluate_file(args.FILE)

    else:
        if args.lex:
            rlpl = Rlpl()
            rlpl.start()
        elif args.parse:
            rppl = Rppl()
            rppl.start()
        else:
            repl = Repl()
            repl.start()


if __name__ == "__main__":
    main()
