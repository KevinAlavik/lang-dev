from lexer import TokenType


# AST Nodes
class ASTNode:
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})"


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = int(value)


class FloatNumberNode(ASTNode):
    def __init__(self, value):
        self.value = float(value)


class CharNode(ASTNode):
    def __init__(self, value):
        self.value = value


class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value


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


class VariableDeclarationNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class VariableAssignmentNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class FunctionDeclarationNode(ASTNode):
    def __init__(self, name, arguments, body):
        self.name = name
        self.arguments = arguments
        self.body = body


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

    def next_token():
        return tokens[pos + 1] if pos + 1 < len(tokens) else (None, None)

    def eat():
        nonlocal pos
        token = current_token()
        pos += 1
        return token

    def expect(token_type, token_value=None, optional=False):
        nonlocal pos
        token_type_actual, token_value_actual = current_token()
        if token_type_actual == token_type and (
            token_value is None or token_value_actual == token_value
        ):
            token = current_token()
            pos += 1
            return token

        if optional:
            return None
        raise ValueError(
            f"Expected token: ({token_type}, {token_value}), got: ({token_type_actual}, {token_value_actual})"
        )

    def parse_primary():
        token_type, value = current_token()

        if token_type == TokenType.NUMBER:
            expect(TokenType.NUMBER)
            return NumberNode(value)

        if token_type == TokenType.FLOAT:
            expect(TokenType.FLOAT)
            return FloatNumberNode(value)

        elif token_type == TokenType.CHAR:
            expect(TokenType.CHAR)
            return CharNode(value)

        elif token_type == TokenType.STRING:
            expect(TokenType.STRING)
            return StringNode(value)

        elif token_type == TokenType.IDENTIFIER:
            expect(TokenType.IDENTIFIER)
            if current_token()[0] == TokenType.LPAREN:
                expect(TokenType.LPAREN)
                args = []
                if current_token()[0] != TokenType.RPAREN:
                    args.append(parse_expression())
                    while current_token()[0] == TokenType.COMMA:
                        eat()  # Eat the comma
                        args.append(parse_expression())
                expect(TokenType.RPAREN)
                return FunctionCallNode(value, args)
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

        if token_type == TokenType.KEYWORD and value == "fn":
            expect(TokenType.KEYWORD, "fn")
            return parse_function_declaration()

        if token_type == TokenType.KEYWORD and value == "return":
            expect(TokenType.KEYWORD, "return")
            expr = parse_expression()
            return ReturnNode(expr)

        if token_type == TokenType.KEYWORD and value == "var":
            expect(TokenType.KEYWORD, "var")
            token_type, var_name = expect(TokenType.IDENTIFIER)
            expect(TokenType.EQUAL)
            expr = parse_expression()
            return VariableDeclarationNode(var_name, expr)

        if token_type == TokenType.IDENTIFIER and next_token()[0] == TokenType.EQUAL:
            name = value
            eat()  # eat identifier
            expect(TokenType.EQUAL)
            expr = parse_expression()
            return VariableAssignmentNode(name, expr)

        return parse_expression()

    def parse_function_declaration():
        _, name = eat()
        expect(TokenType.LPAREN)

        arguments = []

        # Handle function arguments
        while True:
            token_type, value = current_token()

            if token_type == TokenType.RPAREN:
                break

            if token_type == TokenType.IDENTIFIER:
                arguments.append(IdentifierNode(value))
                eat()
            if current_token()[0] == TokenType.COMMA:
                eat()

            if current_token()[0] not in [
                TokenType.IDENTIFIER,
                TokenType.COMMA,
                TokenType.RPAREN,
            ]:
                raise ValueError(
                    f"Unexpected token in function arguments: {current_token()}"
                )

        expect(TokenType.RPAREN)
        expect(TokenType.LBRACE)

        body = []
        while current_token()[0] != TokenType.RBRACE:
            body.append(parse_statement())

        expect(TokenType.RBRACE)

        return FunctionDeclarationNode(name, arguments, body)

    statements = []
    while pos < len(tokens):
        statements.append(parse_statement())

    return statements
