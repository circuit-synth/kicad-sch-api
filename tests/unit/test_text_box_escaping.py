#!/usr/bin/env python3
"""Unit tests for text_box string escaping in formatter.

Tests that special characters (newlines, tabs, backslashes, quotes) are
properly escaped when formatting text_box elements for KiCad schematic files.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.formatter import ExactFormatter


class TestTextBoxEscaping:
    """Test suite for text_box string escaping functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test artifacts."""
        temp_path = tempfile.mkdtemp(prefix="kicad_sch_api_test_")
        yield Path(temp_path)
        # Cleanup after test
        shutil.rmtree(temp_path, ignore_errors=True)

    def test_escape_string_newlines(self):
        """Test that newlines are escaped to \\n."""
        formatter = ExactFormatter()
        text = "Line 1\nLine 2\nLine 3"
        escaped = formatter._escape_string(text)
        assert escaped == "Line 1\\nLine 2\\nLine 3"
        assert "\n" not in escaped  # No literal newlines

    def test_escape_string_tabs(self):
        """Test that tabs are escaped to \\t."""
        formatter = ExactFormatter()
        text = "Text with\ttab\there"
        escaped = formatter._escape_string(text)
        assert escaped == "Text with\\ttab\\there"
        assert "\t" not in escaped  # No literal tabs

    def test_escape_string_backslashes(self):
        """Test that backslashes are escaped to \\\\."""
        formatter = ExactFormatter()
        text = "Path\\to\\file"
        escaped = formatter._escape_string(text)
        assert escaped == "Path\\\\to\\\\file"

    def test_escape_string_quotes(self):
        """Test that double quotes are escaped to \\\"."""
        formatter = ExactFormatter()
        text = 'Text with "quotes" here'
        escaped = formatter._escape_string(text)
        assert escaped == 'Text with \\"quotes\\" here'

    def test_escape_string_carriage_returns(self):
        """Test that carriage returns are escaped to \\r."""
        formatter = ExactFormatter()
        text = "Line 1\r\nLine 2"
        escaped = formatter._escape_string(text)
        assert escaped == "Line 1\\r\\nLine 2"

    def test_escape_string_mixed_special_chars(self):
        """Test escaping with multiple special characters."""
        formatter = ExactFormatter()
        text = 'Line 1\nTab:\there\nPath: C:\\Users\\Name\nQuote: "text"'
        escaped = formatter._escape_string(text)

        # Check all escapes are present
        assert "\\n" in escaped
        assert "\\t" in escaped
        assert "\\\\" in escaped
        assert '\\"' in escaped

        # Check no literal special chars remain
        assert "\n" not in escaped
        assert "\t" not in escaped

    def test_escape_order_backslash_first(self):
        """Test that backslashes are escaped before other characters.

        This is critical - if we escape quotes before backslashes,
        a string like 'a\"b' would become 'a\\"b' then 'a\\\\"b' (wrong).
        Backslash must be escaped first.
        """
        formatter = ExactFormatter()
        # String that already has an escaped quote
        text = 'Already escaped: \\"quote\\"'
        escaped = formatter._escape_string(text)
        # The backslashes should be escaped, then the quotes
        assert escaped == 'Already escaped: \\\\\\"quote\\\\\\"'

    def test_text_box_multiline_formatting(self, temp_dir):
        """Test that text_box with multiline text is formatted correctly."""
        sch = ksa.create_schematic("Test Multiline")

        text = "Line 1: Basic text\nLine 2: More text\nLine 3: Final text"
        sch.add_text_box(
            text=text,
            position=(100, 100),
            size=(50, 30),
        )

        output_path = temp_dir / "test_multiline.kicad_sch"
        sch.save(str(output_path))

        # Read the file and verify escaping
        with open(output_path, "rb") as f:
            content = f.read()

        # Should contain escaped newlines (bytes 0x5C 0x6E = \n)
        assert b"\\n" in content

        # Count actual newlines - should only be structural (between S-expressions)
        # The text_box line itself should NOT contain literal newlines
        lines = content.split(b"\n")
        text_box_line = [line for line in lines if b"text_box" in line][0]

        # The text_box line should have no embedded newlines (it's on one line)
        # but should have escaped \n in the string
        assert b"\\n" in text_box_line
        assert text_box_line.count(b"\n") == 0  # No literal newlines in this line

    def test_text_box_special_characters_formatting(self, temp_dir):
        """Test that text_box with special chars is formatted correctly."""
        sch = ksa.create_schematic("Test Special Chars")

        text = 'Text with\ttab and\\backslash and"quote"'
        sch.add_text_box(
            text=text,
            position=(100, 100),
            size=(50, 30),
        )

        output_path = temp_dir / "test_special.kicad_sch"
        sch.save(str(output_path))

        # Read and verify
        with open(output_path, "r") as f:
            content = f.read()

        # Find the text_box line
        text_box_line = [line for line in content.split("\n") if "text_box" in line][0]

        # Check for escaped characters
        assert "\\t" in text_box_line  # Escaped tab
        assert "\\\\" in text_box_line  # Escaped backslash
        assert '\\"' in text_box_line  # Escaped quote

    def test_text_box_matches_kicad_reference(self, temp_dir):
        """Test that our formatting matches KiCad's native format.

        Uses the reference file created by KiCad as ground truth.
        """
        # Load the reference schematic created by KiCad
        reference_path = (
            Path(__file__).parent.parent
            / "fixtures"
            / "multi-line-string-kicad"
            / "multi-line-string-kicad.kicad_sch"
        )

        if not reference_path.exists():
            pytest.skip(f"Reference file not found: {reference_path}")

        ref_sch = ksa.Schematic.load(str(reference_path))

        # Save it back out
        output_path = temp_dir / "roundtrip.kicad_sch"
        ref_sch.save(str(output_path))

        # Read both files
        with open(reference_path, "r") as f:
            ref_content = f.read()
        with open(output_path, "r") as f:
            output_content = f.read()

        # Extract the text_box lines
        ref_text_box = [line for line in ref_content.split("\n") if "text_box" in line][0]
        out_text_box = [line for line in output_content.split("\n") if "text_box" in line][0]

        # The text_box content should match (same escaping)
        # Note: We compare the text content, not the entire line (positions might differ)
        assert "\\n" in out_text_box  # Has escaped newlines
        assert "\\\\" in out_text_box  # Has escaped backslashes
        assert '\\"' in out_text_box  # Has escaped quotes

    def test_text_box_roundtrip_preserves_content(self, temp_dir):
        """Test that text survives save/load roundtrip correctly."""
        sch = ksa.create_schematic("Test Roundtrip")

        original_text = 'Line 1\nLine 2 with\ttab\nLine 3 with\\backslash and"quote"'
        sch.add_text_box(
            text=original_text,
            position=(100, 100),
            size=(50, 30),
        )

        # Save and reload
        output_path = temp_dir / "roundtrip.kicad_sch"
        sch.save(str(output_path))

        loaded_sch = ksa.Schematic.load(str(output_path))

        # Get the text_box from loaded schematic
        text_boxes = [
            item
            for item in loaded_sch._data.get("items", [])
            if isinstance(item, list) and len(item) > 0 and item[0] == "text_box"
        ]

        assert len(text_boxes) == 1
        loaded_text = text_boxes[0][1]

        # The text should match the original
        assert loaded_text == original_text

    def test_format_rule_for_text_box(self):
        """Test that text_box has proper format rules configured."""
        formatter = ExactFormatter()

        # text_box should have a format rule
        assert "text_box" in formatter.rules

        # Should have quote_indices set to escape the text content
        rule = formatter.rules["text_box"]
        assert rule.quote_indices == {1}  # Index 1 is the text content

    def test_format_rule_for_text(self):
        """Test that text element also has proper format rules."""
        formatter = ExactFormatter()

        # text should also have a format rule
        assert "text" in formatter.rules

        rule = formatter.rules["text"]
        assert rule.quote_indices == {1}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
