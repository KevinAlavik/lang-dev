import math
import sys
import traceback
from ast import *
from lexer import *


class RuntimeError(Exception):
    def __init__(self, message, node=None, scope=None, func=None):
        self.message = message
        self.node = node
        self.scope = scope
        self.func = func
        super().__init__(message)

    def __str__(self):
        location = f" in scope at {hex(id(self.scope))}"
        if self.func:
            return f"\033[91mRuntimeError{location} in function '{self.func.name}'\033[0m: {self.message}"
        return f"\033[91mRuntimeError{location}: {self.message}\033[0m"


class BuiltInFunction:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, args):
        return self.func(args)

    def __repr__(self):
        return f"<Built-in Function '{self.name}' (callable={self.func.__name__}, scope=global) at {hex(id(self))}>"


class UserFunction:
    def __init__(self, name, node, defining_scope):
        self.name = name
        self.node = node
        self.scope = defining_scope

    def __call__(self, args):
        if len(args) != len(self.node.arguments):
            raise RuntimeError(
                f"Expected {len(self.node.arguments)} arguments, got {len(args)}",
                node=self.node,
                scope=self.scope,
                func=self,
            )

        func_scope = Scope(parent=self.scope)

        for arg_node, value in zip(self.node.arguments, args):
            func_scope.set_var(arg_node.name, value)

        func_scope.set_var("self", self)

        runtime = Runtime(func_scope)
        result = None
        for statement in self.node.body:
            result = runtime.eval(statement)
            if isinstance(statement, ReturnNode):
                return result

        return result

    def __repr__(self):
        arg_list = ", ".join(arg.name for arg in self.node.arguments)
        return f"<UserFunction '{self.name}'({arg_list}) [scope={hex(id(self.scope))}] at {hex(id(self))}]>"


class Scope:
    def __init__(self, parent=None):
        self.vars = {}
        self.functions = {}
        self.parent = parent

        if parent is None:
            self.vars["PI"] = math.pi
            self.functions["print"] = BuiltInFunction("print", Runtime.BuiltIn.print)
            self.functions["str"] = BuiltInFunction("str", Runtime.BuiltIn.str)
            self.functions["int"] = BuiltInFunction("int", Runtime.BuiltIn.int)

    def get_var(self, name):
        if name in self.vars:
            return self.vars[name]
        elif name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_var(name)
        raise RuntimeError(f"Undefined variable or function:  {name}", scope=self)

    def set_var(self, name, value):
        self.vars[name] = value

    def assign_var(self, name, value):
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign_var(name, value)
        else:
            raise RuntimeError(f"Assignment to undefined variable: {name}", scope=self)

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        raise RuntimeError(f"Unknown function: {name}", scope=self)


class Runtime:
    class BuiltIn:
        @staticmethod
        def print(args):
            print("".join(str(arg) for arg in args))
            return None

        @staticmethod
        def str(args):
            return "".join(str(arg) for arg in args)

        @staticmethod
        def int(args):
            return "".join(int(arg) for arg in args)

    def __init__(self, global_scope):
        self.global_scope = global_scope

    def eval(self, node):
        try:
            if isinstance(node, NumberNode):
                return node.value

            elif isinstance(node, CharNode):
                return node.value

            elif isinstance(node, StringNode):
                return node.value

            elif isinstance(node, IdentifierNode):
                return self.global_scope.get_var(node.name)

            elif isinstance(node, UnaryOpNode):
                operand_value = self.eval(node.expr)
                if node.op == TokenType.PLUS:
                    return +operand_value
                elif node.op == TokenType.MINUS:
                    return -operand_value
                else:
                    raise RuntimeError(
                        f"Unsupported unary operation: {node.op}",
                        node=node,
                        scope=self.global_scope,
                    )

            elif isinstance(node, BinaryOpNode):
                left_value = self.eval(node.left)
                right_value = self.eval(node.right)

                if node.op == TokenType.PLUS:
                    if isinstance(left_value, str) and isinstance(right_value, str):
                        return left_value + right_value
                    else:
                        raise RuntimeError(
                            f"Unsupported operand types for '+': {type(left_value)} and {type(right_value)}",
                            node=node,
                            scope=self.global_scope,
                        )
                elif node.op == TokenType.MINUS:
                    return left_value - right_value
                elif node.op == TokenType.MULTIPLY:
                    return left_value * right_value
                elif node.op == TokenType.DIVIDE:
                    if right_value == 0:
                        raise RuntimeError(
                            "Division by zero", node=node, scope=self.global_scope
                        )
                    return left_value / right_value
                else:
                    raise RuntimeError(
                        f"Unsupported binary operation: {node.op}",
                        node=node,
                        scope=self.global_scope,
                    )

            elif isinstance(node, FunctionCallNode):
                func = self.global_scope.get_var(node.name)
                if not callable(func):
                    raise RuntimeError(
                        f"'{node.name}' is not a function",
                        node=node,
                        scope=self.global_scope,
                    )
                evaluated_args = [self.eval(arg) for arg in node.argument]
                return func(evaluated_args)

            elif isinstance(node, FunctionDeclarationNode):
                func_obj = UserFunction(
                    node.name, node, defining_scope=self.global_scope
                )
                self.global_scope.functions[node.name] = func_obj
                return None

            elif isinstance(node, ReturnNode):
                return self.eval(node.return_value)

            elif isinstance(node, VariableDeclarationNode):
                value = self.eval(node.value)
                self.global_scope.set_var(node.name, value)
                return value

            elif isinstance(node, VariableAssignmentNode):
                value = self.eval(node.value)
                self.global_scope.assign_var(node.name, value)
                return value

            elif node is None:
                return None

            else:
                raise RuntimeError(
                    f"Unsupported AST node: {node}", node=node, scope=self.global_scope
                )

        except RuntimeError as e:
            print(f"\033[91m{str(e)}\033[0m")
            exit(1)

        except Exception as e:
            print("\033[91mUnexpected Error:\033[0m", e)
            traceback.print_exc()
            exit(1)

    def run(self, statements):
        for statement in statements:
            result = self.eval(statement)
            if isinstance(statement, ReturnNode):
                return result
        return 0
