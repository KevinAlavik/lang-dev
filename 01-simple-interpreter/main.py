#!/usr/bin/env python3
import sys
import lexer
import parser
import runtime
import pprint


def main(file_path, src):
    tokens = lexer.tokenize(src)
    # pprint.pp(tokens)
    ast_tree = parser.parse(tokens)
    pprint.pp(ast_tree)
    global_scope = runtime.Scope()
    r = runtime.Runtime(global_scope)

    try:
        result = r.run(ast_tree)
        exit(result)
    except runtime.RuntimeError as e:
        pass


def bootstrap():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as file:
            content = file.read()
            main(file_path, content)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    bootstrap()
