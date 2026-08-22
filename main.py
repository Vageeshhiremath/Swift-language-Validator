import argparse
import sys

import lexer as lx
from lexer import tokens, lexer
from parser import parser
from semantic import check as type_check


def read_multiline_input(prompt="Enter Swift code (end with empty line):\n"):
    """Read multiline Swift code until an empty line."""
    print(prompt)
    lines = []
    while True:
        try:
            line = input()
            if not line.strip():  # Empty line ends input
                break
            lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\nExiting validator.")
            sys.exit(0)
    return "\n".join(lines)


def validate_swift_code(data):
    """
    Run lexical, syntax, and semantic validation for Swift subset.

    Returns a result dict instead of printing directly, so both the CLI
    and the test suite can consume the same structured output:
        {
            "status": "lexical_error" | "syntax_error" | "semantic_error" | "success",
            "errors": [list of error strings],
            "ast": the parsed AST, or None
        }
    """
    # NOTE: previously this reset a module-level `lexer_error` that was
    # imported once at import time (`from lexer import lexer_error`).
    # That created a stale local copy in main.py's namespace that never
    # reflected updates made inside lexer.py's t_error(). We now read
    # and write lx.lexer_error directly on the lexer module itself, so
    # the flag actually reflects what the lexer detected.
    lx.lexer_error = False

    lexer.lineno = 1
    lexer.input(data)
    result = parser.parse(data, lexer=lexer)

    if lx.lexer_error:
        return {"status": "lexical_error", "errors": ["Lexical error(s) found — invalid Swift syntax."], "ast": None}

    if result is None:
        return {"status": "syntax_error", "errors": ["Syntax Validation Failed."], "ast": None}

    ok, errors = type_check(result)
    if ok:
        return {"status": "success", "errors": [], "ast": result}
    return {"status": "semantic_error", "errors": errors, "ast": result}


def print_result(result):
    """Render a validate_swift_code() result the same way the original CLI did."""
    status = result["status"]
    if status == "lexical_error":
        print(f"\n [FAILURE] {result['errors'][0]}")
    elif status == "syntax_error":
        print(f"\n [FAILURE] {result['errors'][0]}")
    elif status == "semantic_error":
        print("\n[FAILURE] Semantic Validation Failed.")
        for e in result["errors"]:
            print(e)
    elif status == "success":
        print("\n [SUCCESS] Syntax Validation Passed.")


def run_repl():
    print("Swift Subset Syntax Validator (PLY)")
    print("Supports: Variables, Constants, Structures, Generics, and Protocols")
    print("Type 'quit' or press Ctrl+C to exit.")
    print("-" * 55)

    while True:
        try:
            data = read_multiline_input()
            if data.strip().lower() == 'quit':
                break
            if not data.strip():
                continue
            print_result(validate_swift_code(data))
            print("-" * 55)
        except KeyboardInterrupt:
            print("\nExiting validator.")
            break


def run_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = f.read()
    except OSError as e:
        print(f"[ERROR] Could not read file '{path}': {e}")
        sys.exit(1)

    if not data.strip():
        print(f"[ERROR] File '{path}' is empty.")
        sys.exit(1)

    print(f"Validating '{path}'...")
    print("-" * 55)
    result = validate_swift_code(data)
    print_result(result)
    print("-" * 55)

    # Non-zero exit code on failure — makes this usable as a CI/lint gate.
    sys.exit(0 if result["status"] == "success" else 1)


def main():
    arg_parser = argparse.ArgumentParser(
        description="Swift Subset Syntax Validator (PLY) — validates a Swift-like subset's "
                     "lexical, syntax, and basic semantic correctness."
    )
    arg_parser.add_argument(
        "--file", "-f", metavar="PATH",
        help="Validate a single .swift file instead of starting the interactive REPL."
    )
    args = arg_parser.parse_args()

    if args.file:
        run_file(args.file)
    else:
        run_repl()


if __name__ == '__main__':
    main()
