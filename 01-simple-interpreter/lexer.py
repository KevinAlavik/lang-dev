from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    FLOAT = auto()
    BOOL = auto()

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

    GREATER = auto()
    LESS = auto()
    EQUAL_EQUAL = auto()
    BANG_EQUAL = auto()
    GREATER_EQUAL = auto()
    LESS_EQUAL = auto()
    LOGICAL_AND = auto()
    LOGICAL_OR = auto()

    PLUS_EQUAL = auto()
    MINUS_EQUAL = auto()

    STRING = auto()
    CHAR = auto()

    def __str__(self):
        return self.name


# Keyword table for reserved keywords
keyword_table = {
    "return",
    "fn",
    "var",
    "if",
    "else",
    "while",
}

# Token map for symbols and operators
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
    ">": TokenType.GREATER,
    "<": TokenType.LESS,
    "!=": TokenType.BANG_EQUAL,
    ">=": TokenType.GREATER_EQUAL,
    "<=": TokenType.LESS_EQUAL,
    "==": TokenType.EQUAL_EQUAL,
    "||": TokenType.LOGICAL_OR,
    "&&": TokenType.LOGICAL_AND,
    "+=": TokenType.PLUS_EQUAL,
    "-=": TokenType.MINUS_EQUAL,
}

# Special table for special keywords like "True" and "False"
special_table = {
    "True": TokenType.BOOL,
    "False": TokenType.BOOL,
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

        # Skip comments (# or //)
        if current_char == "#" or (
            current_char == "/" and input_expression[pos + 1] == "/"
        ):
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
            elif word in special_table:
                tokens.append((special_table[word], word))
            else:
                tokens.append((TokenType.IDENTIFIER, word))
            continue

        # Numbers (float and int)
        elif current_char.isdigit() or current_char == ".":
            number = ""
            dot_seen = False

            while pos < length and (
                input_expression[pos].isdigit() or input_expression[pos] == "."
            ):
                if input_expression[pos] == ".":
                    if dot_seen:
                        raise ValueError(
                            "Invalid number format: multiple decimal points"
                        )
                    dot_seen = True
                number += input_expression[pos]
                pos += 1

            if number == "." or number.endswith("."):
                raise ValueError(f"Invalid number format: '{number}'")

            if dot_seen:
                tokens.append((TokenType.FLOAT, float(number)))
            else:
                tokens.append((TokenType.NUMBER, int(number)))
            continue

        # Check for two-character operators like '!=' and '>='
        if pos + 1 < length:
            two_char_operator = input_expression[pos : pos + 2]
            if two_char_operator in token_map:
                tokens.append((token_map[two_char_operator], two_char_operator))
                pos += 2
                continue

        # Tokenize symbols (single characters)
        if current_char in token_map:
            tokens.append((token_map[current_char], current_char))
            pos += 1
            continue

        raise ValueError(f"Unknown character: {current_char}")

    return tokens
