from enum import Enum, auto


class TokenType(Enum):
    NUMBER = auto()
    IDENTIFIER = auto()
    MULTIPLY = auto()
    PLUS = auto()
    MINUS = auto()
    DIVIDE = auto()
    LPAREN = auto()
    RPAREN = auto()

    def __str__(self):
        return self.name


token_map = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULTIPLY,
    "/": TokenType.DIVIDE,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
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

        # Symbols like + - * / ( )
        if current_char in token_map:
            tokens.append((token_map[current_char], current_char))
            pos += 1
            continue

        # Numbers (float or int)
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

            tokens.append((TokenType.NUMBER, float(number)))
            continue

        # Identifiers
        elif current_char.isalpha():
            ident = ""
            while pos < length and (
                input_expression[pos].isalnum() or input_expression[pos] == "_"
            ):
                ident += input_expression[pos]
                pos += 1

            tokens.append((TokenType.IDENTIFIER, ident))
            continue

        else:
            raise ValueError(f"Invalid character: {current_char}")

    return tokens
