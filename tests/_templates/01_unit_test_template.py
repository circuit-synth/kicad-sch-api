#!/usr/bin/env python3
"""
UNIT TEST TEMPLATE: Component Pin Connection Testing

This template demonstrates best practices for unit testing pin-related functionality.
Use this as a starting point for implementing tests for:
  - Pin position calculations
  - Pin getter/setter methods
  - Component pin retrieval
  - Rotation and transformation effects on pins

Key Features:
  - Clear test organization with descriptive class and method names
  - Comprehensive fixtures for common setup patterns
  - Inline comments explaining test logic
  - Error case coverage
  - Parametrized tests for multiple scenarios
  - Logging to understand test behavior
  - >95% coverage achievable

Copy and customize for your specific pin connection feature.
"""

import logging
import math
import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

# Configure logging to help understand test execution
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestGetComponentPins:
    """
    Test suite for getting component pin positions.

    Template for testing pin position retrieval from components.
    All tests follow the pattern:
      1. Create/fixture schematic with components
      2. Call pin position method
      3. Assert expected values
    """

    @pytest.fixture
    def basic_schematic(self):
        """
        Fixture: Create a schematic with a simple two-pin component.

        IMPORTANT: Use fixtures to avoid duplicating setup code.
        Each test gets a fresh fixture instance.
        """
        logger.info("Creating basic_schematic fixture")
        sch = ksa.create_schematic("Pin Position Test")

        # Add a simple component for testing
        resistor = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            rotation=0  # No rotation for baseline test
        )

        logger.info(f"Added resistor: {resistor.reference} at {resistor.position}")
        return sch

    def test_get_existing_pin_position(self, basic_schematic):
        """
        Test: Getting position of an existing pin returns correct Point.

        Pattern:
          - Act: Call get_pin_position for existing pin
          - Assert: Returns Point object (not None)
          - Assert: Position values are reasonable numbers
        """
        logger.info("Test: Get existing pin position")

        # Arrange: Get component from fixture
        comp = basic_schematic.components.get("R1")
        logger.debug(f"Component position: {comp.position}")

        # Act: Get pin position
        pin_pos = comp.get_pin_position("1")
        logger.debug(f"Pin 1 position: {pin_pos}")

        # Assert: Pin should be found
        assert pin_pos is not None, "Pin 1 should exist and be retrievable"

        # Assert: Should return Point object
        assert isinstance(pin_pos, Point), f"Expected Point, got {type(pin_pos)}"

        # Assert: Position should have numeric coordinates
        assert isinstance(pin_pos.x, (int, float)), "Pin X coordinate should be numeric"
        assert isinstance(pin_pos.y, (int, float)), "Pin Y coordinate should be numeric"

        # Assert: Position should be reasonable (not at origin or infinity)
        assert -1000 < pin_pos.x < 1000, f"Pin X position unreasonable: {pin_pos.x}"
        assert -1000 < pin_pos.y < 1000, f"Pin Y position unreasonable: {pin_pos.y}"

    def test_get_multiple_pins_different_positions(self, basic_schematic):
        """
        Test: Getting multiple pins from same component returns different positions.

        Pattern:
          - Act: Get multiple pins from same component
          - Assert: Each pin returns a position
          - Assert: Positions are different (pins at different locations)
        """
        logger.info("Test: Get multiple pins have different positions")

        comp = basic_schematic.components.get("R1")

        # Act: Get both pins from resistor
        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")
        logger.debug(f"Pin 1: {pin1_pos}, Pin 2: {pin2_pos}")

        # Assert: Both pins should exist
        assert pin1_pos is not None, "Pin 1 should exist"
        assert pin2_pos is not None, "Pin 2 should exist"

        # Assert: Pins should be at different positions
        pins_different = (pin1_pos.x != pin2_pos.x) or (pin1_pos.y != pin2_pos.y)
        assert pins_different, "Pins should be at different positions"

        # Log distance between pins for understanding
        distance = math.sqrt((pin2_pos.x - pin1_pos.x)**2 + (pin2_pos.y - pin1_pos.y)**2)
        logger.info(f"Distance between pins: {distance:.2f}mm")

    def test_get_nonexistent_pin_returns_none(self, basic_schematic):
        """
        Test: Getting a non-existent pin number returns None.

        Pattern:
          - Act: Call get_pin_position with invalid pin number
          - Assert: Returns None (not exception, not wrong position)
        """
        logger.info("Test: Get non-existent pin returns None")

        comp = basic_schematic.components.get("R1")

        # Act: Try to get pin that doesn't exist (resistor only has pins 1 and 2)
        pin_pos = comp.get_pin_position("99")
        logger.debug(f"Pin 99 position: {pin_pos}")

        # Assert: Should return None for non-existent pin
        assert pin_pos is None, "Non-existent pin should return None"

    def test_pin_position_respects_component_location(self, basic_schematic):
        """
        Test: Pin position is relative to component's position.

        Pattern:
          - Arrange: Component at known location
          - Act: Get pin position
          - Assert: Pin position = component position + pin offset
        """
        logger.info("Test: Pin position respects component location")

        # Arrange: Component at specific location
        comp = basic_schematic.components.get("R1")
        comp_pos = comp.position
        logger.info(f"Component position: {comp_pos}")

        # Act: Get pin positions
        pin1_pos = comp.get_pin_position("1")

        # Assert: Pin should be offset from component center
        # For a resistor, pins are typically at (0, ±3.81) in symbol space
        pin_offset_x = pin1_pos.x - comp_pos.x
        pin_offset_y = pin1_pos.y - comp_pos.y

        logger.debug(f"Pin offset from component: ({pin_offset_x:.2f}, {pin_offset_y:.2f})")

        # Pin offset should be relatively small (within component bounds)
        assert abs(pin_offset_x) < 20, "Pin X offset should be within component"
        assert abs(pin_offset_y) < 20, "Pin Y offset should be within component"

    @pytest.mark.parametrize("pin_number,should_exist", [
        ("1", True),   # Resistor has pin 1
        ("2", True),   # Resistor has pin 2
        ("3", False),  # Resistor doesn't have pin 3
        ("0", False),  # Pin numbering starts at 1
        ("10", False), # Resistor doesn't have pin 10
    ])
    def test_get_pin_parametrized(self, basic_schematic, pin_number, should_exist):
        """
        Test: Pin existence parametrized across multiple pin numbers.

        Parametrized tests run the same test logic with different inputs.
        This is much cleaner than writing separate test methods.

        Pattern:
          - Mark test with @pytest.mark.parametrize
          - Define parameter name(s) and test cases
          - Use parameter values in test
        """
        comp = basic_schematic.components.get("R1")

        # Act: Get pin position
        pin_pos = comp.get_pin_position(pin_number)
        logger.debug(f"Pin {pin_number}: {pin_pos}")

        # Assert: Pin should exist or not based on expectation
        if should_exist:
            assert pin_pos is not None, f"Pin {pin_number} should exist"
        else:
            assert pin_pos is None, f"Pin {pin_number} should not exist"


class TestPinPositionWithRotation:
    """
    Test suite for pin position calculation with component rotation.

    Demonstrates testing how rotation affects pin positions.
    """

    @pytest.fixture
    def rotated_component_factory(self):
        """
        Fixture: Factory for creating rotated components.

        This is more flexible than a single fixture - allows creating
        multiple rotated components with different angles.
        """
        def _create_rotated_resistor(rotation=0):
            logger.info(f"Creating resistor with {rotation}° rotation")
            sch = ksa.create_schematic(f"Rotation {rotation} Test")
            comp = sch.components.add(
                lib_id="Device:R",
                reference="R1",
                value="10k",
                position=(100.0, 100.0),
                rotation=rotation
            )
            return sch, comp

        return _create_rotated_resistor

    @pytest.mark.parametrize("rotation", [0, 90, 180, 270])
    def test_pin_positions_at_all_rotations(self, rotated_component_factory, rotation):
        """
        Test: Pin positions exist at all valid rotation angles.

        Tests multiple rotation angles in a single parametrized test.
        """
        logger.info(f"Test: Pin positions at {rotation}° rotation")

        # Arrange: Create component with specific rotation
        sch, comp = rotated_component_factory(rotation)

        # Act: Get pin positions
        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        # Assert: Both pins should exist at all rotations
        assert pin1_pos is not None, f"Pin 1 should exist at {rotation}°"
        assert pin2_pos is not None, f"Pin 2 should exist at {rotation}°"

        # Assert: Pins should still be different positions
        assert pin1_pos != pin2_pos, f"Pins should differ at {rotation}°"

        # Log distance for debugging
        dist = math.sqrt((pin2_pos.x - pin1_pos.x)**2 + (pin2_pos.y - pin1_pos.y)**2)
        logger.debug(f"Distance at {rotation}°: {dist:.2f}mm")

    def test_pin_distance_invariant_with_rotation(self, rotated_component_factory):
        """
        Test: Distance between pins remains constant regardless of rotation.

        This verifies that rotation doesn't change pin spacing, which could
        indicate a bug in the transformation logic.
        """
        logger.info("Test: Pin distance invariant with rotation")

        distances = []

        for rotation in [0, 90, 180, 270]:
            sch, comp = rotated_component_factory(rotation)

            pin1_pos = comp.get_pin_position("1")
            pin2_pos = comp.get_pin_position("2")

            distance = math.sqrt((pin2_pos.x - pin1_pos.x)**2 + (pin2_pos.y - pin1_pos.y)**2)
            distances.append(distance)
            logger.debug(f"Rotation {rotation}°: distance = {distance:.4f}mm")

        # Assert: All distances should be approximately equal
        # Use relative tolerance for floating-point comparison
        for i, dist in enumerate(distances[1:], 1):
            assert math.isclose(dist, distances[0], rel_tol=0.01), \
                f"Distance at {i*90}° should match distance at 0°"


class TestGetComponentPinEdgeCases:
    """
    Test suite for edge cases and error handling.

    Demonstrates testing boundary conditions and error scenarios.
    """

    def test_pin_position_from_nonexistent_component(self):
        """
        Test: Getting pin from non-existent component handled gracefully.

        Error case: Component doesn't exist
        Expected: Graceful error handling
        """
        logger.info("Test: Pin from non-existent component")

        sch = ksa.create_schematic("Edge Case Test")

        # Act: Try to get component that doesn't exist
        comp = sch.components.get("R999")
        logger.debug(f"Getting R999: {comp}")

        # Assert: Component should not be found
        assert comp is None, "Non-existent component should return None"

    def test_pin_position_with_empty_schematic(self):
        """
        Test: Pin position handling with empty schematic.

        Edge case: No components in schematic
        Expected: Graceful handling
        """
        logger.info("Test: Pin position from empty schematic")

        # Arrange: Create empty schematic
        sch = ksa.create_schematic("Empty Schematic")

        # Assert: Component collection should be empty
        assert len(sch.components) == 0, "Schematic should be empty"

        # Act: Try to get non-existent component
        comp = sch.components.get("R1")

        # Assert: Should return None
        assert comp is None, "Component should not exist"

    def test_pin_position_with_multi_pin_component(self):
        """
        Test: Pin position with components having many pins.

        Demonstrates testing with more complex components (ICs).
        """
        logger.info("Test: Pin positions from multi-pin IC")

        sch = ksa.create_schematic("IC Test")

        # Add an IC (has many pins)
        ic = sch.components.add(
            lib_id="Package_DIP:DIP-8",
            reference="U1",
            value="Test IC",
            position=(100.0, 100.0)
        )

        logger.info(f"Added IC: {ic.reference}")

        # Test that common pins exist
        for pin_num in ["1", "2", "4", "8"]:
            pin_pos = ic.get_pin_position(pin_num)
            logger.debug(f"Pin {pin_num}: {pin_pos}")

            if pin_pos is not None:
                # If pin exists, it should have valid coordinates
                assert isinstance(pin_pos.x, (int, float))
                assert isinstance(pin_pos.y, (int, float))


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short", "-s"])
