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

    def __str__(self):
        return self.name


keyword_table = {"return"}

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

        # Skip comments (anything starting with '#')
        if current_char == "#":
            while pos < length and input_expression[pos] != "\n":
                pos += 1
            # Skip the newline character after the comment
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
                tokens.append(
                    (TokenType.IDENTIFIER, word)
                )  # If it's not a keyword, treat it as an identifier
            continue

        # Tokenize numbers (only integers for now)
        if current_char.isdigit():
            start_pos = pos
            while pos < length and input_expression[pos].isdigit():
                pos += 1
            number = input_expression[start_pos:pos]
            tokens.append((TokenType.NUMBER, number))
            continue

        # Tokenize single char tokens using the token_map
        if current_char in token_map:
            tokens.append((token_map[current_char], current_char))
            pos += 1
            continue

        raise ValueError(f"Unknown character: {current_char}")

    return tokens
