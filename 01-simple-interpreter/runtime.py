import math
from parser import *
from lexer import *
from typing import Dict, List, Any, Callable, Optional, Union
from functools import lru_cache
import random
import sys


class RuntimeError(Exception):
    def __init__(self, message: str, node=None, scope=None, func=None):
        self.message = message
        self.node = node
        self.scope = scope
        self.func = func
        super().__init__(message)

    def __str__(self) -> str:
        location = f" in scope at {hex(id(self.scope))}"
        if self.func:
            return f"\033[91mRuntimeError{location} in function '{self.func.name}': {self.message}\033[0m"
        return f"\033[91mRuntimeError{location}: {self.message}\033[0m"


class Function:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, args: List[Any]) -> Any:
        raise NotImplementedError("Function subclasses must implement __call__")

    def validate_args(
        self, args: List[Any], expected_count: Optional[int] = None
    ) -> None:
        if expected_count is not None and len(args) != expected_count:
            raise RuntimeError(f"Expected {expected_count} arguments, got {len(args)}")

    def __repr__(self) -> str:
        return f"<Function '{self.name}' at {hex(id(self))}>"


class BuiltInFunction(Function):
    def __init__(
        self, name: str, implementation: Callable, expected_args: Optional[int] = None
    ):
        super().__init__(name)
        self.implementation = implementation
        self.expected_args = expected_args

    def __call__(self, args: List[Any]) -> Any:
        try:
            if self.expected_args is not None:
                self.validate_args(args, self.expected_args)
            return self.implementation(args)
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"Error in built-in function '{self.name}': {str(e)}")

    def __repr__(self) -> str:
        return f"<Built-in Function '{self.name}' at {hex(id(self))}>"


class UserFunction(Function):
    __slots__ = ("name", "node", "scope")

    def __init__(self, name: str, node, defining_scope):
        super().__init__(name)
        self.node = node
        self.scope = defining_scope

    def __call__(self, args: List[Any]) -> Any:
        try:
            self.validate_args(args, len(self.node.arguments))
            func_scope = Scope(parent=self.scope)

            for arg_node, value in zip(self.node.arguments, args):
                func_scope.define(arg_node.name, value)

            func_scope.define("self", self)

            runtime = Runtime(func_scope)
            result = None

            for statement in self.node.body:
                result = runtime.evaluate(statement)
                if isinstance(statement, ReturnNode):
                    return result if result is not None else 0

            return result if result is not None else 0
        except RuntimeError as e:
            if e.func is None:
                e.func = self
            raise
        except Exception as e:
            raise RuntimeError(
                f"Error in function '{self.name}': {str(e)}",
                func=self,
                scope=self.scope,
            )

    def __repr__(self) -> str:
        arg_list = ", ".join(arg.name for arg in self.node.arguments)
        return f"<UserFunction '{self.name}'({arg_list}) at {hex(id(self))}>"


class Scope:
    __slots__ = ("symbols", "parent", "_cached_lookups")

    def __init__(self, parent=None):
        self.symbols: Dict[str, Any] = {}
        self.parent = parent
        self._cached_lookups = {}

        if parent is None:
            self._initialize_builtins()

    def _initialize_builtins(self) -> None:
        """Initialize built-in constants and functions in global scope."""
        self.define("PI", math.pi)

        builtin_functions = {
            "print": BuiltInFunction("print", Runtime.Builtins.print_func, None),
            "input": BuiltInFunction("input", Runtime.Builtins.input_func, None),
            "str": BuiltInFunction("str", Runtime.Builtins.str_func, None),
            "int": BuiltInFunction("int", Runtime.Builtins.int_func, 1),
            "float": BuiltInFunction("float", Runtime.Builtins.float_func, 1),
            "len": BuiltInFunction("len", Runtime.Builtins.len_func, 1),
            "exit": BuiltInFunction("exit", Runtime.Builtins.exit_func, 1),
            "rand": BuiltInFunction("rand", Runtime.Builtins.rand_func, 0),
        }

        for name, func in builtin_functions.items():
            self.define(name, func)

    def lookup(self, name: str) -> Any:
        if name in self._cached_lookups:
            target_scope, value = self._cached_lookups[name]
            if name in target_scope.symbols and target_scope.symbols[name] is value:
                return value

        scope = self
        while scope:
            if name in scope.symbols:
                value = scope.symbols[name]
                self._cached_lookups[name] = (scope, value)
                return value
            scope = scope.parent

        raise RuntimeError(f"Undefined variable or function: {name}", scope=self)

    def define(self, name: str, value: Any) -> None:
        self.symbols[name] = value
        if name in self._cached_lookups:
            del self._cached_lookups[name]

    def assign(self, name: str, value: Any) -> None:
        scope = self
        while scope:
            if name in scope.symbols:
                scope.symbols[name] = value
                if name in self._cached_lookups:
                    self._cached_lookups[name] = (scope, value)

                print(f"{name} = {value}")
                return
            scope = scope.parent
        raise RuntimeError(f"Assignment to undefined variable: {name}", scope=self)


class Runtime:
    class Builtins:
        @staticmethod
        def print_func(args: List[Any]) -> None:
            try:
                print("".join(str(arg) for arg in args))
                return None
            except Exception as e:
                raise RuntimeError(f"Print error: {str(e)}")

        @staticmethod
        def input_func(args: List[Any]) -> str:
            try:
                return input("".join(str(arg) for arg in args))
            except Exception as e:
                raise RuntimeError(f"Input error: {str(e)}")

        @staticmethod
        def str_func(args: List[Any]) -> str:
            try:
                return "".join(str(arg) for arg in args)
            except Exception as e:
                raise RuntimeError(f"String conversion error: {str(e)}")

        @staticmethod
        def int_func(args: List[Any]) -> int:
            try:
                return int(args[0])
            except ValueError:
                raise RuntimeError(f"Cannot convert {args[0]} to int")
            except Exception as e:
                raise RuntimeError(f"Integer conversion error: {str(e)}")

        @staticmethod
        def float_func(args: List[Any]) -> float:
            try:
                return float(args[0])
            except ValueError:
                raise RuntimeError(f"Cannot convert {args[0]} to float")
            except Exception as e:
                raise RuntimeError(f"Float conversion error: {str(e)}")

        @staticmethod
        def len_func(args: List[Any]) -> int:
            try:
                return len(args[0])
            except TypeError:
                raise RuntimeError(
                    f"Object of type {type(args[0]).__name__} has no len()"
                )
            except Exception as e:
                raise RuntimeError(f"Length error: {str(e)}")

        @staticmethod
        def exit_func(args: List[Any]) -> None:
            try:
                exit(args[0])
            except Exception as e:
                raise RuntimeError(f"Exit error: {str(e)}")

        @staticmethod
        def rand_func(args: List[Any]) -> int:
            try:
                return random.randrange(0, sys.maxsize)
            except Exception as e:
                raise RuntimeError(f"Rand error: {str(e)}")

    def __init__(self, scope: Scope):
        self.scope = scope
        self._node_handlers = {
            NumberNode: self._eval_number,
            FloatNumberNode: self._eval_float,
            BoolNode: self._eval_bool,
            CharNode: self._eval_char,
            StringNode: self._eval_string,
            IdentifierNode: self._eval_identifier,
            ArrayNode: self._eval_array,
            ArrayAccessNode: self._eval_array_access,
            ArrayAssignmentNode: self._eval_array_assignment,
            UnaryOpNode: self._eval_unary_op,
            BinaryOpNode: self._eval_binary_op,
            FunctionCallNode: self._eval_function_call,
            FunctionDeclarationNode: self._eval_function_declaration,
            ReturnNode: self._eval_return,
            VariableDeclarationNode: self._eval_var_declaration,
            VariableAssignmentNode: self._eval_var_assignment,
            IfNode: self._eval_if,
            WhileNode: self._eval_while,
        }

        self._binary_op_handlers = {
            TokenType.LOGICAL_AND: lambda left, right: left and right,
            TokenType.LOGICAL_OR: lambda left, right: left or right,
            TokenType.EQUAL_EQUAL: lambda left, right: left == right,
            TokenType.BANG_EQUAL: lambda left, right: left != right,
            TokenType.GREATER: lambda left, right: left > right,
            TokenType.LESS: lambda left, right: left < right,
            TokenType.GREATER_EQUAL: lambda left, right: left >= right,
            TokenType.LESS_EQUAL: lambda left, right: left <= right,
            TokenType.PLUS: lambda left, right: left + right,
            TokenType.MINUS: lambda left, right: left - right,
            TokenType.MULTIPLY: lambda left, right: left * right,
            TokenType.DIVIDE: lambda left, right: left / right,
            TokenType.MODULO: lambda left, right: left % right,
            TokenType.BIT_OR: lambda left, right: left | right,
            TokenType.BIT_XOR: lambda left, right: left ^ right,
            TokenType.BIT_AND: lambda left, right: left & right,
            TokenType.BIT_LSH: lambda left, right: left << right,
            TokenType.BIT_RSH: lambda left, right: left >> right,
        }

        self._eval_cache = {}

    @lru_cache(maxsize=128)
    def _get_node_type(self, node):
        return type(node)

    def evaluate(self, node) -> Any:
        try:
            node_hash = getattr(node, "__hash__", None)
            if node_hash is not None:
                try:
                    cache_key = (node, id(self.scope))
                    if cache_key in self._eval_cache:
                        return self._eval_cache[cache_key]
                except:
                    pass

            handler = self._node_handlers.get(type(node))
            if handler:
                result = handler(node)

                if node_hash is not None:
                    try:
                        cache_key = (node, id(self.scope))
                        self._eval_cache[cache_key] = result
                    except:
                        pass

                return result

            raise RuntimeError(
                f"Unsupported node type: {type(node).__name__}",
                node=node,
                scope=self.scope,
            )
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(
                f"Evaluation error: {str(e)}", node=node, scope=self.scope
            )

    def _eval_number(self, node) -> int:
        return node.value

    def _eval_float(self, node) -> float:
        return node.value

    def _eval_bool(self, node) -> bool:
        return node.value

    def _eval_char(self, node) -> str:
        return chr(node.value)

    def _eval_string(self, node) -> str:
        return node.value

    def _eval_identifier(self, node) -> Any:
        try:
            return self.scope.lookup(node.name)
        except Exception:
            raise RuntimeError(
                f"Undefined variable or function: {node.name}",
                node=node,
                scope=self.scope,
            )

    def _eval_array(self, node) -> List[Any]:
        return [self.evaluate(element) for element in node.elements]

    def _eval_array_access(self, node) -> Any:
        array_value = self.evaluate(node.array)
        index_value = self.evaluate(node.index)

        if not isinstance(array_value, list):
            raise RuntimeError(
                f"Expected array, got {type(array_value).__name__}",
                node=node,
                scope=self.scope,
            )

        if not isinstance(index_value, int):
            raise RuntimeError(
                f"Array index must be an integer, got {type(index_value).__name__}",
                node=node,
                scope=self.scope,
            )

        if index_value < 0 or index_value >= len(array_value):
            raise RuntimeError(
                f"Array index out of bounds: {index_value}", node=node, scope=self.scope
            )

        return array_value[index_value]

    def _eval_array_assignment(self, node) -> Any:
        array_value = self.evaluate(node.array)
        index_value = self.evaluate(node.index)
        assigned_value = self.evaluate(node.value)

        if not isinstance(array_value, list):
            raise RuntimeError(
                f"Expected array, got {type(array_value).__name__}",
                node=node,
                scope=self.scope,
            )

        if not isinstance(index_value, int):
            raise RuntimeError(
                f"Array index must be an integer, got {type(index_value).__name__}",
                node=node,
                scope=self.scope,
            )

        if index_value < 0 or index_value >= len(array_value):
            raise RuntimeError(
                f"Array index out of bounds: {index_value}", node=node, scope=self.scope
            )

        array_value[index_value] = assigned_value
        return assigned_value

    def _eval_unary_op(self, node) -> Any:
        operand_value = self.evaluate(node.expr)

        if node.op == TokenType.PLUS:
            return +operand_value
        elif node.op == TokenType.MINUS:
            return -operand_value
        elif node.op == TokenType.LOGICAL_NOT:
            return not operand_value
        elif node.op == TokenType.BIT_NOT:
            return ~operand_value

        raise RuntimeError(
            f"Unsupported unary operation: {node.op}", node=node, scope=self.scope
        )

    def _eval_binary_op(self, node) -> Any:
        if node.op in (TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL):
            return self._eval_compound_assignment(node)

        if node.op == TokenType.LOGICAL_AND:
            left_value = self.evaluate(node.left)
            if not left_value:
                return False
            return self.evaluate(node.right)

        if node.op == TokenType.LOGICAL_OR:
            left_value = self.evaluate(node.left)
            if left_value:
                return True
            return self.evaluate(node.right)

        left_value = self.evaluate(node.left)
        right_value = self.evaluate(node.right)

        operation = self._binary_op_handlers.get(node.op)
        if operation:
            try:
                return operation(left_value, right_value)
            except TypeError:
                raise RuntimeError(
                    f"Incompatible types for operation {node.op}: {type(left_value).__name__} and {type(right_value).__name__}",
                    node=node,
                    scope=self.scope,
                )
            except ZeroDivisionError:
                raise RuntimeError("Division by zero", node=node, scope=self.scope)

        raise RuntimeError(
            f"Unsupported binary operation: {node.op}", node=node, scope=self.scope
        )

    def _eval_compound_assignment(self, node) -> Any:
        if not isinstance(node.left, IdentifierNode):
            raise RuntimeError(
                "Left side of compound assignment must be a variable",
                node=node,
                scope=self.scope,
            )

        left_value = self.scope.lookup(node.left.name)
        right_value = self.evaluate(node.right)

        if node.op == TokenType.PLUS_EQUAL:
            try:
                result = left_value + right_value
            except TypeError:
                raise RuntimeError(
                    f"Cannot add {type(left_value).__name__} and {type(right_value).__name__}",
                    node=node,
                    scope=self.scope,
                )
        elif node.op == TokenType.MINUS_EQUAL:
            try:
                result = left_value - right_value
            except TypeError:
                raise RuntimeError(
                    f"Cannot subtract {type(right_value).__name__} from {type(left_value).__name__}",
                    node=node,
                    scope=self.scope,
                )
        else:
            raise RuntimeError(
                f"Unsupported compound assignment: {node.op}",
                node=node,
                scope=self.scope,
            )

        self.scope.assign(node.left.name, result)

        return result

    def _eval_function_call(self, node) -> Any:
        func = self.scope.lookup(node.name)

        if not isinstance(func, Function):
            raise RuntimeError(
                f"Attempted to call a non-callable object: {node.name}",
                node=node,
                scope=self.scope,
            )

        arguments = [self.evaluate(arg) for arg in node.arguments]
        return func(arguments)

    def _eval_function_declaration(self, node) -> Function:
        func = UserFunction(node.name, node, self.scope)
        self.scope.define(node.name, func)
        return func

    def _eval_return(self, node) -> Any:
        return self.evaluate(node.value)

    def _eval_var_declaration(self, node) -> Any:
        value = self.evaluate(node.value)
        self.scope.define(node.name, value)
        return value

    def _eval_var_assignment(self, node) -> Any:
        value = self.evaluate(node.value)
        self.scope.assign(node.name, value)
        return value

    def _eval_if(self, node) -> Any:
        condition = self.evaluate(node.condition)
        if condition:
            runtime = Runtime(Scope(parent=self.scope))
            result = None
            for stmt in node.body:
                result = runtime.evaluate(stmt)
            return result
        return None

    def _eval_while(self, node) -> None:
        result = None
        while_scope = Scope(parent=self.scope)
        while_runtime = Runtime(while_scope)

        iteration = 0
        while while_runtime.evaluate(node.condition):
            result = None
            for stmt in node.body:
                result = while_runtime.evaluate(stmt)
                if isinstance(stmt, ReturnNode):
                    return result
            iteration += 1
            if iteration > 1000:
                raise RuntimeError("Maximum iteration limit reached")

        return result

    def execute(self, statements) -> Any:
        result = None
        for statement in statements:
            result = self.evaluate(statement)
        return result
