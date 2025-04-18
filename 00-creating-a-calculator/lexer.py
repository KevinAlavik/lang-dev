from enum import Enum, auto

class TokenType(Enum):
    NUMBER = auto()

    MULTIPLY = auto()
    PLUS = auto()
    MINUS = auto()
    DIVIDE = auto()
    LPAREN = auto()
    RPAREN = auto()

    def __str__(self):
        return self.name

token_map = {
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
}

def tokenize(input_expression):
    tokens = []
    pos = 0
    length = len(input_expression)

    while pos < length:
        current_char = input_expression[pos]

        # Skip spaces
        if current_char.isspace():
            pos += 1
            continue

        # Handle symbols and shit
        if current_char in token_map:
            tokens.append((token_map[current_char], current_char))
            pos += 1
            continue

        # Handle numbers (int and float)
        elif current_char.isdigit() or current_char == '.':
            number = ''
            dot_seen = False
            start_pos = pos

            while pos < length and (input_expression[pos].isdigit() or input_expression[pos] == '.'):
                if input_expression[pos] == '.':
                    if dot_seen:
                        raise ValueError("Invalid number format: multiple decimal points")
                    dot_seen = True
                number += input_expression[pos]
                pos += 1

            # validate number
            if number == '.' or number.endswith('.'):
                raise ValueError(f"Invalid number format: '{number}'")

            try:
                value = float(number)
            except ValueError:
                raise ValueError(f"Invalid number format: '{number}'")

            tokens.append((TokenType.NUMBER, value))
            continue

        else:
            raise ValueError(f"Invalid character: {current_char}")

    return tokens
