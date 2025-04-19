from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()

    KEYWORD = auto()
    IDENTIFIER = auto()

    MULTIPLY = auto()
    PLUS = auto()
    MINUS = auto()
    DIVIDE = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    EQUAL = auto()

    STRING = auto()
    CHAR = auto()

    def __str__(self):
        return self.name


keyword_table = {"return", "fn", "var"}

token_map = {
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ",": TokenType.COMMA,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULTIPLY,
    "/": TokenType.DIVIDE,
    "=": TokenType.EQUAL,
}


def tokenize(input_expression):
    tokens = []
    pos = 0
    length = len(input_expression)

    while pos < length:
        current_char = input_expression[pos]

        # Skip whitespace
        if current_char.isspace():
            pos += 1
            continue

        # Skip comments
        if current_char == "#":
            while pos < length and input_expression[pos] != "\n":
                pos += 1
            pos += 1
            continue

        # Tokenize string literals
        if current_char == '"':
            pos += 1
            start_pos = pos
            while pos < length and input_expression[pos] != '"':
                pos += 1
            if pos >= length:
                raise ValueError("Unterminated string literal")
            string_value = input_expression[start_pos:pos]
            tokens.append((TokenType.STRING, string_value))
            pos += 1
            continue

        # Tokenize char literals
        if current_char == "'":
            pos += 1
            if pos >= length:
                raise ValueError("Unterminated character literal")

            if input_expression[pos] == "\\":  # Handle escape characters like '\n'
                pos += 1
                if pos >= length:
                    raise ValueError("Unterminated escape in character literal")
                char_value = "\\" + input_expression[pos]
                pos += 1
            else:
                char_value = input_expression[pos]
                pos += 1

            if pos >= length or input_expression[pos] != "'":
                raise ValueError("Unterminated or invalid character literal")

            tokens.append((TokenType.CHAR, char_value))
            pos += 1
            continue

        # Tokenize keywords and identifiers
        if current_char.isalpha():
            start_pos = pos
            while pos < length and (
                input_expression[pos].isalnum() or input_expression[pos] == "_"
            ):
                pos += 1
            word = input_expression[start_pos:pos]
            if word in keyword_table:
                tokens.append((TokenType.KEYWORD, word))
            else:
                tokens.append((TokenType.IDENTIFIER, word))
            continue

        # Tokenize numbers
        if current_char.isdigit():
            start_pos = pos
            while pos < length and input_expression[pos].isdigit():
                pos += 1
            number = input_expression[start_pos:pos]
            tokens.append((TokenType.NUMBER, number))
            continue

        # Tokenize symbols
        if current_char in token_map:
            tokens.append((token_map[current_char], current_char))
            pos += 1
            continue

        raise ValueError(f"Unknown character: {current_char}")

    return tokens
