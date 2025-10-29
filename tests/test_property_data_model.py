"""
Unit tests for property data model (PropertyEffects and ComponentProperty).

Tests the new data structures that capture complete property formatting data
including position, rotation, font effects, justification, and hide flags.
"""

import sexpdata
import pytest

from kicad_sch_api.core.types import ComponentProperty, PropertyEffects
from kicad_sch_api.parsers.elements.symbol_parser import SymbolParser


class TestPropertyEffects:
    """Test PropertyEffects dataclass and S-expression conversion."""

    def test_default_effects(self):
        """Test default PropertyEffects values."""
        effects = PropertyEffects()

        assert effects.font_size == (1.27, 1.27)
        assert effects.justification is None
        assert effects.hide is False

    def test_custom_effects(self):
        """Test PropertyEffects with custom values."""
        effects = PropertyEffects(
            font_size=(1.5, 1.5),
            justification="left",
            hide=True
        )

        assert effects.font_size == (1.5, 1.5)
        assert effects.justification == "left"
        assert effects.hide is True

    def test_effects_to_sexp_minimal(self):
        """Test converting minimal effects to S-expression."""
        effects = PropertyEffects()
        sexp = effects.to_sexp()

        # Should have effects symbol and font
        assert str(sexp[0]) == "effects"

        # Find font element
        font_elem = next(e for e in sexp if isinstance(e, list) and str(e[0]) == "font")
        assert font_elem is not None

        # Find size in font
        size_elem = next(e for e in font_elem if isinstance(e, list) and str(e[0]) == "size")
        assert size_elem[1] == 1.27
        assert size_elem[2] == 1.27

    def test_effects_to_sexp_with_justification(self):
        """Test effects with justification."""
        effects = PropertyEffects(justification="left")
        sexp = effects.to_sexp()

        # Find justify element
        justify_elem = next((e for e in sexp if isinstance(e, list) and str(e[0]) == "justify"), None)
        assert justify_elem is not None
        assert str(justify_elem[1]) == "left"

    def test_effects_to_sexp_with_hide(self):
        """Test effects with hide flag."""
        effects = PropertyEffects(hide=True)
        sexp = effects.to_sexp()

        # Find hide element
        hide_elem = next((e for e in sexp if isinstance(e, list) and str(e[0]) == "hide"), None)
        assert hide_elem is not None
        assert str(hide_elem[1]) == "yes"


class TestComponentProperty:
    """Test ComponentProperty dataclass and S-expression conversion."""

    def test_minimal_property(self):
        """Test property with only name and value."""
        prop = ComponentProperty("Reference", "R1")

        assert prop.name == "Reference"
        assert prop.value == "R1"
        assert prop.position is None
        assert prop.rotation == 0.0
        assert prop.effects.font_size == (1.27, 1.27)
        assert prop.effects.hide is False

    def test_complete_property(self):
        """Test property with all attributes."""
        prop = ComponentProperty(
            name="Reference",
            value="R1",
            position=(102.0, 99.0),
            rotation=45.0,
            effects=PropertyEffects(
                font_size=(1.27, 1.27),
                justification="left",
                hide=False
            )
        )

        assert prop.position == (102.0, 99.0)
        assert prop.rotation == 45.0
        assert prop.effects.justification == "left"

    def test_property_to_sexp_minimal(self):
        """Test converting minimal property to S-expression."""
        prop = ComponentProperty("Reference", "R1")
        sexp = prop.to_sexp()

        # Basic structure
        assert str(sexp[0]) == "property"
        assert sexp[1] == "Reference"
        assert sexp[2] == "R1"

        # Should have effects
        effects_elem = next((e for e in sexp if isinstance(e, list) and str(e[0]) == "effects"), None)
        assert effects_elem is not None

    def test_property_to_sexp_with_position(self):
        """Test property with position and rotation."""
        prop = ComponentProperty(
            "Reference",
            "R1",
            position=(102.0, 99.0),
            rotation=45.0
        )
        sexp = prop.to_sexp()

        # Find (at x y rotation)
        at_elem = next((e for e in sexp if isinstance(e, list) and str(e[0]) == "at"), None)
        assert at_elem is not None
        assert at_elem[1] == 102
        assert at_elem[2] == 99
        assert at_elem[3] == 45

    def test_property_to_sexp_preserves_float(self):
        """Test that non-integer values are preserved."""
        prop = ComponentProperty(
            "Reference",
            "R1",
            position=(102.5, 99.3),
            rotation=45.7
        )
        sexp = prop.to_sexp()

        at_elem = next((e for e in sexp if isinstance(e, list) and str(e[0]) == "at"), None)
        assert at_elem[1] == 102.5
        assert at_elem[2] == 99.3
        assert at_elem[3] == 45.7


class TestSymbolParserPropertyParsing:
    """Test SymbolParser's property parsing methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SymbolParser()

    def test_parse_property_minimal(self):
        """Test parsing property with only name and value."""
        prop_sexp = [
            sexpdata.Symbol("property"),
            "Reference",
            "R1"
        ]

        prop = self.parser._parse_property(prop_sexp)

        assert prop is not None
        assert prop.name == "Reference"
        assert prop.value == "R1"
        assert prop.position is None
        assert prop.rotation == 0.0

    def test_parse_property_with_position(self):
        """Test parsing property with position."""
        prop_sexp = [
            sexpdata.Symbol("property"),
            "Reference",
            "R1",
            [sexpdata.Symbol("at"), 102.0, 99.0, 0]
        ]

        prop = self.parser._parse_property(prop_sexp)

        assert prop.position == (102.0, 99.0)
        assert prop.rotation == 0.0

    def test_parse_property_with_rotation(self):
        """Test parsing property with position and rotation."""
        prop_sexp = [
            sexpdata.Symbol("property"),
            "Reference",
            "R1",
            [sexpdata.Symbol("at"), 102.0, 99.0, 45.0]
        ]

        prop = self.parser._parse_property(prop_sexp)

        assert prop.position == (102.0, 99.0)
        assert prop.rotation == 45.0

    def test_parse_property_with_effects(self):
        """Test parsing property with effects."""
        prop_sexp = [
            sexpdata.Symbol("property"),
            "Reference",
            "R1",
            [sexpdata.Symbol("at"), 102.0, 99.0, 45.0],
            [
                sexpdata.Symbol("effects"),
                [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                [sexpdata.Symbol("justify"), sexpdata.Symbol("left")]
            ]
        ]

        prop = self.parser._parse_property(prop_sexp)

        assert prop.effects.font_size == (1.27, 1.27)
        assert prop.effects.justification == "left"
        assert prop.effects.hide is False

    def test_parse_property_with_hide(self):
        """Test parsing property with hide flag."""
        prop_sexp = [
            sexpdata.Symbol("property"),
            "Footprint",
            "Resistor_SMD:R_0603_1608Metric",
            [sexpdata.Symbol("at"), 98.0, 100.0, 90],
            [
                sexpdata.Symbol("effects"),
                [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")]
            ]
        ]

        prop = self.parser._parse_property(prop_sexp)

        assert prop.effects.hide is True

    def test_parse_property_effects(self):
        """Test parsing effects sub-element."""
        effects_sexp = [
            sexpdata.Symbol("effects"),
            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.5, 1.5]],
            [sexpdata.Symbol("justify"), sexpdata.Symbol("right")],
            [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")]
        ]

        effects = self.parser._parse_property_effects(effects_sexp)

        assert effects.font_size == (1.5, 1.5)
        assert effects.justification == "right"
        assert effects.hide is True

    def test_parse_property_invalid(self):
        """Test parsing invalid property returns None."""
        # Too few elements
        prop_sexp = [sexpdata.Symbol("property"), "Reference"]

        prop = self.parser._parse_property(prop_sexp)

        assert prop is None


class TestPropertyRoundTrip:
    """Test that properties survive parse → to_sexp round trip."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SymbolParser()

    def test_roundtrip_simple_property(self):
        """Test round-trip for simple property."""
        original_sexp = [
            sexpdata.Symbol("property"),
            "Reference",
            "R1",
            [sexpdata.Symbol("at"), 102.0, 99.0, 45.0],
            [
                sexpdata.Symbol("effects"),
                [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                [sexpdata.Symbol("justify"), sexpdata.Symbol("left")]
            ]
        ]

        # Parse
        prop = self.parser._parse_property(original_sexp)

        # Convert back
        result_sexp = prop.to_sexp()

        # Verify key attributes preserved
        assert str(result_sexp[0]) == "property"
        assert result_sexp[1] == "Reference"
        assert result_sexp[2] == "R1"

        # Check position
        at_elem = next(e for e in result_sexp if isinstance(e, list) and str(e[0]) == "at")
        assert at_elem[1] == 102
        assert at_elem[2] == 99
        assert at_elem[3] == 45

        # Check effects
        effects_elem = next(e for e in result_sexp if isinstance(e, list) and str(e[0]) == "effects")
        justify_elem = next(e for e in effects_elem if isinstance(e, list) and str(e[0]) == "justify")
        assert str(justify_elem[1]) == "left"

    def test_roundtrip_hidden_property(self):
        """Test round-trip for hidden property."""
        original_sexp = [
            sexpdata.Symbol("property"),
            "Footprint",
            "Resistor_SMD:R_0603_1608Metric",
            [sexpdata.Symbol("at"), 98.0, 100.0, 90],
            [
                sexpdata.Symbol("effects"),
                [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")]
            ]
        ]

        # Parse
        prop = self.parser._parse_property(original_sexp)

        # Verify hide flag
        assert prop.effects.hide is True

        # Convert back
        result_sexp = prop.to_sexp()

        # Verify hide preserved
        effects_elem = next(e for e in result_sexp if isinstance(e, list) and str(e[0]) == "effects")
        hide_elem = next((e for e in effects_elem if isinstance(e, list) and str(e[0]) == "hide"), None)
        assert hide_elem is not None
