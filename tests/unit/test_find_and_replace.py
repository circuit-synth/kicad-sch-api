"""
Tests for find and replace functionality in schematic.

Tests cover:
- Literal string replacement in labels
- Regex pattern replacement in labels
- Scope-based replacement (labels, components, properties, all)
- Validation preventing invalid component references
- Edge cases and error handling
"""

import re
from unittest.mock import Mock, patch

import pytest

from kicad_sch_api import create_schematic
from kicad_sch_api.core.types import Point, SchematicSymbol


def create_mock_component(lib_id, reference, value, position=(0, 0), parent_collection=None):
    """Create a mock component without needing actual libraries."""
    from kicad_sch_api.collections.components import Component
    import uuid

    # Create minimal component data
    component_data = SchematicSymbol(
        uuid=str(uuid.uuid4()),
        lib_id=lib_id,
        reference=reference,
        value=value,
        position=Point(position[0], position[1]),
        rotation=0.0,
        properties={},
        unit=1,
        in_bom=True,
        on_board=True,
        fields_autoplaced=True,
        footprint="",
        instances=[],
    )

    return Component(component_data, parent_collection=parent_collection)


class TestFindAndReplaceLiterals:
    """Test literal string replacement."""

    def test_replace_label_text_simple(self):
        """Test simple literal replacement in label text."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR_1", position=(100, 100))
        sch.labels.add("MOTOR_2", position=(120, 100))
        sch.labels.add("POWER", position=(140, 100))

        # Replace MOTOR_ with DC_MOTOR_
        results = sch.find_and_replace(find="MOTOR_", replace="DC_MOTOR_", scope="labels")

        assert results["replaced_count"] == 2
        assert results["scope"] == "labels"

        # Verify labels were updated
        labels = list(sch.labels)
        label_texts = [l.text for l in labels]
        assert "DC_MOTOR_1" in label_texts
        assert "DC_MOTOR_2" in label_texts
        assert "POWER" in label_texts
        assert "MOTOR_1" not in label_texts

    def test_replace_label_text_case_sensitive(self):
        """Test that replacement is case-sensitive by default."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR_1", position=(100, 100))
        sch.labels.add("motor_2", position=(120, 100))

        # Replace only uppercase
        results = sch.find_and_replace(find="MOTOR_", replace="DC_MOTOR_", scope="labels")

        assert results["replaced_count"] == 1

        labels = list(sch.labels)
        label_texts = [l.text for l in labels]
        assert "DC_MOTOR_1" in label_texts
        assert "motor_2" in label_texts  # Unchanged

    def test_replace_no_matches(self):
        """Test replacement when no matches found."""
        sch = create_schematic("test")
        sch.labels.add("POWER", position=(100, 100))

        results = sch.find_and_replace(find="MOTOR_", replace="DC_MOTOR_", scope="labels")

        assert results["replaced_count"] == 0
        assert results["scope"] == "labels"


class TestFindAndReplaceRegex:
    """Test regex pattern replacement."""

    def test_replace_with_regex_pattern(self):
        """Test regex pattern with capture groups."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR_1", position=(100, 100))
        sch.labels.add("MOTOR_2", position=(120, 100))
        sch.labels.add("MOTOR_12", position=(140, 100))

        # Replace MOTOR_X with DC_MOTOR_X (single digit only)
        results = sch.find_and_replace(
            find=r"MOTOR_(\d)$", replace=r"DC_MOTOR_\1", scope="labels", regex=True
        )

        assert results["replaced_count"] == 2
        assert results["regex"] is True

        labels = list(sch.labels)
        label_texts = [l.text for l in labels]
        assert "DC_MOTOR_1" in label_texts
        assert "DC_MOTOR_2" in label_texts
        assert "MOTOR_12" in label_texts  # Not matched (two digits)

    def test_replace_with_complex_regex(self):
        """Test complex regex with multiple capture groups."""
        sch = create_schematic("test")
        sch.labels.add("PWM_CH1_OUT", position=(100, 100))
        sch.labels.add("PWM_CH2_OUT", position=(120, 100))

        # Replace PWM_CHX_OUT with TIMER_CHX_OUTPUT
        results = sch.find_and_replace(
            find=r"PWM_CH(\d+)_OUT", replace=r"TIMER_CH\1_OUTPUT", scope="labels", regex=True
        )

        assert results["replaced_count"] == 2

        labels = list(sch.labels)
        label_texts = [l.text for l in labels]
        assert "TIMER_CH1_OUTPUT" in label_texts
        assert "TIMER_CH2_OUTPUT" in label_texts

    def test_regex_invalid_pattern(self):
        """Test that invalid regex pattern raises error."""
        sch = create_schematic("test")
        sch.labels.add("TEST", position=(100, 100))

        with pytest.raises(ValueError, match="Invalid regex pattern"):
            sch.find_and_replace(
                find=r"[invalid(regex", replace="replacement", scope="labels", regex=True
            )


class TestFindAndReplaceScopes:
    """Test different replacement scopes."""

    def test_scope_labels_only(self):
        """Test that scope='labels' only affects labels."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR_1", position=(100, 100))

        # Add component directly to bypass library requirement
        comp = create_mock_component(
            "Device:R", "RMOTOR1", "10k", position=(150, 150), parent_collection=sch._components
        )
        sch._components._items.append(comp)
        sch._components._indexes_dirty = True

        results = sch.find_and_replace(find="MOTOR_", replace="DCMOTOR_", scope="labels")

        assert results["replaced_count"] == 1

        # Label changed
        labels = list(sch.labels)
        assert labels[0].text == "DCMOTOR_1"

        # Component unchanged
        components = list(sch.components)
        assert components[0].reference == "RMOTOR1"

    def test_scope_components_only(self):
        """Test that scope='components' only affects component references."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR_1", position=(100, 100))

        # Add component directly
        comp = create_mock_component(
            "Device:R", "RMOTOR1", "10k", position=(150, 150), parent_collection=sch._components
        )
        sch._components._items.append(comp)
        sch._components._indexes_dirty = True

        results = sch.find_and_replace(find="MOTOR", replace="DCMOTOR", scope="components")

        assert results["replaced_count"] == 1

        # Component changed
        components = list(sch.components)
        assert components[0].reference == "RDCMOTOR1"

        # Label unchanged
        labels = list(sch.labels)
        assert labels[0].text == "MOTOR_1"

    def test_scope_properties_only(self):
        """Test that scope='properties' only affects component properties."""
        sch = create_schematic("test")

        # Add component directly
        comp = create_mock_component(
            "Device:R", "R1", "MOTORTYPE", position=(150, 150), parent_collection=sch._components
        )
        sch._components._items.append(comp)
        sch._components._indexes_dirty = True

        results = sch.find_and_replace(find="MOTORTYPE", replace="DCMOTOR", scope="properties")

        assert results["replaced_count"] == 1

        # Component value changed
        components = list(sch.components)
        assert components[0].value == "DCMOTOR"

    def test_scope_all(self):
        """Test that scope='all' affects all elements."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR_1", position=(100, 100))

        # Add component directly
        comp = create_mock_component(
            "Device:R",
            "RMOTOR1",
            "MOTORTYPE",
            position=(150, 150),
            parent_collection=sch._components,
        )
        sch._components._items.append(comp)
        sch._components._indexes_dirty = True
        comp.set_property("Description", "MOTOR controller")

        results = sch.find_and_replace(find="MOTOR", replace="DCMOTOR", scope="all")

        # Should replace in label, component reference, and properties
        assert results["replaced_count"] >= 3

        labels = list(sch.labels)
        assert labels[0].text == "DCMOTOR_1"

        components = list(sch.components)
        assert components[0].reference == "RDCMOTOR1"
        assert components[0].value == "DCMOTORTYPE"

    def test_scope_invalid(self):
        """Test that invalid scope raises error."""
        sch = create_schematic("test")

        with pytest.raises(ValueError, match="Invalid scope"):
            sch.find_and_replace(find="test", replace="new", scope="invalid_scope")


class TestFindAndReplaceValidation:
    """Test validation and error handling."""

    def test_prevent_empty_label_text(self):
        """Test that replacement resulting in empty label is prevented."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR", position=(100, 100))

        with pytest.raises(ValueError, match="empty"):
            sch.find_and_replace(find="MOTOR", replace="", scope="labels")

    def test_prevent_invalid_component_reference(self):
        """Test that replacement resulting in invalid component reference is prevented."""
        sch = create_schematic("test")

        # Add component directly
        comp = create_mock_component(
            "Device:R", "R1", "10k", position=(150, 150), parent_collection=sch._components
        )
        sch._components._items.append(comp)
        sch._components._indexes_dirty = True

        with pytest.raises(ValueError, match="Invalid component reference"):
            sch.find_and_replace(
                find="R", replace="9", scope="components"  # Would make "91" - starts with number
            )

    def test_prevent_duplicate_component_references(self):
        """Test that replacement creating duplicate references is prevented."""
        sch = create_schematic("test")

        # Add components directly
        comp1 = create_mock_component(
            "Device:R", "R1", "10k", position=(150, 150), parent_collection=sch._components
        )
        comp2 = create_mock_component(
            "Device:R", "R2", "20k", position=(170, 150), parent_collection=sch._components
        )
        sch._components._items.append(comp1)
        sch._components._items.append(comp2)
        sch._components._indexes_dirty = True

        with pytest.raises(ValueError, match="duplicate"):
            sch.find_and_replace(find="2", replace="1", scope="components")

    def test_empty_find_string(self):
        """Test that empty find string raises error."""
        sch = create_schematic("test")

        with pytest.raises(ValueError, match="Find string cannot be empty"):
            sch.find_and_replace(find="", replace="replacement", scope="labels")

    def test_dry_run_mode(self):
        """Test dry run mode that doesn't modify schematic."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR_1", position=(100, 100))
        sch.labels.add("MOTOR_2", position=(120, 100))

        results = sch.find_and_replace(
            find="MOTOR_", replace="DC_MOTOR_", scope="labels", dry_run=True
        )

        assert results["replaced_count"] == 2
        assert results["dry_run"] is True

        # Verify nothing actually changed
        labels = list(sch.labels)
        label_texts = [l.text for l in labels]
        assert "MOTOR_1" in label_texts
        assert "MOTOR_2" in label_texts
        assert "DC_MOTOR_1" not in label_texts


class TestFindAndReplaceResults:
    """Test return value structure."""

    def test_result_structure(self):
        """Test that result dictionary has expected structure."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR_1", position=(100, 100))

        results = sch.find_and_replace(find="MOTOR_", replace="DC_MOTOR_", scope="labels")

        # Check all expected keys
        assert "replaced_count" in results
        assert "scope" in results
        assert "regex" in results
        assert "dry_run" in results
        assert "replacements" in results

        # Check types
        assert isinstance(results["replaced_count"], int)
        assert isinstance(results["scope"], str)
        assert isinstance(results["regex"], bool)
        assert isinstance(results["dry_run"], bool)
        assert isinstance(results["replacements"], list)

    def test_result_replacements_details(self):
        """Test that result includes details of each replacement."""
        sch = create_schematic("test")
        sch.labels.add("MOTOR_1", position=(100, 100))
        sch.labels.add("MOTOR_2", position=(120, 100))

        results = sch.find_and_replace(find="MOTOR_", replace="DC_MOTOR_", scope="labels")

        assert len(results["replacements"]) == 2

        # Check first replacement details
        repl = results["replacements"][0]
        assert "element_type" in repl
        assert "old_value" in repl
        assert "new_value" in repl
        assert repl["element_type"] == "label"
        assert repl["old_value"] == "MOTOR_1"
        assert repl["new_value"] == "DC_MOTOR_1"
