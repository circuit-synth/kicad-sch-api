"""
Unit tests for parse_bool_property helper function.

This test suite verifies that boolean properties are parsed correctly
from S-expression data, handling both Symbol and string types.

Regression test for bug where Symbol('yes') == 'yes' returned False,
causing in_bom and on_board properties to be parsed incorrectly.
"""

import pytest
import sexpdata

from kicad_sch_api.core.parsing_utils import parse_bool_property


class TestParseBoolProperty:
    """Test parse_bool_property function handles all input types correctly."""

    def test_symbol_yes(self):
        """Test that Symbol('yes') returns True."""
        result = parse_bool_property(sexpdata.Symbol("yes"))
        assert result is True

    def test_symbol_no(self):
        """Test that Symbol('no') returns False."""
        result = parse_bool_property(sexpdata.Symbol("no"))
        assert result is False

    def test_string_yes(self):
        """Test that string 'yes' returns True."""
        result = parse_bool_property("yes")
        assert result is True

    def test_string_no(self):
        """Test that string 'no' returns False."""
        result = parse_bool_property("no")
        assert result is False

    def test_case_insensitive_yes(self):
        """Test that YES, Yes, yes all return True."""
        assert parse_bool_property("YES") is True
        assert parse_bool_property("Yes") is True
        assert parse_bool_property("yes") is True

    def test_case_insensitive_no(self):
        """Test that NO, No, no all return False."""
        assert parse_bool_property("NO") is False
        assert parse_bool_property("No") is False
        assert parse_bool_property("no") is False

    def test_none_with_default_true(self):
        """Test that None with default=True returns True."""
        result = parse_bool_property(None, default=True)
        assert result is True

    def test_none_with_default_false(self):
        """Test that None with default=False returns False."""
        result = parse_bool_property(None, default=False)
        assert result is False

    def test_bool_true_passthrough(self):
        """Test that boolean True is returned as-is."""
        result = parse_bool_property(True)
        assert result is True

    def test_bool_false_passthrough(self):
        """Test that boolean False is returned as-is."""
        result = parse_bool_property(False)
        assert result is False

    def test_unexpected_type_uses_default(self):
        """Test that unexpected types fall back to default."""
        result = parse_bool_property(123, default=False)
        assert result is False

        result = parse_bool_property([1, 2, 3], default=True)
        assert result is True

    def test_empty_string_returns_false(self):
        """Test that empty string returns False (not 'yes')."""
        result = parse_bool_property("")
        assert result is False

    def test_symbol_regression_bug(self):
        """
        Regression test for critical bug.

        Bug: Symbol('yes') == 'yes' returned False, causing
        in_bom and on_board to be parsed incorrectly.

        This test verifies the bug is fixed by ensuring
        parse_bool_property correctly handles Symbol objects.
        """
        # This is what sexpdata returns when parsing (in_bom yes)
        sexp = sexpdata.loads("(in_bom yes)")
        value = sexp[1]  # Symbol('yes')

        # Before fix: Symbol('yes') == 'yes' returned False ❌
        # After fix: parse_bool_property handles Symbol correctly ✅
        result = parse_bool_property(value)
        assert result is True

        # Same for 'no'
        sexp_no = sexpdata.loads("(in_bom no)")
        value_no = sexp_no[1]  # Symbol('no')
        result_no = parse_bool_property(value_no)
        assert result_no is False
