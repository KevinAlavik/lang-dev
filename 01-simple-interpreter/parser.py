from lexer import TokenType


# AST Nodes
class ASTNode:
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})"


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value


class FloatNumberNode(ASTNode):
    def __init__(self, value):
        self.value = value


class BoolNode(ASTNode):
    def __init__(self, value):
        self.value = value


class CharNode(ASTNode):
    def __init__(self, value):
        self.value = ord(value)


class StringNode(ASTNode):
    def __init__(self, value):
        self.value = str(value)


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
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name


class ReturnNode(ASTNode):
    def __init__(self, return_value):
        self.value = return_value


class VariableDeclarationNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class VariableAccessNode(ASTNode):
    def __init__(self, variable, index):
        self.variable = variable
        self.index = index


class VariableAssignmentNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class ArrayNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements


class ArrayAccessNode(ASTNode):
    def __init__(self, array, index):
        self.array = array
        self.index = index


class ArrayAssignmentNode(ASTNode):
    def __init__(self, array, index, value):
        self.array = array
        self.index = index
        self.value = value


class FunctionDeclarationNode(ASTNode):
    def __init__(self, name, arguments, body):
        self.name = name
        self.arguments = arguments
        self.body = body


class IfNode(ASTNode):
    def __init__(self, condition, body, else_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body


class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


# (type, precedence)
binops = {
    TokenType.PLUS: 2,
    TokenType.MINUS: 2,
    TokenType.MULTIPLY: 3,
    TokenType.DIVIDE: 3,
    TokenType.MODULO: 3,
    # Comparison
    TokenType.EQUAL_EQUAL: 1,
    TokenType.BANG_EQUAL: 1,
    TokenType.LESS: 1,
    TokenType.GREATER: 1,
    TokenType.LESS_EQUAL: 1,
    TokenType.GREATER_EQUAL: 1,
    # Logical
    TokenType.LOGICAL_AND: 0,
    TokenType.LOGICAL_OR: 0,
    # Etc
    TokenType.PLUS_EQUAL: 0,
    TokenType.MINUS_EQUAL: 0,
    # Bitwise
    TokenType.BIT_OR: 4,
    TokenType.BIT_XOR: 4,
    TokenType.BIT_AND: 4,
    TokenType.BIT_NOT: 4,
    TokenType.BIT_LSH: 4,
    TokenType.BIT_RSH: 4,
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
            return eat()

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

        if token_type == TokenType.BOOL:
            expect(TokenType.BOOL)
            return BoolNode(value)

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
                        eat()
                        args.append(parse_expression())
                expect(TokenType.RPAREN)
                return FunctionCallNode(value, args)
            elif current_token()[0] == TokenType.LBRACKET:
                # Handle array access: arr[0]
                expect(TokenType.LBRACKET)
                index = parse_expression()
                expect(TokenType.RBRACKET)
                return ArrayAccessNode(IdentifierNode(value), index)
            return IdentifierNode(value)

        elif token_type == TokenType.LPAREN:
            expect(TokenType.LPAREN)
            expr = parse_expression()
            expect(TokenType.RPAREN)
            return expr

        # Handle arrays
        elif token_type == TokenType.LBRACKET:
            expect(TokenType.LBRACKET)
            elements = []

            # Parse elements inside the array
            if current_token()[0] != TokenType.RBRACKET:
                elements.append(parse_expression())
                while current_token()[0] == TokenType.COMMA:
                    eat()
                    elements.append(parse_expression())

            expect(TokenType.RBRACKET)
            return ArrayNode(elements)

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
            if token_type not in binops:
                break

            prec = binops[token_type]
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

        # Function declaration
        if token_type == TokenType.KEYWORD and value == "fn":
            expect(TokenType.KEYWORD, "fn")
            return parse_function_declaration()

        # If statement
        if token_type == TokenType.KEYWORD and value == "if":
            expect(TokenType.KEYWORD, "if")
            return parse_if()

        # While statement
        if token_type == TokenType.KEYWORD and value == "while":
            expect(TokenType.KEYWORD, "while")
            return parse_while()

        # Return statement
        if token_type == TokenType.KEYWORD and value == "return":
            expect(TokenType.KEYWORD, "return")
            expr = parse_expression()
            return ReturnNode(expr)

        # Variable declaration
        if token_type == TokenType.KEYWORD and value == "var":
            expect(TokenType.KEYWORD, "var")
            token_type, var_name = expect(TokenType.IDENTIFIER)
            expect(TokenType.EQUAL)
            expr = parse_expression()
            return VariableDeclarationNode(var_name, expr)

        # Variable assignment
        if token_type == TokenType.IDENTIFIER and next_token()[0] == TokenType.EQUAL:
            name = value
            eat()
            expect(TokenType.EQUAL)
            expr = parse_expression()
            return VariableAssignmentNode(name, expr)

        # Array assignment
        if token_type == TokenType.IDENTIFIER and (
            next_token()[0] == TokenType.KEYWORD and next_token()[1] == "at"
        ):
            name = value
            eat()
            expect(TokenType.KEYWORD, "at")
            index = parse_expression()
            expect(TokenType.EQUAL)
            expr = parse_expression()
            return ArrayAssignmentNode(IdentifierNode(name), index, expr)

        # General expression
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

    def parse_if():
        expect(TokenType.LPAREN)

        condition = parse_expression()

        expect(TokenType.RPAREN)
        body = []
        if current_token()[0] == TokenType.LBRACE:
            expect(TokenType.LBRACE)
            while current_token()[0] != TokenType.RBRACE:
                body.append(parse_statement())
            expect(TokenType.RBRACE)
        else:
            body.append(parse_statement())

        # Check for the else block
        else_body = None
        if current_token()[0] == TokenType.KEYWORD and current_token()[1] == "else":
            expect(TokenType.KEYWORD, "else")
            if current_token()[0] == TokenType.LBRACE:
                expect(TokenType.LBRACE)
                else_body = []
                while current_token()[0] != TokenType.RBRACE:
                    else_body.append(parse_statement())
                expect(TokenType.RBRACE)
            else:
                else_body = [parse_statement()]

        return IfNode(condition, body, else_body)

    def parse_while():
        expect(TokenType.LPAREN)
        condition = parse_expression()
        expect(TokenType.RPAREN)
        body = []
        if current_token()[0] == TokenType.LBRACE:
            expect(TokenType.LBRACE)
            while current_token()[0] != TokenType.RBRACE:
                body.append(parse_statement())
            expect(TokenType.RBRACE)
        else:
            body.append(parse_statement())

        return WhileNode(condition, body)

    # "main"
    statements = []
    while pos < len(tokens):
        statements.append(parse_statement())

    return statements
