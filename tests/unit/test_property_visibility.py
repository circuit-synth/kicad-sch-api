"""
Unit tests for component property visibility tracking.

Tests the hidden_properties field and helper methods for managing
property visibility state during load, save, and programmatic modification.
"""

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point, SchematicSymbol


class TestPropertyVisibilityLoading:
    """Test that property visibility state is extracted during load."""

    def test_load_extracts_hidden_properties(self):
        """Hidden properties should be identified and added to hidden_properties set."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Properties with (hide yes) should be in hidden_properties set
        assert "Footprint" in r1.hidden_properties
        assert "Datasheet" in r1.hidden_properties
        assert "MPN" in r1.hidden_properties

    def test_load_identifies_visible_properties(self):
        """Visible properties should NOT be in hidden_properties set."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Properties without hide flag should NOT be in set
        assert "Reference" not in r1.hidden_properties
        assert "Value" not in r1.hidden_properties
        assert "Manufacturer" not in r1.hidden_properties
        assert "Tolearnce" not in r1.hidden_properties  # Typo preserved from reference

    def test_all_properties_loaded(self):
        """All properties should be loaded regardless of visibility."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Check all properties are in dict
        assert r1.properties["Datasheet"] == "~"
        assert r1.properties["MPN"] == "C0603FR-0710KL"
        assert r1.properties["Manufacturer"] == "Yageo"
        assert r1.properties["Tolearnce"] == "1%"
        assert r1.properties["Description"] == ""  # Empty value

    def test_hidden_properties_field_exists(self):
        """SchematicSymbol should have hidden_properties field."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Field should exist and be a set
        assert hasattr(r1, "hidden_properties")
        assert isinstance(r1.hidden_properties, set)


class TestPropertyVisibilityRoundTrip:
    """Test that visibility state survives round-trip load → save → load."""

    def test_hidden_properties_preserved_on_save(self, tmp_path):
        """Hidden properties should have (hide yes) flag after save."""
        # Load reference
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )

        # Save to temp file
        output_path = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(output_path))

        # Reload
        sch2 = ksa.Schematic.load(str(output_path))
        r1 = sch2.components.get("R1")

        # Hidden properties should still be hidden
        assert "Footprint" in r1.hidden_properties
        assert "Datasheet" in r1.hidden_properties
        assert "MPN" in r1.hidden_properties

    def test_visible_properties_preserved_on_save(self, tmp_path):
        """Visible properties should NOT have hide flag after save."""
        # Load reference
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )

        # Save to temp file
        output_path = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(output_path))

        # Reload
        sch2 = ksa.Schematic.load(str(output_path))
        r1 = sch2.components.get("R1")

        # Visible properties should still be visible
        assert "Reference" not in r1.hidden_properties
        assert "Value" not in r1.hidden_properties
        assert "Manufacturer" not in r1.hidden_properties

    def test_property_values_unchanged_after_roundtrip(self, tmp_path):
        """Property values should not change during round-trip."""
        # Load reference
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )

        # Save and reload
        output_path = tmp_path / "roundtrip.kicad_sch"
        sch.save(str(output_path))
        sch2 = ksa.Schematic.load(str(output_path))
        r1 = sch2.components.get("R1")

        # Values should be identical
        assert r1.properties["MPN"] == "C0603FR-0710KL"
        assert r1.properties["Manufacturer"] == "Yageo"
        assert r1.properties["Tolearnce"] == "1%"
        assert r1.properties["Datasheet"] == "~"


class TestAddPropertyMethod:
    """Test the add_property() helper method."""

    def test_add_property_hidden(self):
        """Adding property with hidden=True should add to hidden_properties."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        # Add hidden property
        r1.add_property("Supplier", "Digikey", hidden=True)

        assert r1.properties["Supplier"] == "Digikey"
        assert "Supplier" in r1.hidden_properties

    def test_add_property_visible(self):
        """Adding property with hidden=False should NOT add to hidden_properties."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        # Add visible property
        r1.add_property("Notes", "Important resistor", hidden=False)

        assert r1.properties["Notes"] == "Important resistor"
        assert "Notes" not in r1.hidden_properties

    def test_add_property_default_visible(self):
        """Default hidden parameter should be False (visible)."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        # Add property without specifying hidden
        r1.add_property("TestProp", "TestValue")

        assert r1.properties["TestProp"] == "TestValue"
        assert "TestProp" not in r1.hidden_properties

    def test_add_property_update_existing(self):
        """Adding property that exists should update value and visibility."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        # Add initially hidden
        r1.add_property("MPN", "OLD_VALUE", hidden=True)
        assert "MPN" in r1.hidden_properties

        # Update to visible with new value
        r1.add_property("MPN", "NEW_VALUE", hidden=False)

        assert r1.properties["MPN"] == "NEW_VALUE"
        assert "MPN" not in r1.hidden_properties


class TestAddPropertiesMethod:
    """Test the add_properties() bulk helper method."""

    def test_add_properties_hidden(self):
        """Adding multiple properties with hidden=True."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        props = {
            "MPN": "RC0603FR-0710KL",
            "Manufacturer": "Yageo",
            "Supplier": "Digikey",
        }
        r1.add_properties(props, hidden=True)

        # All properties should be added and hidden
        assert r1.properties["MPN"] == "RC0603FR-0710KL"
        assert r1.properties["Manufacturer"] == "Yageo"
        assert r1.properties["Supplier"] == "Digikey"

        assert "MPN" in r1.hidden_properties
        assert "Manufacturer" in r1.hidden_properties
        assert "Supplier" in r1.hidden_properties

    def test_add_properties_visible(self):
        """Adding multiple properties with hidden=False."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        props = {
            "Notes": "High precision",
            "Category": "Passive",
        }
        r1.add_properties(props, hidden=False)

        # All properties should be added and visible
        assert r1.properties["Notes"] == "High precision"
        assert r1.properties["Category"] == "Passive"

        assert "Notes" not in r1.hidden_properties
        assert "Category" not in r1.hidden_properties

    def test_add_properties_default_visible(self):
        """Default hidden parameter should be False (visible)."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        props = {"Prop1": "Value1", "Prop2": "Value2"}
        r1.add_properties(props)

        assert "Prop1" not in r1.hidden_properties
        assert "Prop2" not in r1.hidden_properties


class TestVisibilityToggling:
    """Test changing visibility of existing properties."""

    def test_hide_existing_property(self):
        """Adding property to hidden_properties should hide it."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Manufacturer is initially visible
        assert "Manufacturer" not in r1.hidden_properties

        # Hide it
        r1.hidden_properties.add("Manufacturer")

        assert "Manufacturer" in r1.hidden_properties

    def test_show_existing_property(self):
        """Removing property from hidden_properties should show it."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # MPN is initially hidden
        assert "MPN" in r1.hidden_properties

        # Show it
        r1.hidden_properties.discard("MPN")

        assert "MPN" not in r1.hidden_properties

    def test_visibility_change_survives_save(self, tmp_path):
        """Visibility changes should persist after save."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Hide Manufacturer (was visible)
        r1.hidden_properties.add("Manufacturer")

        # Show MPN (was hidden)
        r1.hidden_properties.discard("MPN")

        # Save and reload
        output_path = tmp_path / "toggled.kicad_sch"
        sch.save(str(output_path))
        sch2 = ksa.Schematic.load(str(output_path))
        r1_reloaded = sch2.components.get("R1")

        # Changes should persist
        assert "Manufacturer" in r1_reloaded.hidden_properties
        assert "MPN" not in r1_reloaded.hidden_properties


class TestEdgeCases:
    """Test edge cases for property visibility."""

    def test_empty_property_value(self):
        """Properties with empty values should be handled correctly."""
        sch = ksa.Schematic.load(
            "tests/reference_kicad_projects/property_preservation/test.kicad_sch"
        )
        r1 = sch.components.get("R1")

        # Description has empty value
        assert r1.properties["Description"] == ""
        # It's visible in reference
        assert "Description" not in r1.hidden_properties

    def test_special_characters_in_property_value(self):
        """Properties with special characters should be preserved."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        # Add property with quotes
        r1.add_property("Notes", 'Use "high quality" parts', hidden=False)

        assert r1.properties["Notes"] == 'Use "high quality" parts'

    def test_property_not_in_hidden_set_if_never_added(self):
        """Newly created components should have empty hidden_properties set."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        # Should have empty set by default
        assert isinstance(r1.hidden_properties, set)
        assert len(r1.hidden_properties) == 0

    def test_delete_property_should_remove_from_hidden_set(self):
        """Deleting a property should also clean up hidden_properties."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        r1.add_property("TempProp", "TempValue", hidden=True)
        assert "TempProp" in r1.hidden_properties

        # Delete property
        del r1.properties["TempProp"]
        r1.hidden_properties.discard("TempProp")

        assert "TempProp" not in r1.properties
        assert "TempProp" not in r1.hidden_properties


@pytest.mark.format
class TestFormatPreservation:
    """Test that S-expression format is preserved correctly."""

    def test_hide_flag_present_for_hidden_properties(self, tmp_path):
        """Hidden properties should have (hide yes) in saved file."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))
        r1.add_property("MPN", "TEST_MPN", hidden=True)

        output_path = tmp_path / "test_hide.kicad_sch"
        sch.save(str(output_path))

        # Read raw file and check for hide flag
        with open(output_path, "r") as f:
            content = f.read()

        # Should contain (hide yes) for MPN property
        assert "(hide yes)" in content
        assert 'property "MPN" "TEST_MPN"' in content

    def test_no_hide_flag_for_visible_properties(self, tmp_path):
        """Visible properties should NOT have (hide yes) in saved file."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))
        r1.add_property("Notes", "Important", hidden=False)

        output_path = tmp_path / "test_visible.kicad_sch"
        sch.save(str(output_path))

        # Read raw file
        with open(output_path, "r") as f:
            content = f.read()

        # Find the Notes property section
        notes_start = content.find('property "Notes"')
        notes_end = content.find(")", notes_start + 200)  # Find closing paren
        notes_section = content[notes_start:notes_end]

        # Should NOT contain hide flag
        assert "(hide yes)" not in notes_section


class TestHasPropertyMethod:
    """Test the has_property() method."""

    def test_has_property_returns_true_when_property_exists(self):
        """has_property() should return True when property exists."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))
        r1.add_property("MPN", "RC0603FR-0710KL")

        assert r1.has_property("MPN") is True

    def test_has_property_returns_false_when_property_missing(self):
        """has_property() should return False when property doesn't exist."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        assert r1.has_property("MPN") is False

    def test_has_property_with_custom_properties(self):
        """has_property() should work with custom user properties."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        # Add some custom properties
        r1.add_property("Tolerance", "1%")
        r1.add_property("Power", "0.1W")

        # Should detect custom properties
        assert r1.has_property("Tolerance") is True
        assert r1.has_property("Power") is True
        assert r1.has_property("NonExistent") is False

    def test_has_property_case_sensitive(self):
        """has_property() should be case-sensitive."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))
        r1.add_property("MPN", "TEST")

        assert r1.has_property("MPN") is True
        assert r1.has_property("mpn") is False
        assert r1.has_property("Mpn") is False

    def test_has_property_after_adding_property(self):
        """has_property() should return True after adding property."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        assert r1.has_property("Manufacturer") is False

        r1.add_property("Manufacturer", "Yageo")

        assert r1.has_property("Manufacturer") is True

    def test_has_property_after_removing_property(self):
        """has_property() should return False after removing property."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))
        r1.add_property("TempProp", "TempValue")

        assert r1.has_property("TempProp") is True

        r1.remove_property("TempProp")

        assert r1.has_property("TempProp") is False

    def test_has_property_with_empty_value(self):
        """has_property() should return True even if value is empty."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))
        r1.add_property("EmptyProp", "")

        assert r1.has_property("EmptyProp") is True
        assert r1.get_property("EmptyProp") == ""

    def test_has_property_with_hidden_property(self):
        """has_property() should return True for hidden properties."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))
        r1.add_property("HiddenProp", "HiddenValue", hidden=True)

        # Property exists regardless of visibility
        assert r1.has_property("HiddenProp") is True
        assert "HiddenProp" in r1.hidden_properties

    def test_has_property_usage_example_from_docs(self):
        """Test the usage example from documentation (RECIPES.md)."""
        sch = ksa.create_schematic("Test")
        r1 = sch.components.add("Device:R", "R1", "10k", position=(100, 100))

        # Example from RECIPES.md
        issues = []
        for comp in sch.components:
            if not comp.has_property("MPN"):
                issues.append(f"{comp.reference}: Missing MPN property")

        # Should find issue for R1
        assert len(issues) == 1
        assert "R1" in issues[0]
        assert "Missing MPN" in issues[0]

        # Add MPN and verify issue goes away
        r1.add_property("MPN", "RC0603FR-0710KL")
        issues = []
        for comp in sch.components:
            if not comp.has_property("MPN"):
                issues.append(f"{comp.reference}: Missing MPN property")

        assert len(issues) == 0
