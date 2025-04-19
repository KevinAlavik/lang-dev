#!/usr/bin/env python3
import math
import time
import lexer
import ast
from eval import evaluate


def run_tests():
    test_cases = [
        # Basic arithmetic
        ("1 + 2", 3.0, "basic"),
        ("1.5 + 1.5", 3.0, "basic"),
        ("3 - 1", 2.0, "basic"),
        ("2 * 4", 8.0, "basic"),
        ("10 / 2", 5.0, "basic"),
        ("(2 + 3) * 4", 20.0, "basic"),
        ("3 + 2 * 5", 13.0, "precedence"),
        ("(3 + 2) * 5", 25.0, "precedence"),
        # Unary
        ("-(2 + 3)", -5.0, "unary"),
        ("+.5", 0.5, "unary"),
        ("-.5", -0.5, "unary"),
        ("-(-5)", 5.0, "unary"),
        ("+(+3)", 3.0, "unary"),
        # Floats
        (".5 + .5", 1.0, "float"),
        ("(.5 + .5) * 2", 2.0, "float"),
        ("0.1 + 0.2", 0.3, "float"),  # approximate
        ("3.1415", 3.1415, "float"),
        ("3.0 * 0.5 + 2", 3.5, "float"),
        # Complex expressions
        ("1 + 2 * 3 - 4 / 2", 5.0, "complex"),
        ("(1 + (2 + 3) * (4 - 1)) / 2", 8.0, "complex"),
        ("(((((1)))))", 1.0, "parens"),
        # Invalid expressions
        ("5.", ValueError, "invalid"),
        (".", ValueError, "invalid"),
        ("..5", ValueError, "invalid"),
        ("2 +", ValueError, "invalid"),
        ("*", ValueError, "invalid"),
        ("(1 + 2", ValueError, "invalid"),
        ("1 / 0", ValueError, "invalid"),
        ("abc", ValueError, "invalid"),
        # Advanced math
        ("sqrt(sqrt(9) * 3)", 3.0, "advanced"),
        ("PI", math.pi, "advanced"),
    ]

    passed = 0
    failed = 0
    total_time = 0.0

    print("Running tests...\n")

    for expr, expected, category in test_cases:
        start = time.perf_counter()
        try:
            tokens = lexer.tokenize(expr)
            tree = ast.parse(tokens)
            result = evaluate(tree)
            duration = (time.perf_counter() - start) * 1000

            if isinstance(expected, float):
                if abs(result - expected) < 1e-9:
                    print(
                        f"\033[92m✅ PASS\033[0m [{category:>10}] {expr:<30} = {result:.6f} ({duration:.2f}ms)"
                    )
                    passed += 1
                else:
                    print(
                        f"\033[91m❌ FAIL\033[0m [{category:>10}] {expr:<30} → Expected {expected}, got {result} ({duration:.2f}ms)"
                    )
                    failed += 1
            else:
                print(
                    f"\033[91m❌ FAIL\033[0m [{category:>10}] {expr:<30} → Expected error {expected.__name__}, got {result} ({duration:.2f}ms)"
                )
                failed += 1

        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            if isinstance(expected, type) and isinstance(e, expected):
                print(
                    f"\033[92m✅ PASS\033[0m [{category:>10}] {expr:<30} raised {e.__class__.__name__} ({duration:.2f}ms)"
                )
                passed += 1
            else:
                print(
                    f"\033[91m❌ FAIL\033[0m [{category:>10}] {expr:<30} → Unexpected error: {e} ({duration:.2f}ms)"
                )
                failed += 1

        total_time += duration

    print("\n=== Test Summary ===")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total Time: {total_time:.2f}ms")
    print(
        f"📊 Total Tests: {passed + failed} ({(passed / (passed + failed)) * 100:.1f}% passed)"
    )


if __name__ == "__main__":
    run_tests()
