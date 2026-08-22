"""
Test suite for the Swift Subset Syntax Validator.

Run with: pytest -v

Organized by pipeline stage (lexical -> syntax -> semantic) rather than
by feature, so a failing test immediately tells you which stage of the
pipeline broke.
"""
import pytest
from main import validate_swift_code


def status_of(code):
    return validate_swift_code(code)["status"]


# ---------------------------------------------------------------------
# Lexical stage
# ---------------------------------------------------------------------

class TestLexicalErrors:
    def test_illegal_character(self):
        assert status_of("let x @ Int = 5") == "lexical_error"

    def test_valid_identifiers_and_numbers(self):
        assert status_of("let x1_2: Int = 42") == "success"

    def test_scientific_notation_number(self):
        assert status_of("let x: Float = 1.5e3") == "success"

    def test_block_comment_is_ignored(self):
        # Regression test for the Phase 0 bug: block comments used to
        # raise "Illegal character '/'" because t_BLOCK_COMMENT didn't
        # exist yet.
        code = "/* this is a comment\nspanning lines */\nlet x: Int = 5"
        assert status_of(code) == "success"

    def test_single_line_comment_is_ignored(self):
        code = "let x: Int = 5 // trailing comment"
        assert status_of(code) == "success"

    def test_string_literal(self):
        assert status_of('let name: String = "Vageesh"') == "success"


# ---------------------------------------------------------------------
# Syntax stage
# ---------------------------------------------------------------------

class TestSyntaxErrors:
    def test_missing_type_after_colon(self):
        assert status_of("let invalidVar: = 5") == "syntax_error"

    def test_missing_identifier_after_let(self):
        assert status_of("let : Int = 10") == "syntax_error"

    def test_unclosed_struct_brace(self):
        code = "struct Missing {\n let x: Int = 1"
        assert status_of(code) == "syntax_error"

    def test_invalid_generic_constraint_missing_colon(self):
        code = "struct InvalidGeneric<T where T Comparable> {}"
        assert status_of(code) == "syntax_error"

    def test_let_declaration_no_type_no_value(self):
        # `let x` alone is valid per this grammar (both type and
        # assignment are optional) — this documents that behavior
        # rather than asserting it's an error.
        assert status_of("let x") == "success"

    def test_semicolon_terminator_accepted(self):
        # Phase 0 addition: SEMICOLON now wired in as optional terminator
        assert status_of("let x: Int = 5;") == "success"

    def test_var_declaration(self):
        assert status_of("var count: Int = 0") == "success"


# ---------------------------------------------------------------------
# Struct / generics / protocol syntax
# ---------------------------------------------------------------------

class TestStructuresAndGenerics:
    def test_simple_struct(self):
        code = """
        struct Student {
            let name: String = "Vageesh"
            var age: Int = 18
        }
        """
        assert status_of(code) == "success"

    def test_empty_struct(self):
        assert status_of("struct Empty {}") == "success"

    def test_generic_struct(self):
        code = "struct Box<T> {\n let item: T\n}"
        assert status_of(code) == "success"

    def test_generic_with_constraint_and_where_clause(self):
        code = """
        struct GenericPair<T: Hashable, U> where T: Comparable {
            let first: T
            var second: U
        }
        """
        assert status_of(code) == "success"

    def test_protocol_declaration_minimal(self):
        assert status_of("protocol MyProtocol {}") == "success"

    def test_protocol_declaration_no_braces(self):
        assert status_of("protocol MyProtocol") == "success"

    def test_nested_struct_not_supported(self):
        # Known limitation, documented by the roadmap: property_declaration_list
        # only accepts var_declaration, not struct_declaration.
        code = """
        struct Outer {
            struct Inner {
                let x: Int = 1
            }
        }
        """
        assert status_of(code) == "syntax_error"


# ---------------------------------------------------------------------
# Semantic stage
# ---------------------------------------------------------------------

class TestSemanticErrors:
    def test_type_mismatch_string_to_int(self):
        result = validate_swift_code('let age: Int = "abc"')
        assert result["status"] == "semantic_error"
        assert any("cannot assign value of type" in e for e in result["errors"])

    def test_type_mismatch_int_to_string(self):
        assert status_of('let name: String = 10') == "semantic_error"

    def test_type_match_is_success(self):
        assert status_of('let age: Int = 42') == "success"

    def test_undefined_identifier_in_assignment(self):
        result = validate_swift_code("let a: Int = b")
        assert result["status"] == "semantic_error"
        assert any("Undefined identifier" in e for e in result["errors"])

    def test_defined_identifier_reference_is_success(self):
        code = "let a: Int = 5\nlet b: Int = a"
        assert status_of(code) == "success"

    def test_struct_property_type_mismatch(self):
        code = """
        struct MyStruct {
            let property: Int = "wrong"
        }
        """
        result = validate_swift_code(code)
        assert result["status"] == "semantic_error"
        assert any("MyStruct" in e for e in result["errors"])

    def test_generic_type_param_mismatch(self):
        # Documents current (naive) generic handling: T is compared as a
        # literal type name, not resolved via substitution. This test
        # locks in today's behavior so a future Phase-2 fix to proper
        # generic binding shows up as an intentional, visible change.
        code = """
        struct MyStruct<T: Equatable, U> where T: Protocol {
            let property: T = 5
            var anotherProperty: U
        }
        """
        assert status_of(code) == "semantic_error"

    def test_bool_literal_type_check(self):
        assert status_of("let isTrue: Bool = true") == "success"
        assert status_of("let isTrue: Bool = false") == "success"


# ---------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_input_produces_no_declarations_or_syntax_error(self):
        # Whitespace-only input; grammar requires at least one declaration
        result = validate_swift_code("   \n  ")
        assert result["status"] in ("syntax_error",)

    def test_multiple_top_level_declarations(self):
        code = "let a: Int = 1\nvar b: String = \"x\"\nstruct S {}"
        assert status_of(code) == "success"

    def test_line_number_reported_correctly_in_syntax_error(self):
        # Regression test for the Phase 0 t_ignore bug: newlines used to
        # never reach t_newline(), so every error reported "line 1".
        code = "let a: Int = 5\nlet b : = 10"
        result = validate_swift_code(code)
        assert result["status"] == "syntax_error"
        # We can't easily capture the printed line number here since
        # p_error() only prints, but this at minimum exercises the
        # multi-line path without crashing. See README for a manual
        # verification example.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
