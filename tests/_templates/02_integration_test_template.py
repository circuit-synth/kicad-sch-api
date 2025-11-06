#!/usr/bin/env python3
"""
INTEGRATION TEST TEMPLATE: Pin Connection Workflow Testing

This template demonstrates testing complete workflows that involve pin connections.
Use this for testing:
  - End-to-end pin connection operations
  - Multiple components interacting through pins
  - Persistence (save/load) with pin data
  - Real-world circuit connection scenarios

Key Features:
  - Full workflow testing (create → connect → verify → save → reload)
  - Integration with file I/O operations
  - Multiple components and wiring
  - Temporary file handling for cleanup
  - Clear separation of arrange/act/assert phases
  - Logging to understand workflow execution
  - Error scenarios in realistic contexts

Copy and customize for your specific integration scenarios.
"""

import logging
import math
import os
import tempfile
from pathlib import Path

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestPinConnectionWorkflow:
    """
    Test suite for complete pin connection workflows.

    Demonstrates testing realistic circuit building scenarios where
    components are created, connected, and verified.
    """

    @pytest.fixture
    def temp_schematic_file(self):
        """
        Fixture: Temporary file for schematic testing.

        Creates a temporary file, provides it to test, cleans up after.
        Essential for testing file persistence.
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            suffix=".kicad_sch",
            delete=False  # We'll delete manually in cleanup
        ) as f:
            temp_path = f.name

        logger.info(f"Created temporary schematic file: {temp_path}")

        yield temp_path  # Provide to test

        # Cleanup after test
        try:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.info(f"Cleaned up temporary file: {temp_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {temp_path}: {e}")

    def test_create_two_components_and_get_pins(self):
        """
        Test: Create two components and verify pin positions.

        Simple integration: multiple components, pin retrieval.
        """
        logger.info("Integration test: Create two components")

        # Arrange: Create schematic and add components
        sch = ksa.create_schematic("Two Component Test")
        logger.info("Created schematic")

        r1 = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0)
        )
        logger.info(f"Added R1: {r1.position}")

        r2 = sch.components.add(
            lib_id="Device:R",
            reference="R2",
            value="20k",
            position=(150.0, 100.0)  # Next to R1
        )
        logger.info(f"Added R2: {r2.position}")

        # Act: Get pin positions from both components
        r1_pin1 = r1.get_pin_position("1")
        r1_pin2 = r1.get_pin_position("2")
        r2_pin1 = r2.get_pin_position("1")
        r2_pin2 = r2.get_pin_position("2")

        logger.debug(f"R1 pins: {r1_pin1}, {r1_pin2}")
        logger.debug(f"R2 pins: {r2_pin1}, {r2_pin2}")

        # Assert: All pins should be found
        assert r1_pin1 is not None
        assert r1_pin2 is not None
        assert r2_pin1 is not None
        assert r2_pin2 is not None

        # Assert: Pins from different components should be different
        assert r1_pin1 != r2_pin1, "Same pin numbers from different components should differ"

        # Assert: Components should have different positions
        assert r1.position != r2.position, "Components should be at different positions"

        # Assert: Pin spacing should be consistent
        r1_pin_distance = math.sqrt(
            (r1_pin2.x - r1_pin1.x)**2 + (r1_pin2.y - r1_pin1.y)**2
        )
        r2_pin_distance = math.sqrt(
            (r2_pin2.x - r2_pin1.x)**2 + (r2_pin2.y - r2_pin1.y)**2
        )
        logger.debug(f"R1 pin distance: {r1_pin_distance:.2f}mm")
        logger.debug(f"R2 pin distance: {r2_pin_distance:.2f}mm")

        assert math.isclose(
            r1_pin_distance, r2_pin_distance, rel_tol=0.01
        ), "Same component types should have same pin spacing"

    def test_save_and_reload_pin_positions(self, temp_schematic_file):
        """
        Test: Pin positions persist through save/load cycle.

        Comprehensive integration: create → save → load → verify
        """
        logger.info("Integration test: Save and reload pin positions")

        # Arrange & Act: Create schematic with components
        sch = ksa.create_schematic("Persistence Test")
        r1 = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            rotation=90  # Include rotation for complexity
        )
        logger.info(f"Created R1 at {r1.position} with {r1.rotation}° rotation")

        # Get original pin positions
        original_pin1 = r1.get_pin_position("1")
        original_pin2 = r1.get_pin_position("2")
        logger.debug(f"Original pins: {original_pin1}, {original_pin2}")

        # Act: Save schematic to file
        sch.save(temp_schematic_file)
        logger.info(f"Saved schematic to {temp_schematic_file}")

        # Assert: File should be created
        assert os.path.exists(temp_schematic_file), "Schematic file should exist"
        assert os.path.getsize(temp_schematic_file) > 0, "File should have content"
        logger.info(f"File size: {os.path.getsize(temp_schematic_file)} bytes")

        # Act: Reload schematic from file
        sch2 = ksa.Schematic.load(temp_schematic_file)
        logger.info("Reloaded schematic from file")

        # Assert: Schematic should have component
        r1_reloaded = sch2.components.get("R1")
        assert r1_reloaded is not None, "R1 should exist after reload"
        logger.debug(f"Reloaded R1: {r1_reloaded.position}, rotation: {r1_reloaded.rotation}")

        # Assert: Component properties should match
        assert r1_reloaded.reference == "R1", "Reference should match"
        assert r1_reloaded.value == "10k", "Value should match"
        assert math.isclose(r1_reloaded.rotation, 90.0, abs_tol=0.01), "Rotation should match"

        # Act: Get pin positions from reloaded component
        reloaded_pin1 = r1_reloaded.get_pin_position("1")
        reloaded_pin2 = r1_reloaded.get_pin_position("2")
        logger.debug(f"Reloaded pins: {reloaded_pin1}, {reloaded_pin2}")

        # Assert: Pin positions should match original
        if original_pin1 is not None and reloaded_pin1 is not None:
            assert math.isclose(
                original_pin1.x, reloaded_pin1.x, abs_tol=0.01
            ), f"Pin 1 X should match: {original_pin1.x} vs {reloaded_pin1.x}"
            assert math.isclose(
                original_pin1.y, reloaded_pin1.y, abs_tol=0.01
            ), f"Pin 1 Y should match: {original_pin1.y} vs {reloaded_pin1.y}"

    def test_circuit_workflow_with_multiple_connections(self):
        """
        Test: Build a simple circuit with multiple connections.

        Demonstrates:
          - Multiple components at different positions
          - Various rotations
          - Pin retrieval from each component
          - Position relationships between pins
        """
        logger.info("Integration test: Multi-component circuit")

        # Arrange: Create voltage divider circuit
        sch = ksa.create_schematic("Voltage Divider")

        # Add VCC power supply (top)
        vcc = sch.components.add(
            lib_id="power:VCC",
            reference="#PWR01",
            value="VCC",
            position=(100.0, 50.0)
        )
        logger.info(f"Added VCC at {vcc.position}")

        # Add resistor 1 (vertical orientation, 0°)
        r1 = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            rotation=0
        )
        logger.info(f"Added R1 at {r1.position}, rotation {r1.rotation}°")

        # Add resistor 2 (vertical orientation, 0°)
        r2 = sch.components.add(
            lib_id="Device:R",
            reference="R2",
            value="10k",
            position=(100.0, 150.0),
            rotation=0
        )
        logger.info(f"Added R2 at {r2.position}, rotation {r2.rotation}°")

        # Add GND ground symbol (bottom)
        gnd = sch.components.add(
            lib_id="power:GND",
            reference="#PWR02",
            value="GND",
            position=(100.0, 200.0)
        )
        logger.info(f"Added GND at {gnd.position}")

        # Assert: All components created successfully
        assert len(sch.components) == 4, "Should have 4 components"

        # Act: Get all pin positions
        r1_pin1 = r1.get_pin_position("1")
        r1_pin2 = r1.get_pin_position("2")
        r2_pin1 = r2.get_pin_position("1")
        r2_pin2 = r2.get_pin_position("2")

        logger.debug(f"R1: pin1={r1_pin1}, pin2={r1_pin2}")
        logger.debug(f"R2: pin1={r2_pin1}, pin2={r2_pin2}")

        # Assert: All pins found
        assert all([r1_pin1, r1_pin2, r2_pin1, r2_pin2]), "All pins should exist"

        # Assert: Pin positions follow expected layout
        # In a voltage divider: VCC → R1 → R2 → GND (vertically)
        assert r1_pin1.x == r1_pin2.x, "R1 pins should have same X (vertical)"
        assert r1_pin1.y < r1_pin2.y, "R1 pin1 should be above pin2"  # Lower Y = higher
        assert r2_pin1.x == r2_pin2.x, "R2 pins should have same X (vertical)"
        assert r2_pin1.y < r2_pin2.y, "R2 pin1 should be above pin2"

        # Assert: R1 pin2 and R2 pin1 are close (they connect)
        connection_distance = math.sqrt(
            (r2_pin1.x - r1_pin2.x)**2 + (r2_pin1.y - r1_pin2.y)**2
        )
        logger.info(f"Distance between R1 pin2 and R2 pin1: {connection_distance:.2f}mm")

        # Distance should be related to component spacing
        expected_spacing = 50.0  # Components are 50mm apart
        assert 40 < connection_distance < 60, \
            f"Connection distance should be near {expected_spacing}mm, got {connection_distance:.2f}mm"

    def test_component_rotation_affects_pin_orientation(self):
        """
        Test: Component rotation changes which pins face which direction.

        Verifies that rotated components have appropriately positioned pins.
        """
        logger.info("Integration test: Rotation affects pin orientation")

        # Test at multiple rotations
        for rotation in [0, 90, 180, 270]:
            logger.info(f"Testing rotation: {rotation}°")

            sch = ksa.create_schematic(f"Rotation {rotation}")
            comp = sch.components.add(
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=(100.0, 100.0),
                rotation=rotation
            )

            pin1 = comp.get_pin_position("1")
            pin2 = comp.get_pin_position("2")

            assert pin1 is not None
            assert pin2 is not None

            # Log pin positions for analysis
            logger.debug(f"Rotation {rotation}°: pin1={pin1}, pin2={pin2}")

            # Assert: Distance between pins remains constant
            distance = math.sqrt((pin2.x - pin1.x)**2 + (pin2.y - pin1.y)**2)
            logger.debug(f"Distance at {rotation}°: {distance:.2f}mm")

            # Resistor pins should always be ~3.81mm apart (standard KiCAD spacing)
            assert 3.0 < distance < 4.0, \
                f"Pin distance should be ~3.81mm, got {distance:.2f}mm at {rotation}°"


class TestPinConnectionErrorHandling:
    """
    Test suite for error conditions and edge cases in workflows.
    """

    def test_invalid_rotation_value(self):
        """
        Test: Invalid rotation value is handled gracefully.

        Error case: Invalid rotation angle
        """
        logger.info("Test: Invalid rotation handling")

        sch = ksa.create_schematic("Rotation Error Test")

        # Most implementations should validate rotation values
        # Expected: Either error or snap to valid value
        try:
            comp = sch.components.add(
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=(100.0, 100.0),
                rotation=45  # Invalid: not 0, 90, 180, or 270
            )
            logger.info(f"Component added with rotation: {comp.rotation}")
            # If no error, rotation might be snapped to nearest valid value
        except (ValueError, TypeError) as e:
            logger.info(f"Rotation validation raised: {type(e).__name__}: {e}")

    def test_component_position_at_grid_boundaries(self):
        """
        Test: Components at grid boundaries have correct pin positions.

        Edge case: Component at grid origin or edge
        """
        logger.info("Test: Pin positions at grid boundaries")

        test_cases = [
            ("Grid Origin", (0.0, 0.0)),
            ("Near Origin", (1.27, 1.27)),
            ("Large Position", (1000.0, 1000.0)),
        ]

        for description, position in test_cases:
            logger.info(f"Testing: {description} at {position}")

            sch = ksa.create_schematic(f"{description} Test")
            comp = sch.components.add(
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=position
            )

            pin1 = comp.get_pin_position("1")
            pin2 = comp.get_pin_position("2")

            assert pin1 is not None, f"Pin 1 should exist at {position}"
            assert pin2 is not None, f"Pin 2 should exist at {position}"

            logger.debug(f"{description}: pin1={pin1}, pin2={pin2}")

    def test_schematic_with_many_components(self):
        """
        Test: Pin position retrieval works with many components.

        Performance/correctness: Multiple components shouldn't interfere.
        """
        logger.info("Test: Pin positions with many components")

        sch = ksa.create_schematic("Many Components Test")

        # Add many components
        num_components = 20
        components = []

        for i in range(num_components):
            comp = sch.components.add(
                lib_id="Device:R",
                reference=f"R{i+1}",
                value="10k",
                position=(100.0 + i * 10.0, 100.0)  # Spread horizontally
            )
            components.append(comp)

        logger.info(f"Added {num_components} components")

        # Act: Get pin positions from all components
        for comp in components:
            pin1 = comp.get_pin_position("1")
            pin2 = comp.get_pin_position("2")

            # Assert: Both pins should exist
            assert pin1 is not None, f"{comp.reference} pin 1 should exist"
            assert pin2 is not None, f"{comp.reference} pin 2 should exist"

        logger.info("Successfully retrieved pins from all components")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
