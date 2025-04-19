#!/usr/bin/env python3
import lexer
import ast
from eval import evaluate


def main():
    while True:
        input_expression = input(">>> ")
        if input_expression.lower() in ["exit", "quit"]:
            print("Exiting repl...")
            break
        try:
            tokens = lexer.tokenize(input_expression)
            print("Tokens:")
            print("[")
            for token, value in tokens:
                print(f"    ({token}, '{value}'),")
            print("]")
            tree = ast.parse(tokens)
            print("\nAST:")
            ast.pretty_print(tree)
            print("\nResult:")
            print(evaluate(tree))

        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
