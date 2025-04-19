#!/usr/bin/env python3
import sys
import lexer
import ast


def main(src):
    tokens = lexer.tokenize(src)
    print(ast.print(ast.parse(tokens)))


# stuff
def bootstrap():
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r") as file:
            content = file.read()
            main(content)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    bootstrap()
