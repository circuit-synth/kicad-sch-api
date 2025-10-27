"""
Unit tests for ComponentCollection class.

Tests component-specific functionality including reference indexing,
lib_id grouping, and component-specific operations.
"""

from unittest.mock import MagicMock, patch

import pytest

from kicad_sch_api.collections.components import Component, ComponentCollection
from kicad_sch_api.core.types import Point, SchematicSymbol
from kicad_sch_api.utils.validation import ValidationError


class TestComponentCollection:
    """Test cases for ComponentCollection."""

    def test_collection_initialization_empty(self):
        """Test component collection initializes empty correctly."""
        collection = ComponentCollection()
        assert len(collection) == 0

    def test_collection_initialization_with_components(self):
        """Test collection initializes with components correctly."""
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=Point(100, 100),
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:C",
                reference="C1",
                value="100nF",
                position=Point(200, 100),
            ),
        ]
        collection = ComponentCollection(symbol_data)

        assert len(collection) == 2
        assert collection.get_by_reference("R1") is not None
        assert collection.get_by_reference("C1") is not None

    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_lib_id")
    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_reference")
    @patch("kicad_sch_api.core.geometry.snap_to_grid")
    def test_add_component_basic(self, mock_snap, mock_validate_ref, mock_validate_lib):
        """Test adding a basic component."""
        mock_validate_lib.return_value = True
        mock_validate_ref.return_value = True
        mock_snap.return_value = (100.0, 100.0)

        collection = ComponentCollection()

        component = collection.add(
            lib_id="Device:R", reference="R1", value="10k", position=(100, 100)
        )

        assert isinstance(component, Component)
        assert component.reference == "R1"
        assert component.lib_id == "Device:R"
        assert component.value == "10k"
        assert len(collection) == 1

    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_lib_id")
    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_reference")
    @patch("kicad_sch_api.core.geometry.snap_to_grid")
    def test_add_component_auto_reference(self, mock_snap, mock_validate_ref, mock_validate_lib):
        """Test adding component with auto-generated reference."""
        mock_validate_lib.return_value = True
        mock_validate_ref.return_value = True
        mock_snap.return_value = (100.0, 100.0)

        collection = ComponentCollection()

        component = collection.add(lib_id="Device:R", value="10k")

        assert component.reference == "R1"  # Auto-generated

    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_lib_id")
    def test_add_component_invalid_lib_id(self, mock_validate_lib):
        """Test adding component with invalid lib_id raises error."""
        mock_validate_lib.return_value = False

        collection = ComponentCollection()

        with pytest.raises(ValidationError, match="Invalid lib_id format"):
            collection.add(lib_id="InvalidLibId")

    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_lib_id")
    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_reference")
    def test_add_component_invalid_reference(self, mock_validate_ref, mock_validate_lib):
        """Test adding component with invalid reference raises error."""
        mock_validate_lib.return_value = True
        mock_validate_ref.return_value = False

        collection = ComponentCollection()

        with pytest.raises(ValidationError, match="Invalid reference format"):
            collection.add(lib_id="Device:R", reference="Invalid Ref")

    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_lib_id")
    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_reference")
    @patch("kicad_sch_api.core.geometry.snap_to_grid")
    def test_add_component_duplicate_reference(
        self, mock_snap, mock_validate_ref, mock_validate_lib
    ):
        """Test adding component with duplicate reference raises error."""
        mock_validate_lib.return_value = True
        mock_validate_ref.return_value = True
        mock_snap.return_value = (100.0, 100.0)

        collection = ComponentCollection()

        # Add first component
        collection.add(lib_id="Device:R", reference="R1")

        # Try to add duplicate reference
        with pytest.raises(ValidationError, match="Reference R1 already exists"):
            collection.add(lib_id="Device:C", reference="R1")

    def test_get_by_reference(self):
        """Test getting components by reference."""
        symbol_data = SchematicSymbol(
            uuid="uuid1", lib_id="Device:R", reference="R1", value="10k", position=Point(100, 100)
        )
        collection = ComponentCollection([symbol_data])

        component = collection.get_by_reference("R1")
        assert component is not None
        assert component.reference == "R1"

        not_found = collection.get_by_reference("NonExistent")
        assert not_found is None

    def test_get_by_lib_id(self):
        """Test getting components by lib_id."""
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=Point(100, 100),
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:R",
                reference="R2",
                value="1k",
                position=Point(200, 100),
            ),
            SchematicSymbol(
                uuid="uuid3",
                lib_id="Device:C",
                reference="C1",
                value="100nF",
                position=Point(300, 100),
            ),
        ]
        collection = ComponentCollection(symbol_data)

        resistors = collection.get_by_lib_id("Device:R")
        assert len(resistors) == 2
        assert all(comp.lib_id == "Device:R" for comp in resistors)

        capacitors = collection.get_by_lib_id("Device:C")
        assert len(capacitors) == 1
        assert capacitors[0].lib_id == "Device:C"

        none_found = collection.get_by_lib_id("NonExistent")
        assert len(none_found) == 0

    def test_get_by_value(self):
        """Test getting components by value."""
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=Point(100, 100),
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:R",
                reference="R2",
                value="10k",
                position=Point(200, 100),
            ),
            SchematicSymbol(
                uuid="uuid3",
                lib_id="Device:R",
                reference="R3",
                value="1k",
                position=Point(300, 100),
            ),
        ]
        collection = ComponentCollection(symbol_data)

        ten_k_resistors = collection.get_by_value("10k")
        assert len(ten_k_resistors) == 2
        assert all(comp.value == "10k" for comp in ten_k_resistors)

        one_k_resistors = collection.get_by_value("1k")
        assert len(one_k_resistors) == 1
        assert one_k_resistors[0].value == "1k"

    def test_generate_reference_basic(self):
        """Test basic reference generation."""
        collection = ComponentCollection()

        # Test common component types
        assert collection._generate_reference("Device:R") == "R1"
        assert collection._generate_reference("Device:C") == "C1"
        assert collection._generate_reference("Device:L") == "L1"

    def test_generate_reference_with_existing(self):
        """Test reference generation with existing components."""
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=Point(100, 100),
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:R",
                reference="R2",
                value="1k",
                position=Point(200, 100),
            ),
        ]
        collection = ComponentCollection(symbol_data)

        # Should generate R3 since R1 and R2 exist
        next_ref = collection._generate_reference("Device:R")
        assert next_ref == "R3"

    def test_find_available_position(self):
        """Test finding available position for new component."""
        collection = ComponentCollection()

        position = collection._find_available_position()
        assert isinstance(position, Point)
        assert position.x >= 100.0
        assert position.y >= 100.0

    def test_update_reference_index(self):
        """Test updating reference index when component reference changes."""
        symbol_data = SchematicSymbol(
            uuid="uuid1", lib_id="Device:R", reference="R1", value="10k", position=Point(100, 100)
        )
        collection = ComponentCollection([symbol_data])

        component = collection.get_by_reference("R1")
        assert component is not None

        # Update reference through the index update method
        collection._update_reference_index("R1", "R99")

        # Old reference should not be found
        assert collection.get_by_reference("R1") is None
        # New reference should be found
        assert collection.get_by_reference("R99") is component

    def test_bulk_update(self):
        """Test bulk update operations."""
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=Point(100, 100),
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:R",
                reference="R2",
                value="1k",
                position=Point(200, 100),
            ),
            SchematicSymbol(
                uuid="uuid3",
                lib_id="Device:C",
                reference="C1",
                value="100nF",
                position=Point(300, 100),
            ),
        ]
        collection = ComponentCollection(symbol_data)

        # Bulk update all resistors
        updated_count = collection.bulk_update(
            criteria={"lib_id": "Device:R"}, updates={"footprint": "Resistor_SMD:R_0603_1608Metric"}
        )

        assert updated_count == 2
        assert collection.get_by_reference("R1").footprint == "Resistor_SMD:R_0603_1608Metric"
        assert collection.get_by_reference("R2").footprint == "Resistor_SMD:R_0603_1608Metric"
        assert collection.get_by_reference("C1").footprint is None  # Should not be updated


class TestComponent:
    """Test cases for Component wrapper class."""

    def test_component_properties(self):
        """Test component property access."""
        symbol_data = SchematicSymbol(
            uuid="uuid1",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(100, 100),
            rotation=90.0,
            footprint="Resistor_SMD:R_0603_1608Metric",
        )
        collection = ComponentCollection()
        component = Component(symbol_data, collection)

        assert component.uuid == "uuid1"
        assert component.reference == "R1"
        assert component.lib_id == "Device:R"
        assert component.value == "10k"
        assert component.position == Point(100, 100)
        assert component.rotation == 90.0
        assert component.footprint == "Resistor_SMD:R_0603_1608Metric"

    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_reference")
    def test_component_set_reference_valid(self, mock_validate):
        """Test setting valid component reference."""
        mock_validate.return_value = True

        symbol_data = SchematicSymbol(
            uuid="uuid1", lib_id="Device:R", reference="R1", value="10k", position=Point(100, 100)
        )
        collection = ComponentCollection()
        collection._reference_index = {}  # Empty index
        component = Component(symbol_data, collection)

        component.reference = "R99"
        assert component.reference == "R99"

    @patch("kicad_sch_api.utils.validation.SchematicValidator.validate_reference")
    def test_component_set_reference_invalid(self, mock_validate):
        """Test setting invalid component reference raises error."""
        mock_validate.return_value = False

        symbol_data = SchematicSymbol(
            uuid="uuid1", lib_id="Device:R", reference="R1", value="10k", position=Point(100, 100)
        )
        collection = ComponentCollection()
        component = Component(symbol_data, collection)

        with pytest.raises(ValidationError, match="Invalid reference format"):
            component.reference = "Invalid Ref"

    def test_component_set_value(self):
        """Test setting component value."""
        symbol_data = SchematicSymbol(
            uuid="uuid1", lib_id="Device:R", reference="R1", value="10k", position=Point(100, 100)
        )
        collection = ComponentCollection()
        component = Component(symbol_data, collection)

        component.value = "22k"
        assert component.value == "22k"
        assert collection.is_modified

    def test_component_set_position_point(self):
        """Test setting component position with Point."""
        symbol_data = SchematicSymbol(
            uuid="uuid1", lib_id="Device:R", reference="R1", value="10k", position=Point(100, 100)
        )
        collection = ComponentCollection()
        component = Component(symbol_data, collection)

        new_position = Point(200, 200)
        component.position = new_position
        assert component.position == new_position
        assert collection.is_modified

    def test_component_set_position_tuple(self):
        """Test setting component position with tuple."""
        symbol_data = SchematicSymbol(
            uuid="uuid1", lib_id="Device:R", reference="R1", value="10k", position=Point(100, 100)
        )
        collection = ComponentCollection()
        component = Component(symbol_data, collection)

        component.position = (200, 200)
        assert component.position == Point(200, 200)
        assert collection.is_modified

    def test_component_properties_management(self):
        """Test component property management."""
        symbol_data = SchematicSymbol(
            uuid="uuid1",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(100, 100),
            properties={"MPN": "RC0603FR-0710KL"},
        )
        collection = ComponentCollection()
        component = Component(symbol_data, collection)

        # Get existing property
        assert component.get_property("MPN") == "RC0603FR-0710KL"

        # Get non-existent property
        assert component.get_property("NonExistent") is None

        # Set new property
        component.set_property("Tolerance", "1%")
        assert component.get_property("Tolerance") == "1%"
        assert collection.is_modified

    def test_component_repr(self):
        """Test component string representation."""
        symbol_data = SchematicSymbol(
            uuid="uuid1",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(100, 100),
            rotation=90.0,
        )
        collection = ComponentCollection()
        component = Component(symbol_data, collection)

        repr_str = repr(component)
        assert "Component(ref='R1'" in repr_str
        assert "lib_id='Device:R'" in repr_str
        assert "value='10k'" in repr_str
        assert "pos=(100.000, 100.000)" in repr_str
        assert "rotation=90.0" in repr_str

    def test_remove_component_by_reference(self):
        """Test removing component by reference."""
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=Point(100, 100),
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:R",
                reference="R2",
                value="20k",
                position=Point(200, 100),
            ),
        ]
        collection = ComponentCollection(symbol_data)
        assert len(collection) == 2

        # Remove R2
        result = collection.remove("R2")
        assert result is True
        assert len(collection) == 1
        assert collection.get_by_reference("R1") is not None
        assert collection.get_by_reference("R2") is None

    def test_remove_component_by_uuid(self):
        """Test removing component by UUID."""
        symbol_data = SchematicSymbol(
            uuid="test-uuid-123",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(100, 100),
        )
        collection = ComponentCollection([symbol_data])

        # Remove by UUID
        result = collection.remove_by_uuid("test-uuid-123")
        assert result is True
        assert len(collection) == 0
        assert collection.get_by_reference("R1") is None

    def test_remove_component_by_object(self):
        """Test removing component by component object."""
        symbol_data = SchematicSymbol(
            uuid="uuid1",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(100, 100),
        )
        collection = ComponentCollection([symbol_data])
        component = collection.get_by_reference("R1")

        # Remove by object
        result = collection.remove_component(component)
        assert result is True
        assert len(collection) == 0
        assert collection.get_by_reference("R1") is None

    def test_remove_nonexistent_component_by_reference(self):
        """Test removing non-existent component by reference returns False."""
        collection = ComponentCollection()
        result = collection.remove("NonExistent")
        assert result is False

    def test_remove_nonexistent_component_by_uuid(self):
        """Test removing non-existent component by UUID returns False."""
        collection = ComponentCollection()
        result = collection.remove_by_uuid("nonexistent-uuid")
        assert result is False

    def test_remove_component_invalid_type_reference(self):
        """Test that remove() with non-string raises TypeError."""
        collection = ComponentCollection()
        with pytest.raises(TypeError, match="reference must be a string"):
            collection.remove(123)

    def test_remove_component_invalid_type_uuid(self):
        """Test that remove_by_uuid() with non-string raises TypeError."""
        collection = ComponentCollection()
        with pytest.raises(TypeError, match="component_uuid must be a string"):
            collection.remove_by_uuid(123)

    def test_remove_component_invalid_type_object(self):
        """Test that remove_component() with non-Component raises TypeError."""
        collection = ComponentCollection()
        with pytest.raises(TypeError, match="component must be a Component instance"):
            collection.remove_component("R1")

    def test_remove_updates_indexes(self):
        """Test that removing component updates all indexes properly."""
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=Point(100, 100),
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:C",
                reference="C1",
                value="100nF",
                position=Point(200, 100),
            ),
        ]
        collection = ComponentCollection(symbol_data)

        # Verify initial state
        assert "R1" in collection._reference_index
        assert "Device:R" in collection._lib_id_index
        assert "10k" in collection._value_index

        # Remove R1
        collection.remove("R1")

        # Verify indexes are updated
        assert "R1" not in collection._reference_index
        assert "Device:R" not in collection._lib_id_index
        assert "10k" not in collection._value_index
        assert collection.get_by_lib_id("Device:R") == []
        assert collection.get_by_value("10k") == []
