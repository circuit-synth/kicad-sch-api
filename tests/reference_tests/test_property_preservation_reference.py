"""
Reference tests for property preservation.

Tests that validate exact format preservation against the manually-created
reference schematic with custom properties and mixed visibility states.
"""

import pytest

import kicad_sch_api as ksa


@pytest.mark.format
class TestPropertyPreservationReference:
    """Test loading and preserving the property preservation reference schematic."""

    def test_load_reference_schematic(self):
        """Reference schematic should load without errors."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )

        assert sch is not None
        assert len(sch.components) == 1
        assert sch.components.get("R1") is not None

    def test_reference_component_properties(self):
        """All properties from reference should be loaded."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Standard properties
        assert r1.reference == "R1"
        assert r1.value == "10k"
        assert r1.footprint == "Resistor_SMD:R_0603_1608Metric"

        # Properties dict should contain all properties
        assert r1.properties["Datasheet"]["value"] == "~"
        assert r1.properties["Description"]["value"] == ""
        assert r1.properties["MPN"]["value"] == "C0603FR-0710KL"
        assert r1.properties["Manufacturer"]["value"] == "Yageo"
        assert r1.properties["Tolearnce"]["value"] == "1%"  # Typo from reference

    def test_reference_hidden_properties_set(self):
        """Hidden properties should be correctly identified."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # These have (hide yes) in reference
        expected_hidden = {"Footprint", "Datasheet", "MPN"}

        for prop in expected_hidden:
            assert prop in r1.hidden_properties, f"{prop} should be hidden"

    def test_reference_visible_properties_set(self):
        """Visible properties should NOT be in hidden_properties."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # These do NOT have (hide yes) in reference
        expected_visible = {"Reference", "Value", "Description", "Manufacturer", "Tolearnce"}

        for prop in expected_visible:
            # Check both in properties dict and NOT in hidden set
            # Note: Reference and Value are special and stored as attributes
            if prop in ["Reference", "Value"]:
                # These are stored as attributes, not in properties dict
                continue
            else:
                assert prop not in r1.hidden_properties, f"{prop} should be visible"

    def test_reference_roundtrip_byte_perfect(self, tmp_path):
        """Load → save should produce output matching reference (or semantically equivalent)."""
        # Load reference
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )

        # Save to temp
        output_path = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(output_path))

        # Reload and compare
        sch2 = ksa.Schematic.load(str(output_path))
        r1 = sch2.components.get("R1")

        # Properties should match
        assert r1.reference == "R1"
        assert r1.value == "10k"
        assert r1.footprint == "Resistor_SMD:R_0603_1608Metric"
        assert r1.properties["MPN"]["value"] == "C0603FR-0710KL"
        assert r1.properties["Manufacturer"]["value"] == "Yageo"
        assert r1.properties["Tolearnce"]["value"] == "1%"

        # Visibility should match
        assert "MPN" in r1.hidden_properties
        assert "Footprint" in r1.hidden_properties
        assert "Datasheet" in r1.hidden_properties
        assert "Manufacturer" not in r1.hidden_properties

    def test_reference_sexp_preservation(self):
        """S-expression structures should be preserved for all properties."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # All properties should have preserved S-expressions
        expected_sexp_props = [
            "Reference",
            "Value",
            "Footprint",
            "Datasheet",
            "Description",
            "MPN",
            "Manufacturer",
            "Tolearnce",
        ]

        for prop_name in expected_sexp_props:
            sexp_key = f"__sexp_{prop_name}"
            assert sexp_key in r1.properties, f"Missing S-expression for {prop_name}"

    def test_programmatic_recreation_of_reference(self):
        """Programmatically create a component matching the reference."""
        sch = ksa.create_schematic("PropertyPreservationTest")

        # Create component
        r1 = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.33, 100.33),
            footprint="Resistor_SMD:R_0603_1608Metric",
        )

        # Add custom properties with correct visibility
        r1.add_property("Datasheet", "~", hidden=True)
        r1.add_property("Description", "", hidden=False)
        r1.add_property("MPN", "C0603FR-0710KL", hidden=True)
        r1.add_property("Manufacturer", "Yageo", hidden=False)
        r1.add_property("Tolearnce", "1%", hidden=False)

        # Verify structure matches
        assert r1.reference == "R1"
        assert r1.value == "10k"
        assert r1.properties["MPN"]["value"] == "C0603FR-0710KL"

        # Verify visibility matches
        assert "MPN" in r1.hidden_properties
        assert "Datasheet" in r1.hidden_properties
        assert "Manufacturer" not in r1.hidden_properties
        assert "Tolearnce" not in r1.hidden_properties

    def test_reference_property_count(self):
        """Reference should have exactly 8 properties (including Reference, Value, Footprint)."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Count properties with S-expression preservation
        sexp_props = [k for k in r1.properties.keys() if k.startswith("__sexp_")]

        # Should have: Reference, Value, Footprint, Datasheet, Description, MPN, Manufacturer, Tolearnce
        assert len(sexp_props) == 8

    def test_reference_hidden_count(self):
        """Reference should have exactly 3 hidden properties."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Should be: Footprint, Datasheet, MPN
        assert len(r1.hidden_properties) == 3


@pytest.mark.format
class TestPropertyPreservationFileFormat:
    """Test exact file format details."""

    def test_hide_flag_format_in_reference(self):
        """Reference file should use (hide yes) format, not (hide no)."""
        with open("tests/reference_kicad_projects/property_preservation/test.kicad_sch", "r") as f:
            content = f.read()

        # Should contain (hide yes)
        assert "(hide yes)" in content

        # Should NOT contain (hide no) - KiCAD doesn't use this
        assert "(hide no)" not in content

    def test_property_ordering_in_reference(self):
        """Properties should appear in standard order in file."""
        with open("tests/reference_kicad_projects/property_preservation/test.kicad_sch", "r") as f:
            content = f.read()

        # Find property positions
        ref_pos = content.find('property "Reference"')
        val_pos = content.find('property "Value"')
        fp_pos = content.find('property "Footprint"')
        ds_pos = content.find('property "Datasheet"')
        desc_pos = content.find('property "Description"')
        mpn_pos = content.find('property "MPN"')

        # Standard properties should come first
        assert ref_pos < val_pos < fp_pos < ds_pos < desc_pos < mpn_pos

    def test_effects_section_structure(self):
        """Effects sections should have consistent structure."""
        with open("tests/reference_kicad_projects/property_preservation/test.kicad_sch", "r") as f:
            content = f.read()

        # All properties should have effects section with font
        assert content.count("(effects") >= 8  # One per property
        # Font can be inline or multiline - just check for size
        assert content.count("(size 1.27 1.27)") >= 8

    def test_justification_preserved_in_reference(self):
        """User-set justification should be preserved in reference."""
        with open("tests/reference_kicad_projects/property_preservation/test.kicad_sch", "r") as f:
            content = f.read()

        # Manufacturer has (justify right top) - user set this
        assert "(justify right top)" in content

        # Tolearnce has (justify left bottom) - user set this
        assert "(justify left bottom)" in content
