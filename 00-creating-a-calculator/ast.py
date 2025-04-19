from lexer import TokenType
import math


class ASTNode:
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})"


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = float(value)


class UnaryOpNode(ASTNode):
    def __init__(self, op_token, expr):
        self.op = op_token
        self.expr = expr


class BinaryOpNode(ASTNode):
    def __init__(self, left, op_token, right):
        self.left = left
        self.op = op_token
        self.right = right


class FunctionCallNode(ASTNode):
    def __init__(self, name, argument):
        self.name = name
        self.argument = argument


class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name


def pretty_print(node, indent="", is_last=True):
    marker = "└── " if is_last else "├── "

    if isinstance(node, NumberNode):
        print(f"{indent}{marker}Number({node.value})")
    elif isinstance(node, UnaryOpNode):
        print(f"{indent}{marker}UnaryOp({node.op.name})")
        pretty_print(node.expr, indent + "    ", True)
    elif isinstance(node, BinaryOpNode):
        print(f"{indent}{marker}BinaryOp({node.op.name})")
        indent += "    " if is_last else "│   "
        pretty_print(node.left, indent, False)
        pretty_print(node.right, indent, True)
    elif isinstance(node, FunctionCallNode):
        print(f"{indent}{marker}FunctionCall({node.name})")
        pretty_print(node.argument, indent + "    ", True)
    else:
        print(f"{indent}{marker}UnknownNode({node})")


def compact_print(node):
    if isinstance(node, NumberNode):
        return str(node.value)
    elif isinstance(node, UnaryOpNode):
        op_name = node.op.name.capitalize()
        return f"{op_name}({compact_print(node.expr)})"
    elif isinstance(node, BinaryOpNode):
        op_name = node.op.name.capitalize()
        return f"{op_name}({compact_print(node.left)}, {compact_print(node.right)})"
    elif isinstance(node, FunctionCallNode):
        return f"{node.name.capitalize()}({compact_print(node.argument)})"
    else:
        return f"Unknown({node})"


PRECEDENCE = {
    TokenType.PLUS: 1,
    TokenType.MINUS: 1,
    TokenType.MULTIPLY: 2,
    TokenType.DIVIDE: 2,
}


def parse(tokens):
    pos = 0

    def current_token():
        return tokens[pos] if pos < len(tokens) else (None, None)

    def eat():
        nonlocal pos
        token = current_token()
        pos += 1
        return token

    def parse_primary():
        token_type, value = eat()

        if token_type == TokenType.NUMBER:
            return NumberNode(value)

        elif token_type == TokenType.LPAREN:
            expr = parse_expression()
            if current_token()[0] != TokenType.RPAREN:
                raise ValueError("Expected ')'")
            eat()
            return expr

        elif token_type == TokenType.MINUS:
            expr = parse_primary()
            return UnaryOpNode(TokenType.MINUS, expr)

        elif token_type == TokenType.PLUS:
            expr = parse_primary()
            return UnaryOpNode(TokenType.PLUS, expr)

        elif token_type == TokenType.IDENTIFIER:
            if current_token()[0] == TokenType.LPAREN:
                func_name = value
                eat()  # Consume '('
                argument = parse_expression()
                if current_token()[0] != TokenType.RPAREN:
                    raise ValueError(f"Expected ')'")
                eat()  # Consume ')'
                return FunctionCallNode(func_name, argument)
            else:
                return IdentifierNode(value)

        else:
            raise ValueError(f"Unexpected token: {token_type}")

    def parse_expression(precedence=0):
        left = parse_primary()

        while True:
            token_type, value = current_token()
            if token_type not in PRECEDENCE:
                break

            token_prec = PRECEDENCE[token_type]
            if token_prec < precedence:
                break

            op_token = eat()
            right = parse_expression(token_prec + 1)
            left = BinaryOpNode(left, op_token[0], right)

        return left

    return parse_expression()
