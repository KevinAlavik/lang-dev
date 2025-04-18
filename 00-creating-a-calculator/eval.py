import math
import ast
import lexer

function_table = {
    "sqrt": math.sqrt,
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
    else:
        raise ValueError(f"Unknown node type: {type(node)}")
