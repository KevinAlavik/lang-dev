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
            self.functions["exit"] = BuiltInFunction("exit", Runtime.BuiltIn.exit)

    def get_var(self, name):
        # Direct dictionary lookup avoids recursion
        scope = self
        while scope:
            if name in scope.vars:
                return scope.vars[name]
            elif name in scope.functions:
                return scope.functions[name]
            scope = scope.parent
        raise RuntimeError(f"Undefined variable or function:  {name}", scope=self)

    def set_var(self, name, value):
        self.vars[name] = value

    def assign_var(self, name, value):
        scope = self
        while scope:
            if name in scope.vars:
                scope.vars[name] = value
                return
            scope = scope.parent
        raise RuntimeError(f"Assignment to undefined variable: {name}", scope=self)


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

        @staticmethod
        def exit(args):
            if len(args) != 1:
                raise RuntimeError("exit() takes exactly one argument")
            return exit(args[0])

    def __init__(self, global_scope):
        self.global_scope = global_scope

    def eval(self, node):
        # Use a dictionary to store evaluated nodes for faster lookup
        node_type_handlers = {
            NumberNode: lambda n: int(n.value),
            FloatNumberNode: lambda n: float(n.value),
            BoolNode: lambda n: n.value,
            CharNode: lambda n: chr(n.value),
            StringNode: lambda n: str(n.value),
            IdentifierNode: self.eval_identifier,
            ArrayNode: self.eval_array,
            ArrayAccessNode: self.eval_array_access,
            ArrayAssignmentNode: self.eval_array_assignment,
            UnaryOpNode: self.eval_unary_op,
            BinaryOpNode: self.eval_binary_op,
            FunctionCallNode: self.eval_function_call,
            FunctionDeclarationNode: self.eval_function_declaration,
            ReturnNode: self.eval_return,
            VariableDeclarationNode: self.eval_var_declaration,
            VariableAssignmentNode: self.eval_var_assignment,
            IfNode: self.eval_if,
            WhileNode: self.eval_while,
        }

        handler = node_type_handlers.get(type(node))
        if handler:
            return handler(node)
        raise RuntimeError(
            f"Unsupported node type: {type(node)}", node=node, scope=self.global_scope
        )

    def eval_identifier(self, node):
        return self.global_scope.get_var(node.name)

    def eval_array(self, node):
        return [self.eval(element) for element in node.elements]

    def eval_array_access(self, node):
        array_value = self.eval(node.array)
        index_value = self.eval(node.index)

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

    def eval_array_assignment(self, node):
        array_value = self.eval(node.array)
        index_value = self.eval(node.index)
        assigned_value = self.eval(node.value)

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

        array_value[index_value] = assigned_value
        return assigned_value

    def eval_unary_op(self, node):
        operand_value = self.eval(node.expr)
        if node.op == TokenType.PLUS:
            return +operand_value
        elif node.op == TokenType.MINUS:
            return -operand_value
        raise RuntimeError(
            f"Unsupported unary operation: {node.op}",
            node=node,
            scope=self.global_scope,
        )

    def eval_binary_op(self, node):
        left_value = self.eval(node.left)
        right_value = self.eval(node.right)

        operations = {
            TokenType.LOGICAL_AND: lambda: left_value and right_value,
            TokenType.LOGICAL_OR: lambda: left_value or right_value,
            TokenType.EQUAL_EQUAL: lambda: left_value == right_value,
            TokenType.BANG_EQUAL: lambda: left_value != right_value,
            TokenType.GREATER: lambda: left_value > right_value,
            TokenType.LESS: lambda: left_value < right_value,
            TokenType.GREATER_EQUAL: lambda: left_value >= right_value,
            TokenType.LESS_EQUAL: lambda: left_value <= right_value,
            TokenType.PLUS: lambda: left_value + right_value,
            TokenType.MINUS: lambda: left_value - right_value,
            TokenType.MULTIPLY: lambda: left_value * right_value,
            TokenType.DIVIDE: lambda: left_value / right_value,
            TokenType.MODULO: lambda: left_value % right_value,
            TokenType.BIT_OR: lambda: left_value | right_value,
            TokenType.BIT_XOR: lambda: left_value ^ right_value,
            TokenType.BIT_AND: lambda: left_value & right_value,
            TokenType.BIT_LSH: lambda: left_value << right_value,
            TokenType.BIT_RSH: lambda: left_value >> right_value,
        }

        if node.op == TokenType.PLUS_EQUAL:
            left_value += right_value
            self.global_scope.assign_var(node.left.name, left_value)
            return left_value
        elif node.op == TokenType.MINUS_EQUAL:
            left_value -= right_value
            self.global_scope.assign_var(node.left.name, left_value)
            return left_value
        op_func = operations.get(node.op)

        if op_func:
            return op_func()

        raise RuntimeError(
            f"Unsupported binary operation: {node.op}",
            node=node,
            scope=self.global_scope,
        )

    def eval_function_call(self, node):
        function = self.global_scope.get_var(node.name)
        if not callable(function):
            raise RuntimeError(
                f"Attempted to call non-function: {node.name}",
                node=node,
                scope=self.global_scope,
            )
        args = [self.eval(arg) for arg in node.arguments]
        return function(args)

    def eval_function_declaration(self, node):
        self.global_scope.set_var(
            node.name, UserFunction(node.name, node, self.global_scope)
        )
        return None

    def eval_var_declaration(self, node):
        value = self.eval(node.value)
        self.global_scope.set_var(node.name, value)
        return value

    def eval_var_assignment(self, node):
        value = self.eval(node.value)
        self.global_scope.assign_var(node.name, value)
        return value

    def eval_return(self, node):
        return self.eval(node.value) if node.value else None

    def eval_if(self, node):
        condition = self.eval(node.condition)
        if condition:
            for stmt in node.body:
                self.eval(stmt)

    def eval_while(self, node):
        while self.eval(node.condition):
            for stmt in node.body:
                self.eval(stmt)

    def run(self, statements):
        for statement in statements:
            result = self.eval(statement)
            return result
