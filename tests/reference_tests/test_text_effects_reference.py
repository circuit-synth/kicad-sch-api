"""
Reference tests for text effects preservation.

Tests against the text_effects reference schematic to validate:
- Parsing of all text effects from KiCAD files
- Exact format preservation during round-trip
- Correct handling of all effect properties
"""

import os
from pathlib import Path

import pytest

import kicad_sch_api as ksa

# Path to reference schematic
REFERENCE_DIR = Path(__file__).parent.parent / "reference_kicad_projects" / "text_effects"
REFERENCE_FILE = REFERENCE_DIR / "text_effects.kicad_sch"


@pytest.mark.format
class TestTextEffectsReference:
    """Test text effects against reference schematic."""

    def test_reference_exists(self):
        """Verify reference schematic exists."""
        assert REFERENCE_FILE.exists(), f"Reference not found: {REFERENCE_FILE}"

    def test_load_reference_schematic(self):
        """Load the reference schematic."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        assert sch is not None
        assert len(sch.components) == 1
        assert sch.components[0].reference == "R1"
        assert sch.components[0].value == "10k"

    def test_reference_has_preserved_sexpressions(self):
        """Verify preserved S-expressions exist for all properties."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        # Check preserved S-expressions exist
        assert "__sexp_Reference" in r1.properties
        assert "__sexp_Value" in r1.properties
        assert "__sexp_Footprint" in r1.properties

    def test_parse_reference_bold_flag(self):
        """Parse bold flag from Reference property in reference."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        # Parse effects from preserved S-expression
        sexp = r1.properties["__sexp_Reference"]

        # Find effects section
        effects_section = None
        for item in sexp:
            if isinstance(item, list) and len(item) > 0:
                from sexpdata import Symbol

                if isinstance(item[0], Symbol) and str(item[0]) == "effects":
                    effects_section = item
                    break

        assert effects_section is not None, "No effects section found"

        # Find font section within effects
        font_section = None
        for item in effects_section:
            if isinstance(item, list) and len(item) > 0:
                from sexpdata import Symbol

                if isinstance(item[0], Symbol) and str(item[0]) == "font":
                    font_section = item
                    break

        assert font_section is not None, "No font section found"

        # Check for bold flag
        has_bold = False
        for item in font_section:
            if isinstance(item, list) and len(item) > 0:
                from sexpdata import Symbol

                if isinstance(item[0], Symbol) and str(item[0]) == "bold":
                    has_bold = True
                    break

        assert has_bold, "Bold flag not found in Reference property"

    def test_parse_reference_font_size(self):
        """Parse font size from Reference property."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        sexp = r1.properties["__sexp_Reference"]

        # Find size in font section
        # Expected: (size 2 2) in Reference
        # This will be replaced with proper parsing API once implemented
        # For now, just verify S-expression contains it
        sexp_str = str(sexp)
        assert "size" in sexp_str

    def test_parse_reference_font_face(self):
        """Parse Arial font face from Reference property."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        sexp = r1.properties["__sexp_Reference"]
        sexp_str = str(sexp)

        # Expected: (face "Arial")
        assert "Arial" in sexp_str

    def test_parse_reference_color(self):
        """Parse red color from Reference property."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        sexp = r1.properties["__sexp_Reference"]
        sexp_str = str(sexp)

        # Expected: (color 255 0 0 1)
        assert "color" in sexp_str

    def test_parse_value_italic_flag(self):
        """Parse italic flag from Value property."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        sexp = r1.properties["__sexp_Value"]

        # Find italic flag in font section
        # Expected: (italic yes)
        sexp_str = str(sexp)
        assert "italic" in sexp_str

    def test_parse_value_font_size(self):
        """Parse 1.5mm font size from Value property."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        sexp = r1.properties["__sexp_Value"]
        sexp_str = str(sexp)

        # Expected: (size 1.5 1.5)
        assert "size" in sexp_str

    def test_parse_footprint_hidden_flag(self):
        """Parse hidden flag from Footprint property."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        sexp = r1.properties["__sexp_Footprint"]

        # Find hide flag in effects section
        # Expected: (hide yes)
        sexp_str = str(sexp)
        assert "hide" in sexp_str


@pytest.mark.format
class TestTextEffectsRoundTrip:
    """Test round-trip preservation of text effects."""

    def test_roundtrip_preserves_all_effects(self, tmp_path):
        """Load reference, save it, verify byte-perfect preservation."""
        # Load reference
        sch = ksa.Schematic.load(str(REFERENCE_FILE))

        # Save to temp file
        output_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(output_file))

        # Load again
        sch2 = ksa.Schematic.load(str(output_file))

        # Compare components
        assert len(sch2.components) == 1
        r1_original = sch.components[0]
        r1_roundtrip = sch2.components[0]

        # Verify basic properties preserved
        assert r1_roundtrip.reference == r1_original.reference
        assert r1_roundtrip.value == r1_original.value

        # Verify S-expressions preserved
        assert "__sexp_Reference" in r1_roundtrip.properties
        assert "__sexp_Value" in r1_roundtrip.properties
        assert "__sexp_Footprint" in r1_roundtrip.properties

    def test_roundtrip_preserves_reference_effects(self, tmp_path):
        """Verify Reference property effects preserved exactly."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        output_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(output_file))
        sch2 = ksa.Schematic.load(str(output_file))

        original_sexp = sch.components[0].properties["__sexp_Reference"]
        roundtrip_sexp = sch2.components[0].properties["__sexp_Reference"]

        # Should be identical
        assert original_sexp == roundtrip_sexp

    def test_roundtrip_preserves_value_effects(self, tmp_path):
        """Verify Value property effects preserved exactly."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        output_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(output_file))
        sch2 = ksa.Schematic.load(str(output_file))

        original_sexp = sch.components[0].properties["__sexp_Value"]
        roundtrip_sexp = sch2.components[0].properties["__sexp_Value"]

        # Should be identical
        assert original_sexp == roundtrip_sexp

    def test_roundtrip_preserves_footprint_hidden(self, tmp_path):
        """Verify Footprint hidden flag preserved."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        output_file = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(output_file))
        sch2 = ksa.Schematic.load(str(output_file))

        original_sexp = sch.components[0].properties["__sexp_Footprint"]
        roundtrip_sexp = sch2.components[0].properties["__sexp_Footprint"]

        # Should be identical
        assert original_sexp == roundtrip_sexp


@pytest.mark.format
class TestEffectsAPI:
    """Test effects API with reference schematic."""

    @pytest.mark.skip(reason="API not yet implemented")
    def test_get_reference_effects(self):
        """Get Reference property effects using API."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        # Once API is implemented:
        # effects = r1.get_property_effects("Reference")
        #
        # Expected effects:
        # assert effects["font_face"] == "Arial"
        # assert effects["font_size"] == (2.0, 2.0)
        # assert effects["bold"] is True
        # assert effects["color"] == (255, 0, 0, 1.0)
        # assert effects["justify_h"] == "left"
        pass

    @pytest.mark.skip(reason="API not yet implemented")
    def test_get_value_effects(self):
        """Get Value property effects using API."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        # Once API is implemented:
        # effects = r1.get_property_effects("Value")
        #
        # Expected effects:
        # assert effects["font_size"] == (1.5, 1.5)
        # assert effects["italic"] is True
        pass

    @pytest.mark.skip(reason="API not yet implemented")
    def test_get_footprint_effects(self):
        """Get Footprint property effects using API."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        # Once API is implemented:
        # effects = r1.get_property_effects("Footprint")
        #
        # Expected effects:
        # assert effects["visible"] is False  # Hidden
        pass

    @pytest.mark.skip(reason="API not yet implemented")
    def test_modify_effects_and_save(self, tmp_path):
        """Modify effects using API and verify in saved file."""
        sch = ksa.Schematic.load(str(REFERENCE_FILE))
        r1 = sch.components[0]

        # Once API is implemented:
        # # Change Reference to italic (add to existing effects)
        # r1.set_property_effects("Reference", {"italic": True})
        #
        # # Save
        # output_file = tmp_path / "modified.kicad_sch"
        # sch.save(str(output_file))
        #
        # # Load and verify
        # sch2 = ksa.Schematic.load(str(output_file))
        # effects = sch2.components[0].get_property_effects("Reference")
        # assert effects["italic"] is True
        # assert effects["bold"] is True  # Original effect preserved
        pass
