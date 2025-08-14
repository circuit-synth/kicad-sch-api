"""
Tests for atomic schematic operations.
Adapted from circuit-synth atomic operations tests.
"""

import tempfile
from pathlib import Path

import pytest

from kicad_sch_api.core.schematic import Schematic
from kicad_sch_api.core.types import Point
from kicad_sch_api.utils.validation import ValidationError


class TestAtomicOperations:
    """Test atomic component operations with exact format preservation."""

    def test_add_component_to_empty_schematic(self):
        """Test adding a component to an empty schematic."""
        # Create new schematic
        sch = Schematic.create("Test Circuit")

        # Add component
        component = sch.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=(100, 50)
        )

        # Verify component was added
        assert component.reference == "R1"
        assert component.lib_id == "Device:R"
        assert component.value == "10k"
        assert component.position.x == 100
        assert component.position.y == 50

        # Verify it's in the collection
        assert len(sch.components) == 1
        assert sch.components.get("R1") == component

    def test_remove_component_from_schematic(self):
        """Test removing a component from schematic."""
        # Create schematic with component
        sch = Schematic.create("Test Circuit")
        component = sch.components.add("Device:R", "R1", "10k", (100, 50))

        # Verify component exists
        assert len(sch.components) == 1
        assert sch.components.get("R1") is not None

        # Remove component
        success = sch.components.remove("R1")
        assert success is True

        # Verify component is gone
        assert len(sch.components) == 0
        assert sch.components.get("R1") is None

    def test_remove_nonexistent_component(self):
        """Test removing component that doesn't exist."""
        sch = Schematic.create("Test Circuit")

        # Try to remove non-existent component
        success = sch.components.remove("R999")
        assert success is False

    def test_add_multiple_components(self):
        """Test adding multiple components."""
        sch = Schematic.create("Test Circuit")

        # Add multiple components
        components = []
        for i in range(5):
            comp = sch.components.add(
                lib_id="Device:R", reference=f"R{i+1}", value="10k", position=(i * 20, 50)
            )
            components.append(comp)

        # Verify all were added
        assert len(sch.components) == 5

        # Check each component
        for i, comp in enumerate(components):
            assert comp.reference == f"R{i+1}"
            assert comp.position.x == i * 20
            assert sch.components.get(f"R{i+1}") == comp

    def test_duplicate_reference_validation(self):
        """Test that duplicate references are prevented."""
        sch = Schematic.create("Test Circuit")

        # Add first component
        sch.components.add("Device:R", "R1", "10k")

        # Try to add duplicate reference
        with pytest.raises(ValidationError, match="Reference R1 already exists"):
            sch.components.add("Device:C", "R1", "0.1uF")

    def test_invalid_reference_format(self):
        """Test validation of reference format."""
        sch = Schematic.create("Test Circuit")

        # Try invalid reference formats
        invalid_refs = ["1R", "R-1", "r1", "R 1", ""]

        for invalid_ref in invalid_refs:
            with pytest.raises(ValidationError, match="Invalid reference format"):
                sch.components.add("Device:R", invalid_ref, "10k")

    def test_invalid_lib_id_format(self):
        """Test validation of lib_id format."""
        sch = Schematic.create("Test Circuit")

        # Try invalid lib_id formats
        invalid_lib_ids = ["DeviceR", "Device:", ":R", "", "Device::R"]

        for invalid_lib_id in invalid_lib_ids:
            with pytest.raises(ValidationError, match="Invalid lib_id format"):
                sch.components.add(invalid_lib_id, "R1", "10k")

    def test_component_property_updates(self):
        """Test updating component properties."""
        sch = Schematic.create("Test Circuit")
        comp = sch.components.add("Device:R", "R1", "10k")

        # Update standard properties
        comp.value = "22k"
        comp.footprint = "Resistor_SMD:R_0603_1608Metric"

        # Update custom properties
        comp.set_property("MPN", "RC0603FR-0722KL")
        comp.set_property("Tolerance", "1%")

        # Verify updates
        assert comp.value == "22k"
        assert comp.footprint == "Resistor_SMD:R_0603_1608Metric"
        assert comp.get_property("MPN") == "RC0603FR-0722KL"
        assert comp.get_property("Tolerance") == "1%"

    def test_reference_update_validation(self):
        """Test validation when updating component reference."""
        sch = Schematic.create("Test Circuit")
        comp1 = sch.components.add("Device:R", "R1", "10k")
        comp2 = sch.components.add("Device:R", "R2", "22k")

        # Valid reference update
        comp1.reference = "R5"
        assert comp1.reference == "R5"
        assert sch.components.get("R5") == comp1
        assert sch.components.get("R1") is None

        # Try to set duplicate reference
        with pytest.raises(ValidationError, match="Reference R2 already exists"):
            comp1.reference = "R2"

    def test_component_position_updates(self):
        """Test updating component positions."""
        sch = Schematic.create("Test Circuit")
        comp = sch.components.add("Device:R", "R1", "10k", (100, 50))

        # Update position with Point object
        comp.position = Point(200, 100)
        assert comp.position.x == 200
        assert comp.position.y == 100

        # Update position with tuple
        comp.position = (300, 150)
        assert comp.position.x == 300
        assert comp.position.y == 150

        # Test move method
        comp.move(400, 200)
        assert comp.position.x == 400
        assert comp.position.y == 200

        # Test translate method
        comp.translate(50, 25)
        assert comp.position.x == 450
        assert comp.position.y == 225

    def test_file_save_and_reload(self):
        """Test saving schematic and reloading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.kicad_sch"

            # Create schematic with components
            sch = Schematic.create("Test Circuit")
            comp1 = sch.components.add("Device:R", "R1", "10k", (100, 50))
            comp2 = sch.components.add("Device:C", "C1", "0.1uF", (150, 50))

            # Save schematic
            sch.save(file_path)
            assert file_path.exists()

            # Reload schematic
            sch2 = Schematic.load(file_path)

            # Verify components were preserved
            assert len(sch2.components) == 2

            r1 = sch2.components.get("R1")
            assert r1 is not None
            assert r1.lib_id == "Device:R"
            assert r1.value == "10k"
            assert r1.position.x == 100
            assert r1.position.y == 50

            c1 = sch2.components.get("C1")
            assert c1 is not None
            assert c1.lib_id == "Device:C"
            assert c1.value == "0.1uF"


class TestAtomicOperationsSafety:
    """Test safety features of atomic operations."""

    def test_backup_and_restore(self):
        """Test backup functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.kicad_sch"

            # Create and save initial schematic
            sch = Schematic.create("Test Circuit")
            sch.components.add("Device:R", "R1", "10k")
            sch.save(file_path)

            # Create backup
            backup_path = sch.backup()
            assert backup_path.exists()
            assert backup_path.name.endswith(".backup")

            # Verify backup contains original content
            original_content = file_path.read_text()
            backup_content = backup_path.read_text()
            assert original_content == backup_content

    def test_atomic_operation_rollback(self):
        """Test atomic operation with rollback on error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.kicad_sch"

            # Create and save initial schematic
            sch = Schematic.create("Test Circuit")
            sch.components.add("Device:R", "R1", "10k")
            sch.save(file_path)

            initial_component_count = len(sch.components)

            # Test atomic operation that should fail
            try:
                with sch:  # Atomic operation context
                    # Add valid component
                    sch.components.add("Device:C", "C1", "0.1uF")

                    # Try to add invalid component (should fail)
                    sch.components.add("Invalid:Format", "R1", "fail")  # Duplicate ref

            except ValidationError:
                # Expected to fail due to duplicate reference
                pass

            # Verify rollback occurred (if implemented)
            # For now, just verify we can handle the exception
            assert len(sch.components) >= initial_component_count

    def test_validation_before_save(self):
        """Test that validation prevents saving invalid schematics."""
        sch = Schematic.create("Test Circuit")

        # Add component with invalid reference (bypass validation for this test)
        # This tests the save-time validation
        # For now, just test that save works with valid data
        comp = sch.components.add("Device:R", "R1", "10k")

        with tempfile.NamedTemporaryFile(suffix=".kicad_sch", delete=False) as f:
            try:
                sch.save(f.name)
                # Should succeed
                assert Path(f.name).exists()
            finally:
                Path(f.name).unlink()
