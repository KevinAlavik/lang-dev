# Simple language runtime / evaluator
from ast import *
from lexer import *
import math


class RuntimeError(Exception):
    pass


class Interpreter:
    def __init__(self):
        self.vars = {"PI": math.pi}
        self.functions = {
            "print": self.print_function,
        }

    def eval(self, node):
        try:
            if isinstance(node, NumberNode):
                return node.value
            elif isinstance(node, CharNode):
                return node.value
            elif isinstance(node, StringNode):
                return node.value
            elif isinstance(node, IdentifierNode):
                if node.name in self.vars:
                    return self.vars[node.name]
                raise RuntimeError(f"Undefined variable: {node.name}")
            elif isinstance(node, UnaryOpNode):
                operand_value = self.eval(node.expr)
                if node.op == TokenType.PLUS:
                    return operand_value
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
                if node.name in self.functions:
                    # Ensure that each argument is evaluated
                    evaluated_arguments = [self.eval(arg) for arg in node.argument]
                    return self.functions[node.name](evaluated_arguments)
                raise RuntimeError(f"Unknown function: {node.name}")
            elif isinstance(node, ReturnNode):
                return self.eval(node.return_value)
            elif isinstance(node, VariableDeclarationNode):
                value = self.eval(node.value)
                self.vars[node.name] = value
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

        args = [str(arg) for arg in arguments if arg is not None]
        print(" ".join(args))
        return None

    def run(self, statements):
        for statement in statements:
            result = self.eval(statement)
            if isinstance(statement, ReturnNode):
                return result
        return 0
