#!/usr/bin/env python3
import sys
import lexer
import parser
import runtime
import pprint


def eval_input(src, global_scope):
    tokens = lexer.tokenize(src)
    ast_tree = parser.parse(tokens)
    r = runtime.Runtime(global_scope)

    try:
        result = r.execute(ast_tree)
        return result
    except runtime.RuntimeError as e:
        print(f"{e}")
        return None


def handle_multiline_input():
    multiline_buffer = ""
    while True:
        src = input("... ")
        multiline_buffer += src + "\n"
        if src.strip().endswith("}"):
            return multiline_buffer
        if not src:
            return multiline_buffer


def main(file_path=None, src=None):
    if file_path and src:
        tokens = lexer.tokenize(src)
        ast_tree = parser.parse(tokens)
        global_scope = runtime.Scope()
        r = runtime.Runtime(global_scope)
        try:
            result = r.execute(ast_tree)
            exit(result)
        except runtime.RuntimeError as e:
            print(f"{e}")
            return None
    else:
        global_scope = runtime.Scope()
        print("Welcome to the REPL. Type 'exit' to quit.")

        while True:
            try:
                src = input(">>> ")

                if src.lower() == "exit":
                    break

                if "{" in src:
                    src += handle_multiline_input()

                result = eval_input(src, global_scope)

                if result is not None:
                    print(result)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting REPL.")
                break
            except Exception as e:
                print(f"Error: {e}")


def bootstrap():
    if len(sys.argv) == 2:
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
    else:
        main()


if __name__ == "__main__":
    bootstrap()
