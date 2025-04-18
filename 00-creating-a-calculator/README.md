# Kevin's Simple Calculator Documentation

Kevin's Simple Calculator is a lightweight and simple arithmetic expression evaluator that supports basic arithmetic operations, functions, and variables. The calculator consists of three main components: lexer, AST (abstract syntax tree) representation, and evaluation functions.

## Supported Features

### Arithmetic Operations:
The calculator supports the following arithmetic operations:
- **Addition (+)**: Adds two numbers.
- **Subtraction (-)**: Subtracts one number from another.
- **Multiplication (*)**: Multiplies two numbers.
- **Division (/)**: Divides one number by another. Division by zero will raise an error.

### Parentheses:
- The calculator supports parentheses `(` and `)` to group expressions and define precedence.

### Functions:
The calculator supports the following built-in mathematical functions:
- **sqrt(x)**: Returns the square root of `x`.
- **exp(x)**: Returns `e^x` (exponential function).
- **log(x)**: Returns the natural logarithm (log base `e`) of `x`.
- **log10(x)**: Returns the logarithm (log base 10) of `x`.
- **sin(x)**: Returns the sine of `x` (in radians).
- **cos(x)**: Returns the cosine of `x` (in radians).
- **tan(x)**: Returns the tangent of `x` (in radians).
- **asin(x)**: Returns the arcsine of `x` (in radians).
- **acos(x)**: Returns the arccosine of `x` (in radians).
- **atan(x)**: Returns the arctangent of `x` (in radians).
- **sinh(x)**: Returns the hyperbolic sine of `x`.
- **cosh(x)**: Returns the hyperbolic cosine of `x`.
- **tanh(x)**: Returns the hyperbolic tangent of `x`.
- **degrees(x)**: Converts `x` from radians to degrees.
- **radians(x)**: Converts `x` from degrees to radians.
- **ceil(x)**: Returns the smallest integer greater than or equal to `x`.
- **floor(x)**: Returns the largest integer less than or equal to `x`.
- **factorial(x)**: Returns the factorial of `x`.

### Constants:
The following constants are predefined:
- **PI**: The mathematical constant π.
- **E**: The mathematical constant e.
- **TAU**: The mathematical constant τ (2π).
- **INF**: Represents infinity.
- **NAN**: Represents "Not a Number."

## Core Components

### Lexer:
The lexer is responsible for converting the input expression (a string) into a list of tokens. The supported token types are:
- **NUMBER**: Represents numeric values (both integers and floats).
- **IDENTIFIER**: Represents variable names and function names.
- **MULTIPLY**: The multiplication operator (`*`).
- **PLUS**: The addition operator (`+`).
- **MINUS**: The subtraction operator (`-`).
- **DIVIDE**: The division operator (`/`).
- **LPAREN**: The left parenthesis `(`.
- **RPAREN**: The right parenthesis `)`.

### AST (Abstract Syntax Tree):
The AST represents the structure of the parsed expression. The nodes of the AST are:
- **NumberNode**: Represents a numeric value.
- **UnaryOpNode**: Represents a unary operation (e.g., negation or positive).
- **BinaryOpNode**: Represents a binary operation (e.g., addition, multiplication).
- **FunctionCallNode**: Represents a function call.
- **IdentifierNode**: Represents a variable or constant.

### Evaluation:
The evaluator interprets the AST and computes the result of the expression. It supports:
- **Numeric operations**: Evaluating numbers, unary operations (positive/negative), binary operations (addition, subtraction, multiplication, division).
- **Function calls**: Evaluating built-in functions such as `sqrt`, `log`, and `sin`.
- **Identifiers**: Accessing predefined constants such as `PI` or `E`.

## Example Usage

### Input Expression:
```text
(3 + 5) * sqrt(16)
```

### Lexer Output:
```python
[
    (TokenType.LPAREN, '('),
    (TokenType.NUMBER, 3),
    (TokenType.PLUS, '+'),
    (TokenType.NUMBER, 5),
    (TokenType.RPAREN, ')'),
    (TokenType.MULTIPLY, '*'),
    (TokenType.IDENTIFIER, 'sqrt'),
    (TokenType.LPAREN, '('),
    (TokenType.NUMBER, 16),
    (TokenType.RPAREN, ')')
]
```

### AST Output:
```python
BinaryOpNode(
    left=BinaryOpNode(
        left=NumberNode(3),
        op=TokenType.PLUS,
        right=NumberNode(5)
    ),
    op=TokenType.MULTIPLY,
    right=FunctionCallNode(
        name='sqrt',
        argument=NumberNode(16)
    )
)
```

### Evaluation Output:
```python
Result: 32.0
```

## Error Handling
- **Invalid characters**: The lexer will throw an error if an invalid character is encountered.
- **Invalid number format**: The lexer will throw an error if a number is not formatted correctly (e.g., multiple decimal points).
- **Unknown operator**: The evaluator will throw an error if an unsupported operator is encountered.
- **Unknown function**: The evaluator will throw an error if an unknown function is called.
- **Unknown identifier**: The evaluator will throw an error if an unknown variable is used.
