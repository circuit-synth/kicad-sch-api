"""
Tests for non-unique reference index handling (Issue #171).

The reference index uses unique=False to support multi-unit components.
These tests verify that collection methods correctly handle list returns
from IndexRegistry.get() when multiple components share the same reference.
"""

import pytest

from kicad_sch_api.collections.components import ComponentCollection
from kicad_sch_api.core.types import Point, SchematicSymbol


class TestNonUniqueIndexHandling:
    """Verify ComponentCollection methods handle non-unique index correctly."""

    def test_get_with_single_component_returns_component(self):
        """When only one component has reference, get() should work.

        The reference index returns [0] (list with one item), and get()
        must handle this correctly.
        """
        symbol_data = SchematicSymbol(
            uuid="uuid1",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(100, 100),
        )
        collection = ComponentCollection([symbol_data])

        # Reference index returns [0] (list with one item)
        component = collection.get("R1")
        assert component is not None
        assert component.reference == "R1"
        assert component.uuid == "uuid1"

    def test_get_with_multiple_same_reference_returns_first(self):
        """When multiple components share reference, get() returns first.

        Multi-unit components (like op-amps) can have multiple units with
        the same reference (U1A, U1B both have reference "U1"). The reference
        index returns [0, 1] and get() should return the first component.
        """
        # Simulate multi-unit component (both units share reference "U1")
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:LED",
                reference="U1",
                value="LED",
                position=Point(100, 100),
                unit=1,
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:LED",
                reference="U1",
                value="LED",
                position=Point(150, 100),
                unit=2,
            ),
        ]
        collection = ComponentCollection(symbol_data)

        # Reference index returns [0, 1] (list with two items)
        component = collection.get("U1")
        assert component is not None
        assert component.reference == "U1"
        assert component.uuid == "uuid1"  # First one
        assert component._data.unit == 1

    def test_get_with_three_units_returns_first(self):
        """When three components share reference, get() returns first.

        Tests with more than two components to ensure list handling
        works for any number of items.
        """
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Amplifier_Operational:TL072",
                reference="U1",
                value="TL072",
                position=Point(100, 100),
                unit=1,
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Amplifier_Operational:TL072",
                reference="U1",
                value="TL072",
                position=Point(150, 100),
                unit=2,
            ),
            SchematicSymbol(
                uuid="uuid3",
                lib_id="Amplifier_Operational:TL072",
                reference="U1",
                value="TL072",
                position=Point(200, 100),
                unit=3,
            ),
        ]
        collection = ComponentCollection(symbol_data)

        component = collection.get("U1")
        assert component is not None
        assert component.uuid == "uuid1"  # First one
        assert component._data.unit == 1

    def test_get_nonexistent_returns_none(self):
        """When no components match, get() returns None.

        Reference index returns None (key not in index), and get()
        should handle this gracefully.
        """
        collection = ComponentCollection()

        # Reference index returns None (not in index)
        component = collection.get("NonExistent")
        assert component is None

    def test_get_after_adding_components_with_same_reference(self):
        """Test get() works after dynamically adding components with same reference."""
        collection = ComponentCollection()

        # Add first component
        symbol1 = SchematicSymbol(
            uuid="uuid1",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(100, 100),
            unit=1,
        )
        collection._add_item_to_collection(symbol1)

        # Add second component with same reference
        symbol2 = SchematicSymbol(
            uuid="uuid2",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(150, 100),
            unit=2,
        )
        collection._add_item_to_collection(symbol2)

        # Should still work and return first
        component = collection.get("R1")
        assert component is not None
        assert component.uuid == "uuid1"


class TestNonUniqueIndexRemove:
    """Verify remove() method handles non-unique index correctly."""

    def test_remove_with_single_component_removes_it(self):
        """When only one component has reference, remove() should work."""
        symbol_data = SchematicSymbol(
            uuid="uuid1",
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=Point(100, 100),
        )
        collection = ComponentCollection([symbol_data])

        result = collection.remove("R1")
        assert result is True
        assert len(collection) == 0
        assert collection.get("R1") is None

    def test_remove_with_multiple_same_reference_removes_first(self):
        """When multiple components share reference, remove() removes first.

        After removing the first component, the second component should
        still be accessible by the same reference.
        """
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:LED",
                reference="U1",
                value="LED",
                position=Point(100, 100),
                unit=1,
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:LED",
                reference="U1",
                value="LED",
                position=Point(150, 100),
                unit=2,
            ),
        ]
        collection = ComponentCollection(symbol_data)

        # Remove first unit
        result = collection.remove("U1")
        assert result is True
        assert len(collection) == 1

        # Second unit should remain and be accessible by same reference
        remaining = collection.get("U1")
        assert remaining is not None
        assert remaining.uuid == "uuid2"
        assert remaining._data.unit == 2

    def test_remove_nonexistent_returns_false(self):
        """When no components match, remove() returns False."""
        collection = ComponentCollection()

        result = collection.remove("NonExistent")
        assert result is False

    def test_remove_all_units_sequentially(self):
        """Test removing all units of a multi-unit component one by one."""
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Amplifier_Operational:TL072",
                reference="U1",
                value="TL072",
                position=Point(100, 100),
                unit=1,
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Amplifier_Operational:TL072",
                reference="U1",
                value="TL072",
                position=Point(150, 100),
                unit=2,
            ),
            SchematicSymbol(
                uuid="uuid3",
                lib_id="Amplifier_Operational:TL072",
                reference="U1",
                value="TL072",
                position=Point(200, 100),
                unit=3,
            ),
        ]
        collection = ComponentCollection(symbol_data)

        # Remove first unit
        result = collection.remove("U1")
        assert result is True
        assert len(collection) == 2

        # Remove second unit (which is now first)
        result = collection.remove("U1")
        assert result is True
        assert len(collection) == 1

        # Remove third unit (which is now first)
        result = collection.remove("U1")
        assert result is True
        assert len(collection) == 0

        # All gone
        assert collection.get("U1") is None


class TestNonUniqueIndexEdgeCases:
    """Test edge cases in non-unique index handling."""

    def test_get_with_empty_collection(self):
        """Test get() on empty collection returns None."""
        collection = ComponentCollection()
        component = collection.get("R1")
        assert component is None

    def test_remove_from_empty_collection(self):
        """Test remove() on empty collection returns False."""
        collection = ComponentCollection()
        result = collection.remove("R1")
        assert result is False

    def test_filter_with_non_unique_references(self):
        """Test filter() works correctly with non-unique references.

        Filter uses different code path than get(), ensure it works too.
        """
        symbol_data = [
            SchematicSymbol(
                uuid="uuid1",
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=Point(100, 100),
                unit=1,
            ),
            SchematicSymbol(
                uuid="uuid2",
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=Point(150, 100),
                unit=2,
            ),
            SchematicSymbol(
                uuid="uuid3",
                lib_id="Device:C",
                reference="C1",
                value="100nF",
                position=Point(200, 100),
            ),
        ]
        collection = ComponentCollection(symbol_data)

        # Filter by lib_id should return both R1 units
        resistors = collection.filter(lib_id="Device:R")
        assert len(resistors) == 2
        assert all(r.reference == "R1" for r in resistors)

    def test_mixed_unique_and_non_unique_references(self):
        """Test collection with some unique and some non-unique references."""
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
                lib_id="Device:LED",
                reference="U1",
                value="LED",
                position=Point(150, 100),
                unit=1,
            ),
            SchematicSymbol(
                uuid="uuid3",
                lib_id="Device:LED",
                reference="U1",
                value="LED",
                position=Point(200, 100),
                unit=2,
            ),
            SchematicSymbol(
                uuid="uuid4",
                lib_id="Device:C",
                reference="C1",
                value="100nF",
                position=Point(250, 100),
            ),
        ]
        collection = ComponentCollection(symbol_data)

        # Unique references should work
        assert collection.get("R1") is not None
        assert collection.get("C1") is not None

        # Non-unique reference should return first
        u1 = collection.get("U1")
        assert u1 is not None
        assert u1.uuid == "uuid2"
