#!/usr/bin/env python3
import lexer
import ast

# Simple repl for my calculator
def main():
    while True:
        input_expression = input(">>> ")
        if input_expression.lower() in ['exit', 'quit']:
            print("Exiting repl...")
            break
        try:
            tokens = lexer.tokenize(input_expression)
            tree = ast.parse(tokens)
            print(ast.compact_print(tree))
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
