# Swift Parser using PLY
import ply.yacc as yacc
from lexer import tokens
precedence = (
    ('left', 'STRUCT'),
    ('left', 'LET', 'VAR'),
    ('left', 'COLON'),
    ('left', 'ASSIGN'),
    ('left', 'COMMA'),
    ('left', 'LANGLE', 'RANGLE'),
    ('left', 'WHERE'),
)

# --- Program Root ---
def p_program(p):
    '''program : declaration_list'''
    p[0] = ('program', p[1])

def p_declaration_list(p):
    '''declaration_list : declaration
                        | declaration_list declaration'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_declaration(p):
    '''declaration : var_declaration
                   | struct_declaration
                   | protocol_declaration'''
    p[0] = p[1]

# --- Variable and Constant Declarations ---
def p_var_declaration(p):
    '''var_declaration : LET ID type_annotation_opt assign_opt semicolon_opt
                       | VAR ID type_annotation_opt assign_opt semicolon_opt'''
    p[0] = ('var_decl', p[1], p[2], p[3], p[4])

def p_semicolon_opt(p):
    '''semicolon_opt : SEMICOLON
                     | empty'''
    # Optional statement terminator, matching real Swift's optional ';'.
    pass

def p_type_annotation_opt(p):
    '''type_annotation_opt : COLON ID
                           | empty'''
    if len(p) == 3:
        p[0] = ('type_annotation', p[2])
    else:
        p[0] = None

def p_assign_opt(p):
    '''assign_opt : ASSIGN expression
                  | empty'''
    if len(p) == 3:
        p[0] = ('assignment', p[2])
    else:
        p[0] = None

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = ('expression', 'NUMBER', p[1])

def p_expression_string(p):
    'expression : STRING'
    p[0] = ('expression', 'STRING', p[1])

def p_expression_id(p):
    'expression : ID'
    p[0] = ('expression', 'ID', p[1])

def p_expression_true(p):
    'expression : TRUE'
    p[0] = ('expression', 'TRUE', True)

def p_expression_false(p):
    'expression : FALSE'
    p[0] = ('expression', 'FALSE', False)

# --- Structures ---

def p_struct_declaration(p):
    '''struct_declaration : STRUCT ID generic_params_opt where_clause_opt LBRACE property_declaration_list RBRACE'''
    p[0] = ('struct_decl', p[2], p[3], p[4], p[6])

def p_generic_params_opt(p):
    '''generic_params_opt : generic_params
                          | empty'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None

def p_where_clause_opt(p):
    '''where_clause_opt : where_clause
                        | empty'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None

def p_property_declaration_list(p):
    '''property_declaration_list : var_declaration
                                 | property_declaration_list var_declaration
                                 | empty'''
    if len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# --- Generics ---

def p_generic_params(p):
    'generic_params : LANGLE generic_parameter_list RANGLE'
    p[0] = ('generic_params', p[2])

def p_generic_parameter_list(p):
    '''generic_parameter_list : generic_parameter
                              | generic_parameter_list COMMA generic_parameter'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_generic_parameter(p):
    '''generic_parameter : ID
                         | constraint'''
    p[0] = p[1]

# --- Where Clause ---
def p_where_clause(p):
    'where_clause : WHERE constraint_list'
    p[0] = ('where_clause', p[2])

def p_constraint_list(p):
    '''constraint_list : constraint
                       | constraint_list COMMA constraint'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_constraint(p):
    '''constraint : ID COLON ID'''  # e.g., T: Equatable
    p[0] = ('constraint', p[1], p[3])

# --- Protocol Declaration ---
def p_protocol_declaration(p):
    '''protocol_declaration : PROTOCOL ID LBRACE RBRACE
                            | PROTOCOL ID'''
    if len(p) == 3:
        p[0] = ('protocol_decl', p[2])
    else:
        p[0] = ('protocol_decl', p[2])

# --- Empty Production ---
def p_empty(p):
    'empty :'
    pass

# --- Error Handling ---
def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ('{p.value}') on line {p.lineno}")
    else:
        print("Syntax error at EOF")

# Build the parser
parser = yacc.yacc(write_tables=False)

# Semantic analysis (type checking, symbol table) now lives in
# semantic.py — see that file for check() and infer_literal_type().
# It's imported from there by main.py, not re-exported here, to keep
# parser.py responsible for grammar only.
