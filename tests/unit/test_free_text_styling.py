"""
Unit tests for free text styling properties.

Tests the Text dataclass, parser, and API for bold, italic, thickness, color, and face properties.
"""

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Text, Point


class TestTextDataclass:
    """Test Text dataclass with font styling fields."""

    def test_text_with_basic_properties(self):
        """Create Text with basic properties only."""
        text = Text(
            uuid="test-uuid-1",
            position=Point(100, 100),
            text="Hello World",
            rotation=0.0,
            size=1.27,
        )
        assert text.uuid == "test-uuid-1"
        assert text.text == "Hello World"
        assert text.position.x == 100
        assert text.position.y == 100
        assert text.size == 1.27
        assert text.rotation == 0.0

    def test_text_with_bold(self):
        """Create Text with bold flag."""
        text = Text(
            uuid="test-uuid-2",
            position=Point(100, 100),
            text="Bold Text",
            bold=True,
        )
        assert text.bold is True

    def test_text_with_italic(self):
        """Create Text with italic flag."""
        text = Text(
            uuid="test-uuid-3",
            position=Point(100, 100),
            text="Italic Text",
            italic=True,
        )
        assert text.italic is True

    def test_text_with_thickness(self):
        """Create Text with thickness."""
        text = Text(
            uuid="test-uuid-4",
            position=Point(100, 100),
            text="Thick Text",
            thickness=0.4,
        )
        assert text.thickness == 0.4

    def test_text_with_color(self):
        """Create Text with RGBA color."""
        text = Text(
            uuid="test-uuid-5",
            position=Point(100, 100),
            text="Red Text",
            color=(255, 0, 0, 1.0),
        )
        assert text.color == (255, 0, 0, 1.0)

    def test_text_with_font_face(self):
        """Create Text with custom font face."""
        text = Text(
            uuid="test-uuid-6",
            position=Point(100, 100),
            text="Arial Text",
            face="Arial",
        )
        assert text.face == "Arial"

    def test_text_with_all_effects(self):
        """Create Text with all font effects combined."""
        text = Text(
            uuid="test-uuid-7",
            position=Point(100, 100),
            text="Styled Text",
            size=2.0,
            rotation=90.0,
            bold=True,
            italic=True,
            thickness=0.5,
            color=(255, 16, 29, 1.0),
            face="Arial",
        )
        assert text.bold is True
        assert text.italic is True
        assert text.thickness == 0.5
        assert text.color == (255, 16, 29, 1.0)
        assert text.face == "Arial"

    def test_text_defaults_for_optional_fields(self):
        """Verify optional fields have correct defaults."""
        text = Text(
            uuid="test-uuid-8",
            position=Point(100, 100),
            text="Plain Text",
        )
        assert text.bold is False
        assert text.italic is False
        assert text.thickness is None
        assert text.color is None
        assert text.face is None


class TestTextAPI:
    """Test Text API (add_text method) with styling parameters."""

    def test_add_text_with_bold(self, tmp_path):
        """Add text with bold flag via API."""
        sch = ksa.create_schematic("test")
        text_uuid = sch.add_text(
            "Bold Text",
            position=(100, 100),
            bold=True,
        )

        # Verify text was added
        assert text_uuid is not None

        # Save and reload
        output_file = tmp_path / "test_bold.kicad_sch"
        sch.save(str(output_file))
        sch2 = ksa.Schematic.load(str(output_file))

        # Find the text element
        text_elem = None
        for text in sch2.texts:
            if text.text == "Bold Text":
                text_elem = text
                break

        assert text_elem is not None
        assert text_elem.bold is True

    def test_add_text_with_color(self, tmp_path):
        """Add text with color via API."""
        sch = ksa.create_schematic("test")
        sch.add_text(
            "Red Text",
            position=(100, 100),
            color=(255, 0, 0, 1.0),
        )

        # Save and reload
        output_file = tmp_path / "test_color.kicad_sch"
        sch.save(str(output_file))
        sch2 = ksa.Schematic.load(str(output_file))

        # Find the text element
        text_elem = None
        for text in sch2.texts:
            if text.text == "Red Text":
                text_elem = text
                break

        assert text_elem is not None
        assert text_elem.color == (255, 0, 0, 1.0)

    def test_add_text_with_all_effects(self, tmp_path):
        """Add text with all effects via API."""
        sch = ksa.create_schematic("test")
        sch.add_text(
            "Styled Text",
            position=(100, 100),
            size=2.0,
            bold=True,
            italic=True,
            thickness=0.5,
            color=(255, 16, 29, 1.0),
            face="Arial",
        )

        # Save and reload
        output_file = tmp_path / "test_all_effects.kicad_sch"
        sch.save(str(output_file))
        sch2 = ksa.Schematic.load(str(output_file))

        # Find the text element
        text_elem = None
        for text in sch2.texts:
            if text.text == "Styled Text":
                text_elem = text
                break

        assert text_elem is not None
        assert text_elem.bold is True
        assert text_elem.italic is True
        assert text_elem.thickness == 0.5
        assert text_elem.color == (255, 16, 29, 1.0)
        assert text_elem.face == "Arial"


class TestTextValidation:
    """Test validation of text styling parameters."""

    def test_reject_invalid_color_length(self):
        """Reject color tuple with wrong length."""
        sch = ksa.create_schematic("test")
        with pytest.raises(Exception):  # Will be ValidationError
            sch.add_text(
                "Invalid Color",
                position=(100, 100),
                color=(255, 0, 0),  # Missing alpha
            )

    def test_reject_out_of_range_rgb(self):
        """Reject RGB values outside 0-255 range."""
        sch = ksa.create_schematic("test")
        with pytest.raises(Exception):  # Will be ValidationError
            sch.add_text(
                "Invalid Color",
                position=(100, 100),
                color=(256, 0, 0, 1.0),  # R > 255
            )

    def test_reject_out_of_range_alpha(self):
        """Reject alpha values outside 0-1 range."""
        sch = ksa.create_schematic("test")
        with pytest.raises(Exception):  # Will be ValidationError
            sch.add_text(
                "Invalid Color",
                position=(100, 100),
                color=(255, 0, 0, 1.5),  # A > 1.0
            )

    def test_reject_negative_thickness(self):
        """Reject negative thickness values."""
        sch = ksa.create_schematic("test")
        with pytest.raises(Exception):  # Will be ValidationError
            sch.add_text(
                "Invalid Thickness",
                position=(100, 100),
                thickness=-0.1,
            )

    def test_reject_zero_thickness(self):
        """Reject zero thickness values."""
        sch = ksa.create_schematic("test")
        with pytest.raises(Exception):  # Will be ValidationError
            sch.add_text(
                "Invalid Thickness",
                position=(100, 100),
                thickness=0.0,
            )
