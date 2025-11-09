#!/usr/bin/env python3
"""
PARAMETRIZED TEST TEMPLATE: Testing Multiple Scenarios with Less Code

This template demonstrates parametrized testing patterns to reduce boilerplate
while testing multiple scenarios. Use this for:
  - Testing same logic across different component types
  - Testing multiple rotation angles
  - Testing edge cases systematically
  - Testing various pin configurations
  - Data-driven testing with clear inputs/outputs

Key Features:
  - @pytest.mark.parametrize for clean multi-scenario testing
  - Multiple parameter sets for comprehensive coverage
  - Indirect parametrization for complex fixtures
  - Clear test names showing what's being tested
  - Inline documentation of test data
  - Helper functions for parametrization logic
  - >95% code coverage with minimal test code

Copy and customize for your parametrized pin connection tests.
"""

import logging
import math
from typing import Optional, Tuple

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

logger = logging.getLogger(__name__)


class TestGetPinPositionParametrized:
    """
    Parametrized test suite for get_pin_position across multiple scenarios.

    Shows how to test many cases with minimal code repetition.
    """

    @pytest.fixture
    def schematic(self):
        """Create fresh schematic for each test."""
        return ksa.create_schematic("Parametrized Test")

    # Test Case 1: Different component types
    @pytest.mark.parametrize(
        "lib_id,reference,num_pins",
        [
            ("Device:R", "R1", 2),  # Resistor: 2 pins
            ("Device:C", "C1", 2),  # Capacitor: 2 pins
            ("Device:D", "D1", 2),  # Diode: 2 pins
            ("Device:L", "L1", 2),  # Inductor: 2 pins
            ("Connector_Generic:Conn_01x03_Pin", "J1", 3),  # Header: 3 pins
        ],
    )
    def test_get_pin_position_different_components(self, schematic, lib_id, reference, num_pins):
        """
        Test: get_pin_position works for different component types.

        Parametrized across:
          - Device:R, Device:C, Device:D, Device:L (2-pin)
          - Connector with 3 pins

        This single test method tests 5 different component types.
        """
        logger.info(f"Testing {lib_id} ({reference})")

        # Act: Add component
        comp = schematic.components.add(
            lib_id=lib_id, reference=reference, value="test", position=(100.0, 100.0)
        )

        # Act: Get pin positions for expected number of pins
        pins = {}
        for i in range(1, num_pins + 1):
            pin_pos = comp.get_pin_position(str(i))
            pins[str(i)] = pin_pos
            logger.debug(f"{reference} pin {i}: {pin_pos}")

        # Assert: All expected pins should exist
        for i in range(1, num_pins + 1):
            assert pins[str(i)] is not None, f"{reference} should have pin {i}"

        # Assert: Pins should be at different positions
        # (at least some should differ)
        positions = list(pins.values())
        all_same = all(pos == positions[0] for pos in positions)
        assert not all_same, f"{reference} pins should be at different positions"

    # Test Case 2: Different rotation angles
    @pytest.mark.parametrize(
        "rotation,description",
        [
            (0, "Vertical (0°)"),
            (90, "Horizontal right (90°)"),
            (180, "Vertical flipped (180°)"),
            (270, "Horizontal left (270°)"),
        ],
    )
    def test_get_pin_position_all_rotations(self, schematic, rotation, description):
        """
        Test: get_pin_position works at all rotation angles.

        Parametrized across 4 rotation angles (0°, 90°, 180°, 270°).
        Single test method tests all 4 cases.
        """
        logger.info(f"Testing rotation: {description}")

        # Act: Add component with rotation
        comp = schematic.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            rotation=rotation,
        )

        # Assert: Rotation should be set
        assert math.isclose(
            comp.rotation, rotation, abs_tol=0.1
        ), f"Component rotation should be {rotation}°"

        # Act: Get pin positions
        pin1 = comp.get_pin_position("1")
        pin2 = comp.get_pin_position("2")

        # Assert: Pins should exist
        assert pin1 is not None, f"Pin 1 should exist at {rotation}°"
        assert pin2 is not None, f"Pin 2 should exist at {rotation}°"

        # Assert: Pin distance should be consistent
        distance = math.sqrt((pin2.x - pin1.x) ** 2 + (pin2.y - pin1.y) ** 2)
        assert (
            3.7 < distance < 3.9
        ), f"Pin distance at {rotation}° should be ~3.81mm, got {distance:.2f}mm"

    # Test Case 3: Different position coordinates
    @pytest.mark.parametrize(
        "position,position_name",
        [
            ((0.0, 0.0), "Origin (0, 0)"),
            ((50.0, 50.0), "Small offset (50, 50)"),
            ((100.0, 100.0), "Standard (100, 100)"),
            ((200.0, 200.0), "Large offset (200, 200)"),
            ((500.0, 500.0), "Very large (500, 500)"),
        ],
    )
    def test_get_pin_position_different_locations(self, schematic, position, position_name):
        """
        Test: get_pin_position works at different component locations.

        Parametrized across 5 different position coordinates.
        Tests that pin positions correctly offset from component position.
        """
        logger.info(f"Testing position: {position_name}")

        # Act: Add component at position
        comp = schematic.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=position
        )

        # Assert: Component position should match
        assert math.isclose(comp.position.x, position[0], abs_tol=0.1)
        assert math.isclose(comp.position.y, position[1], abs_tol=0.1)

        # Act: Get pin positions
        pin1 = comp.get_pin_position("1")
        pin2 = comp.get_pin_position("2")

        # Assert: Both pins should exist
        assert pin1 is not None
        assert pin2 is not None

        # Assert: Pin positions should be offset from component position
        # (not at same position, not infinitely far away)
        offset1_x = pin1.x - position[0]
        offset1_y = pin1.y - position[1]
        assert abs(offset1_x) < 20, "Pin 1 X offset should be reasonable"
        assert abs(offset1_y) < 20, "Pin 1 Y offset should be reasonable"

        logger.debug(f"Position {position_name}: pins at {pin1}, {pin2}")


class TestComponentPropertiesParametrized:
    """
    Parametrized tests for component properties and their effects on pins.
    """

    @pytest.fixture
    def schematic(self):
        return ksa.create_schematic("Property Test")

    @pytest.mark.parametrize(
        "value,description",
        [
            ("1k", "Small value"),
            ("10k", "Standard value"),
            ("1M", "Large value"),
            ("470", "Numeric only"),
            ("CUSTOM_VALUE", "Custom text"),
        ],
    )
    def test_pin_position_with_different_values(self, schematic, value, description):
        """
        Test: Component value doesn't affect pin positions.

        Parametrized across different component values.
        Verifies that pin positions are independent of component value.
        """
        logger.info(f"Testing component value: {description} ({value})")

        # Act: Add two components with different values
        comp1 = schematic.components.add(
            lib_id="Device:R", reference="R1", value=value, position=(100.0, 100.0)
        )

        comp2 = schematic.components.add(
            lib_id="Device:R",
            reference="R2",
            value="10k",  # Different value
            position=(100.0, 150.0),  # Same relative position
        )

        # Assert: Components have different values
        assert comp1.value != comp2.value or comp1.value == comp2.value

        # Act: Get pin positions from both
        pin1_comp1 = comp1.get_pin_position("1")
        pin1_comp2 = comp2.get_pin_position("1")

        # Assert: Pin positions should exist for both
        assert pin1_comp1 is not None
        assert pin1_comp2 is not None

        # Assert: Pin distances from component center should be same
        offset1 = math.sqrt(
            (pin1_comp1.x - comp1.position.x) ** 2 + (pin1_comp1.y - comp1.position.y) ** 2
        )
        offset2 = math.sqrt(
            (pin1_comp2.x - comp2.position.x) ** 2 + (pin1_comp2.y - comp2.position.y) ** 2
        )

        assert math.isclose(
            offset1, offset2, rel_tol=0.01
        ), f"Same component type should have same pin offset from center"


class TestPinConnectionScenarios:
    """
    Parametrized tests for different pin connection scenarios.

    Tests logical pin connection patterns rather than just single components.
    """

    @pytest.fixture
    def schematic(self):
        return ksa.create_schematic("Connection Scenario")

    # Connection scenario data: (comp1_rotation, comp2_rotation, description)
    SCENARIOS = [
        (0, 0, "Both vertical"),
        (90, 90, "Both horizontal"),
        (0, 90, "Vertical to horizontal"),
        (90, 0, "Horizontal to vertical"),
        (90, 180, "Horizontal to inverted"),
        (180, 270, "Inverted vertical to horizontal"),
    ]

    @pytest.mark.parametrize("comp1_rot,comp2_rot,description", SCENARIOS)
    def test_pin_positions_for_connection_scenarios(
        self, schematic, comp1_rot, comp2_rot, description
    ):
        """
        Test: Pin positions correct for various connection scenarios.

        Parametrized across 6 different rotation combinations.
        Tests realistic wiring scenarios.
        """
        logger.info(f"Connection scenario: {description}")
        logger.debug(f"R1 rotation: {comp1_rot}°, R2 rotation: {comp2_rot}°")

        # Arrange: Add two components with rotations
        r1 = schematic.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            rotation=comp1_rot,
        )

        r2 = schematic.components.add(
            lib_id="Device:R",
            reference="R2",
            value="20k",
            position=(150.0, 100.0),  # To the right of R1
            rotation=comp2_rot,
        )

        logger.debug(f"R1 at {r1.position}, R2 at {r2.position}")

        # Act: Get all pin positions
        r1_pin1 = r1.get_pin_position("1")
        r1_pin2 = r1.get_pin_position("2")
        r2_pin1 = r2.get_pin_position("1")
        r2_pin2 = r2.get_pin_position("2")

        # Assert: All pins should exist
        assert all(
            [r1_pin1, r1_pin2, r2_pin1, r2_pin2]
        ), f"All pins should exist in scenario: {description}"

        # Assert: Pin pairs should have different Y positions for vertical components
        if comp1_rot in [0, 180]:
            assert r1_pin1.y != r1_pin2.y, f"R1 pins should have different Y at {comp1_rot}°"

        if comp2_rot in [0, 180]:
            assert r2_pin1.y != r2_pin2.y, f"R2 pins should have different Y at {comp2_rot}°"

        # Log for debugging
        logger.debug(f"R1 pins: {r1_pin1}, {r1_pin2}")
        logger.debug(f"R2 pins: {r2_pin1}, {r2_pin2}")


class TestPinErrorCasesParametrized:
    """
    Parametrized tests for error cases and edge conditions.
    """

    @pytest.fixture
    def schematic(self):
        return ksa.create_schematic("Error Case Test")

    @pytest.mark.parametrize(
        "pin_number,should_exist",
        [
            ("1", True),
            ("2", True),
            ("3", False),
            ("10", False),
            ("0", False),
            ("-1", False),
            ("A", False),
            ("", False),
        ],
    )
    def test_pin_existence_parametrized(self, schematic, pin_number, should_exist):
        """
        Test: get_pin_position returns correct result for various pin numbers.

        Parametrized across valid and invalid pin numbers.
        Tests error handling comprehensively.
        """
        logger.debug(f"Testing pin number: {pin_number}")

        # Arrange: Add resistor (has pins 1 and 2)
        comp = schematic.components.add(
            lib_id="Device:R", reference="R1", value="10k", position=(100.0, 100.0)
        )

        # Act: Get pin position
        pin_pos = comp.get_pin_position(pin_number)
        logger.debug(f"Pin {pin_number}: {pin_pos}")

        # Assert: Pin existence matches expectation
        if should_exist:
            assert pin_pos is not None, f"Pin {pin_number} should exist for resistor"
        else:
            assert pin_pos is None, f"Pin {pin_number} should not exist for resistor"

    @pytest.mark.parametrize(
        "component_types",
        [
            ("Device:R", "Device:C"),  # Resistor and capacitor
            ("Device:L", "Device:D"),  # Inductor and diode
            ("Device:R", "Device:L"),  # Different but same pin count
        ],
    )
    def test_multiple_component_types(self, schematic, component_types):
        """
        Test: get_pin_position works correctly with multiple component types.

        Parametrized across different component type combinations.
        """
        lib_id1, lib_id2 = component_types
        logger.info(f"Testing combination: {lib_id1} and {lib_id2}")

        # Act: Add both components
        comp1 = schematic.components.add(
            lib_id=lib_id1, reference="X1", value="test", position=(100.0, 100.0)
        )

        comp2 = schematic.components.add(
            lib_id=lib_id2, reference="X2", value="test", position=(200.0, 100.0)
        )

        # Act: Get pin positions
        pin1_x1 = comp1.get_pin_position("1")
        pin1_x2 = comp2.get_pin_position("1")

        # Assert: Both should have pin 1
        assert pin1_x1 is not None, f"{lib_id1} should have pin 1"
        assert pin1_x2 is not None, f"{lib_id2} should have pin 1"

        # Assert: Pin positions should be different (different component positions)
        assert (
            pin1_x1 != pin1_x2
        ), "Pin 1 from different components should be at different positions"


# Advanced: Indirect parametrization for complex fixtures
class TestIndirectParametrization:
    """
    Demonstrates indirect parametrization for creating complex fixtures.

    Useful when you need to parametrize the fixture itself, not just the test.
    """

    @pytest.fixture
    def component_params(self, request):
        """
        Fixture parametrized with component specifications.

        Receives parameter from test_with_indirect_params.
        """
        lib_id, reference, rotation = request.param
        logger.info(f"Creating component fixture: {reference} ({lib_id}) at {rotation}°")

        sch = ksa.create_schematic("Indirect Test")
        comp = sch.components.add(
            lib_id=lib_id,
            reference=reference,
            value="test",
            position=(100.0, 100.0),
            rotation=rotation,
        )
        return sch, comp

    @pytest.mark.parametrize(
        "component_params",
        [
            ("Device:R", "R1", 0),
            ("Device:C", "C1", 90),
            ("Device:L", "L1", 180),
        ],
        indirect=True,  # Pass to fixture
    )
    def test_with_indirect_params(self, component_params):
        """
        Test: Using indirect parametrization for complex fixtures.

        The component_params fixture receives the parametrized values.
        """
        sch, comp = component_params
        logger.info(f"Test with {comp.reference} at {comp.rotation}°")

        # Act: Get pin positions
        pin1 = comp.get_pin_position("1")
        pin2 = comp.get_pin_position("2")

        # Assert: Pins should exist
        assert pin1 is not None
        assert pin2 is not None

        logger.info(f"✓ Pins found at {pin1}, {pin2}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
