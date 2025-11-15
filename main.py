import ply.lex as lex
import ply.yacc as yacc
import sys
from lexer import tokens, lexer, lexer_error
from parser import parser, check as type_check

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
    """Run lexical, syntax, and semantic validation for Swift subset."""
    global lexer_error
    lexer_error = False  # Reset before every parse

    lexer.lineno = 1
    lexer.input(data)
    result = parser.parse(data, lexer=lexer)

    # Step 1: Lexical check
    if lexer_error:
        print("\n [FAILURE] Lexical error(s) found — invalid Swift syntax.")
        return

    # Step 2: Syntax + Semantic checks
    if result is not None:
        ok, errors = type_check(result)
        if ok:
            print("\n [SUCCESS] Syntax Validation Passed.")
            #print("\n--- Abstract Syntax Tree (AST) ---")
            #print(result)
        else:
            print("\n[FAILURE] Semantic Validation Failed.")
            for e in errors:
                print(e)
    else:
        print("\n [FAILURE] Syntax Validation Failed.")

if __name__ == '__main__':
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
            validate_swift_code(data)
            print("-" * 55)
        except KeyboardInterrupt:
            print("\nExiting validator.")
            break
#T is place holder,var value is of any type,