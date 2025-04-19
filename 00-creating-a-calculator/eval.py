import ast
import lexer
import math

function_table = {
    "sqrt": math.sqrt,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "degrees": math.degrees,
    "radians": math.radians,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial,
}

identifier_table = {
    "PI": math.pi,
    "E": math.e,
    "TAU": math.tau,
    "INF": math.inf,
    "NAN": math.nan,
}


def evaluate(node):
    if isinstance(node, ast.NumberNode):
        return node.value
    elif isinstance(node, ast.UnaryOpNode):
        expr_value = evaluate(node.expr)
        if node.op == lexer.TokenType.MINUS:
            return -expr_value
        elif node.op == lexer.TokenType.PLUS:
            return expr_value
        else:
            raise ValueError(f"Unknown operator: {node.op}")
    elif isinstance(node, ast.BinaryOpNode):
        left_value = evaluate(node.left)
        right_value = evaluate(node.right)
        if node.op == lexer.TokenType.PLUS:
            return left_value + right_value
        elif node.op == lexer.TokenType.MINUS:
            return left_value - right_value
        elif node.op == lexer.TokenType.MULTIPLY:
            return left_value * right_value
        elif node.op == lexer.TokenType.DIVIDE:
            if right_value == 0:
                raise ValueError("Division by zero")
            return left_value / right_value
        else:
            raise ValueError(f"Unknown operator: {node.op}")
    elif isinstance(node, ast.FunctionCallNode):
        # Get the function
        func = function_table.get(node.name)
        if func is None:
            raise ValueError(f"Unknown function: {node.name}")

        # Evaluate the argument
        arg_value = evaluate(node.argument)

        # Call the function with the evaluated argument
        return func(arg_value)
    elif isinstance(node, ast.IdentifierNode):
        value = identifier_table.get(node.name)
        if value is None:
            raise ValueError(f"Unknown identifier: {node.name}")
        return value
    else:
        raise ValueError(f"Unknown node type: {type(node)}")
