"""
Semantic analysis for the Swift-subset validator.

Takes the AST produced by parser.py and checks:
- declared type vs. assigned literal type (var_decl, both top-level and
  inside struct properties)
- use of undefined identifiers in assignments

This was previously embedded at the bottom of parser.py. Splitting it
out keeps each stage of the pipeline (lex -> parse -> check) in its own
file, which is where new semantic rules (Phase 2+) should be added
rather than growing parser.py further.
"""

from typing import Tuple, List, Dict


def infer_literal_type(value) -> str:
    if isinstance(value, int):
        return 'Int'
    if isinstance(value, float):
        return 'Float'
    if isinstance(value, str):
        if value in ('true', 'false'):
            return 'Bool'
        return 'StringOrID'
    return 'Unknown'


def _check_var_decl(decl, symbols, errors, struct_name=None):
    """Shared logic for checking a single var_decl tuple, used for both
    top-level declarations and struct properties."""
    _, kindstr, name, type_ann, assign = decl

    declared_type = None
    if type_ann and isinstance(type_ann, tuple) and type_ann[0] == 'type_annotation':
        declared_type = type_ann[1]

    assigned_type = None
    if assign and isinstance(assign, tuple) and assign[0] == 'assignment':
        expr = assign[1]
        if isinstance(expr, tuple) and expr[0] == 'expression':
            tag = expr[1]
            val = expr[2]
            if tag == 'NUMBER':
                assigned_type = 'Int' if isinstance(val, int) else 'Float' if isinstance(val, float) else 'Unknown'
            elif tag == 'STRING':
                assigned_type = 'String'
            elif tag in ('TRUE', 'FALSE'):
                assigned_type = 'Bool'
            elif tag == 'ID':
                if val in symbols:
                    assigned_type = symbols[val]
                else:
                    where = f" in struct '{struct_name}'" if struct_name else ""
                    errors.append(f"Undefined identifier '{val}' used in assignment to '{name}'{where}")
                    assigned_type = 'Unknown'
            else:
                assigned_type = 'Unknown'
        else:
            assigned_type = 'Unknown'

    if declared_type:
        if assigned_type and assigned_type != declared_type:
            where = f" in struct '{struct_name}'" if struct_name else ""
            errors.append(
                f"Type error{where}: cannot assign value of type '{assigned_type}' to '{name}' of type '{declared_type}'"
            )
        symbols[name] = declared_type
    else:
        symbols[name] = assigned_type if assigned_type and assigned_type != 'Unknown' else 'Any'


def check(ast: Tuple) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    symbols: Dict[str, str] = {}

    if not ast or ast[0] != 'program':
        errors.append('Invalid AST: expected top-level program')
        return False, errors

    decls = ast[1]

    for decl in decls:
        if not isinstance(decl, tuple):
            continue
        kind = decl[0]

        if kind == 'var_decl':
            _check_var_decl(decl, symbols, errors)

        elif kind == 'struct_decl':
            _, struct_name, generics, where_clause, properties = decl
            for prop in properties:
                if isinstance(prop, tuple) and prop[0] == 'var_decl':
                    _check_var_decl(prop, symbols, errors, struct_name=struct_name)

    ok = len(errors) == 0
    return ok, errors
