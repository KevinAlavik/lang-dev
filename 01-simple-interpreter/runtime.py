# Simple language runtime / evaluator
from ast import *
from lexer import *
import math


class RuntimeError(Exception):
    pass


class Interpreter:
    def __init__(self, parent=None):
        self.vars = {}
        self.functions = {}
        self.parent = parent

        if parent is None:
            # Only the global scope has built-ins
            self.vars["PI"] = math.pi
            self.functions["print"] = self.print_function

    def get_var(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get_var(name)
        raise RuntimeError(f"Undefined variable: {name}")

    def set_var(self, name, value):
        self.vars[name] = value

    def assign_var(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign_var(name, value)
        else:
            raise RuntimeError(f"Assignment to undefined variable: {name}")

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        raise RuntimeError(f"Unknown function: {name}")

    def eval(self, node):
        try:
            if isinstance(node, NumberNode):
                return node.value

            elif isinstance(node, CharNode):
                return node.value

            elif isinstance(node, StringNode):
                return node.value

            elif isinstance(node, IdentifierNode):
                return self.get_var(node.name)

            elif isinstance(node, UnaryOpNode):
                operand_value = self.eval(node.expr)
                if node.op == TokenType.PLUS:
                    return +operand_value
                elif node.op == TokenType.MINUS:
                    return -operand_value
                else:
                    raise RuntimeError(f"Unsupported unary operation: {node.op}")

            elif isinstance(node, BinaryOpNode):
                left_value = self.eval(node.left)
                right_value = self.eval(node.right)
                if node.op == TokenType.PLUS:
                    return left_value + right_value
                elif node.op == TokenType.MINUS:
                    return left_value - right_value
                elif node.op == TokenType.MULTIPLY:
                    return left_value * right_value
                elif node.op == TokenType.DIVIDE:
                    if right_value == 0:
                        raise RuntimeError("Division by zero")
                    return left_value / right_value
                else:
                    raise RuntimeError(f"Unsupported binary operation: {node.op}")

            elif isinstance(node, FunctionCallNode):
                func = self.get_function(node.name)
                evaluated_args = [self.eval(arg) for arg in node.argument]
                return func(evaluated_args)

            elif isinstance(node, FunctionDeclarationNode):

                def user_defined_function(args):
                    if len(args) != len(node.arguments):
                        raise RuntimeError(
                            f"Expected {len(node.arguments)} arguments, got {len(args)}"
                        )

                    # Create a new scope for the function call
                    func_scope = Interpreter(parent=self)

                    # Bind arguments
                    for arg_node, value in zip(node.arguments, args):
                        func_scope.set_var(arg_node.name, value)

                    # Execute function body
                    result = func_scope.run(node.body)
                    return result

                self.functions[node.name] = user_defined_function
                return None

            elif isinstance(node, ReturnNode):
                return self.eval(node.return_value)

            elif isinstance(node, VariableDeclarationNode):
                value = self.eval(node.value)
                self.set_var(node.name, value)
                return value

            elif isinstance(node, VariableAssignmentNode):
                value = self.eval(node.value)
                self.assign_var(node.name, value)
                return value

            elif node is None:
                return None

            else:
                raise RuntimeError(f"Unsupported AST node: {node}")

        except RuntimeError as e:
            print(f"Runtime Error: {str(e)}")
            return None

    def print_function(self, arguments):
        if not arguments:
            return None
        print("".join(str(arg) for arg in arguments))
        return None

    def run(self, statements):
        for statement in statements:
            result = self.eval(statement)
            if isinstance(statement, ReturnNode):
                return result
        return 0
