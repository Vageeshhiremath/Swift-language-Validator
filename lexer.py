import ply.lex as lex

# Track lexical errors for main.py
lexer_error = False

# Reserved keywords in Swift subset
reserved = {
    'struct': 'STRUCT',
    'var': 'VAR',
    'let': 'LET',
    'where': 'WHERE',
    'protocol': 'PROTOCOL',
    'true': 'TRUE',
    'false': 'FALSE',
}

# List of token names
tokens = [
    'ID', 'NUMBER', 'STRING', 'ASSIGN', 'COLON', 'COMMA',
    'LBRACE', 'RBRACE', 'LANGLE', 'RANGLE', 'SEMICOLON',
] + list(reserved.values())

# Regular expressions for tokens
t_ASSIGN = r'='
t_COLON = r':'
t_COMMA = r','
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LANGLE = r'<'
t_RANGLE = r'>'
t_SEMICOLON = r';'

# Identifier (variable, struct, etc.)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Number (int/float/scientific)
def t_NUMBER(t):
    r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
    s = t.value
    if ('.' in s) or ('e' in s) or ('E' in s):
        try:
            t.value = float(s)
        except Exception:
            t.value = s
    else:
        try:
            t.value = int(s)
        except Exception:
            t.value = s
    return t

# String literal
def t_STRING(t):
    r'\"([^\\\n]|(\\.))*?\"'
    t.value = t.value[1:-1]
    return t

# Single-line comment
def t_COMMENT(t):
    r'//.*'
    pass

# Ignore whitespace
t_ignore = ' \t\r\n'

# Handle newlines
def t_newline(t):
    r'(\r\n|\n|\r)+'
    t.lexer.lineno += len(t.value)

# Error handling
def t_error(t):
    global lexer_error
    print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    lexer_error = True
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Test code
if __name__ == '__main__':
    data = """
    struct student {
        let name : String = "Vageesh"
        let Roll : Int = 21
        let age : Int = 18
        let percentage : Float = 98.5
    }
    """
    lexer.input(data)
    print("=== TOKENS ===")
    for tok in lexer:
        print(f"{tok.type:<10} {tok.value}")
