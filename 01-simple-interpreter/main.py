#!/usr/bin/env python3
import sys
import lexer
import parser
import runtime
import pprint


def eval_input(src, global_scope):
    tokens = lexer.tokenize(src)
    # pprint.pp(tokens)
    ast_tree = parser.parse(tokens)
    # pprint.pp(ast_tree)
    r = runtime.Runtime(global_scope)

    try:
        result = r.run(ast_tree)
        return result
    except runtime.RuntimeError as e:
        print(f"Runtime Error: {e}")
        return None


def main(file_path=None, src=None):
    if file_path and src:
        tokens = lexer.tokenize(src)
        # pprint.pp(tokens)
        ast_tree = parser.parse(tokens)
        # pprint.pp(ast_tree)
        global_scope = runtime.Scope()
        r = runtime.Runtime(global_scope)

        try:
            result = r.run(ast_tree)
            exit(result)
        except runtime.RuntimeError as e:
            pass
    else:
        global_scope = runtime.Scope()
        print("Welcome to the REPL. Type 'exit' to quit.")

        while True:
            try:
                src = input(">>> ")

                if src.lower() == "exit":
                    break

                result = eval_input(src, global_scope)

                if result is not None:
                    print(result)
            except (EOFError, KeyboardInterrupt):
                print("\nExiting REPL.")
                break
            except Exception as e:
                print(f"Error: {e}")


def bootstrap():
    if len(sys.argv) >= 2:
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
