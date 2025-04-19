import math
from parser import *
from lexer import *
import pprint


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
                return result if result is not None else 0

        return result if result is not None else 0

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
            self.functions["input"] = BuiltInFunction("input", Runtime.BuiltIn.input)
            self.functions["str"] = BuiltInFunction("str", Runtime.BuiltIn.str)
            self.functions["int"] = BuiltInFunction("int", Runtime.BuiltIn.int)
            self.functions["float"] = BuiltInFunction("float", Runtime.BuiltIn.float)
            self.functions["len"] = BuiltInFunction("len", Runtime.BuiltIn.len)

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
        def input(args):
            return input("".join(str(arg) for arg in args))

        @staticmethod
        def str(args):
            return "".join(str(arg) for arg in args)

        @staticmethod
        def int(args):
            if len(args) != 1:
                raise RuntimeError("int() takes exactly one argument")
            try:
                return int(args[0])
            except ValueError:
                raise RuntimeError(f"Cannot convert {args[0]} to int")

        @staticmethod
        def float(args):
            if len(args) != 1:
                raise RuntimeError("float() takes exactly one argument")
            try:
                return float(args[0])
            except ValueError:
                raise RuntimeError(f"Cannot convert {args[0]} to float")

        @staticmethod
        def len(args):
            if len(args) != 1:
                raise RuntimeError("len() takes exactly one argument")
            return len(args[0])

    def __init__(self, global_scope):
        self.global_scope = global_scope

    def eval(self, node):
        try:
            if isinstance(node, NumberNode):
                return int(node.value)

            if isinstance(node, FloatNumberNode):
                return float(node.value)

            if isinstance(node, BoolNode):
                return node.value

            elif isinstance(node, CharNode):
                return chr(node.value)

            elif isinstance(node, StringNode):
                return str(node.value)

            elif isinstance(node, IdentifierNode):
                return self.global_scope.get_var(node.name)

            elif isinstance(node, ArrayNode):
                return [self.eval(element) for element in node.elements]

            elif isinstance(node, ArrayAccessNode):
                array_value = self.eval(node.array)  # Evaluate the array
                index_value = self.eval(node.index)  # Evaluate the index

                if not isinstance(array_value, list):
                    raise RuntimeError(
                        f"Expected array, got {type(array_value)}",
                        node=node,
                        scope=self.global_scope,
                    )

                if not isinstance(index_value, int):
                    raise RuntimeError(
                        f"Array index must be an integer, got {type(index_value)}",
                        node=node,
                        scope=self.global_scope,
                    )

                if index_value < 0 or index_value >= len(array_value):
                    raise RuntimeError(
                        f"Array index out of bounds: {index_value}",
                        node=node,
                        scope=self.global_scope,
                    )

                return array_value[index_value]

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

                if node.op == TokenType.LOGICAL_AND:
                    if not isinstance(left_value, bool) or not isinstance(
                        right_value, bool
                    ):
                        raise RuntimeError(
                            f"Unsupported operand types for '&&': {type(left_value)} and {type(right_value)}",
                            node=node,
                            scope=self.global_scope,
                        )
                    return left_value and right_value

                elif node.op == TokenType.LOGICAL_OR:
                    if not isinstance(left_value, bool) or not isinstance(
                        right_value, bool
                    ):
                        raise RuntimeError(
                            f"Unsupported operand types for '||': {type(left_value)} and {type(right_value)}",
                            node=node,
                            scope=self.global_scope,
                        )
                    return left_value or right_value

                elif node.op == TokenType.EQUAL_EQUAL:
                    return left_value == right_value

                elif node.op == TokenType.BANG_EQUAL:
                    return left_value != right_value

                elif node.op == TokenType.GREATER:
                    return left_value > right_value

                elif node.op == TokenType.LESS:
                    return left_value < right_value

                elif node.op == TokenType.GREATER_EQUAL:
                    return left_value >= right_value

                elif node.op == TokenType.LESS_EQUAL:
                    return left_value <= right_value

                # Handle addition (+)
                elif node.op == TokenType.PLUS:
                    return left_value + right_value

                # Handle subtraction (-)
                elif node.op == TokenType.MINUS:
                    return left_value - right_value

                # Handle multiplication (*)
                elif node.op == TokenType.MULTIPLY:
                    return left_value * right_value

                # Handle division (/)
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

            elif isinstance(node, IfNode):
                condition_value = self.eval(node.condition)
                if condition_value:
                    for statement in node.body:
                        result = self.eval(statement)
                        if isinstance(statement, ReturnNode):
                            if self.global_scope.parent is None:
                                exit(result)
                            return result
                elif node.else_body:
                    for statement in node.else_body:
                        result = self.eval(statement)
                        if isinstance(statement, ReturnNode):
                            if self.global_scope.parent is None:
                                exit(result)
                            return result
                return None

            elif isinstance(node, WhileNode):
                while self.eval(node.condition):
                    for statement in node.body:
                        result = self.eval(statement)
                        if isinstance(statement, ReturnNode):
                            if self.global_scope.parent is None:
                                exit(result)
                            return result
                return None

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

            elif isinstance(node, IfNode):
                condition_value = self.eval(node.condition)
                if condition_value:
                    # Execute the 'if' body if the condition is True
                    for statement in node.body:
                        result = self.eval(statement)
                        if isinstance(statement, ReturnNode):
                            # If a return statement is encountered, exit early
                            if self.global_scope.parent is None:
                                exit(result)
                            return result
                elif node.else_body:  # If there's an 'else' block, execute it
                    for statement in node.else_body:
                        result = self.eval(statement)
                        if isinstance(statement, ReturnNode):
                            # If a return statement is encountered, exit early
                            if self.global_scope.parent is None:
                                exit(result)
                            return result
                return None

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
            exit(1)

    def run(self, statements):
        for statement in statements:
            result = self.eval(statement)
            if isinstance(statement, ReturnNode):
                return result
        return 0
