from lexer import TokenType


# AST Nodes
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


class ReturnNode(ASTNode):
    def __init__(self, return_value):
        self.return_value = return_value


def print(node):
    if isinstance(node, NumberNode):
        return str(node.value)

    elif isinstance(node, IdentifierNode):
        return node.name

    elif isinstance(node, UnaryOpNode):
        op_name = node.op.name.capitalize()
        return f"{op_name}({print(node.expr)})"

    elif isinstance(node, BinaryOpNode):
        op_name = node.op.name.capitalize()
        return f"{op_name}({print(node.left)}, {print(node.right)})"

    elif isinstance(node, FunctionCallNode):
        return f"{node.name}({print(node.argument)})"

    elif isinstance(node, ReturnNode):
        return f"Return({print(node.return_value)})"

    else:
        return f"Unknown({node})"


# Operator precedence
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

    def expect(token_type, token_value=None):
        nonlocal pos
        token_type_actual, token_value_actual = current_token()
        if token_type_actual == token_type and (
            token_value is None or token_value_actual == token_value
        ):
            token = current_token()
            pos += 1
            return token
        raise ValueError(
            f"Expected token: ({token_type}, {token_value}), got: ({token_type_actual}, {token_value_actual})"
        )

    def parse_primary():
        token_type, value = current_token()

        if token_type == TokenType.NUMBER:
            expect(TokenType.NUMBER)
            return NumberNode(value)

        elif token_type == TokenType.IDENTIFIER:
            expect(TokenType.IDENTIFIER)
            if current_token()[0] == TokenType.LPAREN:
                expect(TokenType.LPAREN)
                argument = parse_expression()
                expect(TokenType.RPAREN)
                return FunctionCallNode(value, argument)
            return IdentifierNode(value)

        elif token_type == TokenType.LPAREN:
            expect(TokenType.LPAREN)
            expr = parse_expression()
            expect(TokenType.RPAREN)
            return expr

        raise ValueError(f"Unexpected token in primary: {token_type}")

    def parse_unary():
        token_type, _ = current_token()
        if token_type in (TokenType.PLUS, TokenType.MINUS):
            op_token, _ = expect(token_type)
            operand = parse_unary()
            return UnaryOpNode(op_token, operand)
        return parse_primary()

    def parse_binop(min_prec=0):
        left = parse_unary()

        while True:
            token_type, _ = current_token()
            if token_type not in PRECEDENCE:
                break

            prec = PRECEDENCE[token_type]
            if prec < min_prec:
                break

            op_token, _ = expect(token_type)
            right = parse_binop(prec + 1)
            left = BinaryOpNode(left, op_token, right)

        return left

    def parse_expression():
        return parse_binop()

    def parse_statement():
        token_type, value = current_token()

        if token_type == TokenType.KEYWORD and value == "return":
            expect(TokenType.KEYWORD, "return")
            expr = parse_expression()
            return ReturnNode(expr)

        return parse_expression()

    return parse_statement()
