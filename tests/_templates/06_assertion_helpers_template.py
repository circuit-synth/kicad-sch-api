#!/usr/bin/env python3
"""
ASSERTION HELPERS TEMPLATE: Custom Assertions for Pin/Wire Testing

This template demonstrates creating reusable assertion helper functions for
pin connection testing. Use this to:
  - Reduce assertion boilerplate
  - Create domain-specific assertions
  - Improve test readability
  - Consolidate validation logic
  - Provide detailed failure messages
  - Enable assertion chaining

Key Features:
  - Custom assertion functions with clear names
  - Detailed error messages for debugging
  - Tolerance handling for floating-point comparisons
  - Multiple assertion styles (single condition, compound checks)
  - Logging to understand assertion failures
  - Type hints for clarity
  - Examples of assertion patterns
  - Common pin/wire checks pre-built

Can be used in conftest.py for project-wide availability,
or imported directly into test modules.

Copy and customize for your assertion needs.
"""

import logging
import math
from typing import Optional, Tuple, List, Callable

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.core.types import Point

logger = logging.getLogger(__name__)


# ============================================================================
# PIN POSITION ASSERTIONS
# ============================================================================

def assert_pin_exists(component, pin_number: str, message: str = ""):
    """
    Assert that a component has a given pin.

    Args:
        component: Component object
        pin_number: Pin number as string (e.g., "1", "2")
        message: Optional custom error message

    Raises:
        AssertionError: If pin doesn't exist

    Example:
        assert_pin_exists(r1, "1")
        assert_pin_exists(ic, "8", "IC should have pin 8")
    """
    logger.debug(f"Checking if {component.reference} has pin {pin_number}")

    pin_pos = component.get_pin_position(pin_number)

    if pin_pos is None:
        error_msg = message or f"{component.reference} should have pin {pin_number}"
        pytest.fail(error_msg)

    logger.debug(f"✓ Pin {pin_number} exists at {pin_pos}")
    return pin_pos


def assert_pin_not_exists(component, pin_number: str, message: str = ""):
    """
    Assert that a component does NOT have a given pin.

    Args:
        component: Component object
        pin_number: Pin number as string
        message: Optional custom error message

    Example:
        assert_pin_not_exists(r1, "99")  # Resistor has no pin 99
    """
    logger.debug(f"Checking if {component.reference} doesn't have pin {pin_number}")

    pin_pos = component.get_pin_position(pin_number)

    if pin_pos is not None:
        error_msg = message or f"{component.reference} should NOT have pin {pin_number}"
        pytest.fail(error_msg)

    logger.debug(f"✓ Pin {pin_number} correctly doesn't exist")


def assert_pin_position(
    component,
    pin_number: str,
    expected_x: float,
    expected_y: float,
    tolerance: float = 0.05,
    message: str = ""
):
    """
    Assert that a pin is at an expected position.

    Args:
        component: Component object
        pin_number: Pin number as string
        expected_x: Expected X coordinate
        expected_y: Expected Y coordinate
        tolerance: Maximum allowed difference (absolute tolerance, mm)
        message: Optional custom error message

    Raises:
        AssertionError: If pin position doesn't match

    Example:
        # Test pin 1 is at exactly (100.0, 104.14) ±0.05mm
        assert_pin_position(r1, "1", 100.0, 104.14, tolerance=0.05)
    """
    logger.debug(
        f"Checking {component.reference} pin {pin_number} at ({expected_x}, {expected_y})"
    )

    pin_pos = component.get_pin_position(pin_number)

    if pin_pos is None:
        error_msg = message or f"{component.reference} pin {pin_number} not found"
        pytest.fail(error_msg)

    # Check X coordinate
    if not math.isclose(pin_pos.x, expected_x, abs_tol=tolerance):
        error_msg = (
            message or
            f"{component.reference} pin {pin_number} X mismatch: "
            f"{pin_pos.x:.3f} vs expected {expected_x:.3f} (diff: {abs(pin_pos.x - expected_x):.3f})"
        )
        pytest.fail(error_msg)

    # Check Y coordinate
    if not math.isclose(pin_pos.y, expected_y, abs_tol=tolerance):
        error_msg = (
            message or
            f"{component.reference} pin {pin_number} Y mismatch: "
            f"{pin_pos.y:.3f} vs expected {expected_y:.3f} (diff: {abs(pin_pos.y - expected_y):.3f})"
        )
        pytest.fail(error_msg)

    logger.debug(f"✓ Pin {pin_number} at ({pin_pos.x:.3f}, {pin_pos.y:.3f})")


def assert_pins_at_positions(
    component,
    expected_positions: dict,
    tolerance: float = 0.05
):
    """
    Assert multiple pins are at expected positions in one call.

    Args:
        component: Component object
        expected_positions: Dict mapping pin number -> (x, y) tuple
        tolerance: Maximum allowed difference

    Example:
        # Check both pins of resistor
        assert_pins_at_positions(r1, {
            "1": (100.0, 104.14),
            "2": (100.0, 96.52),
        })
    """
    logger.debug(f"Checking {len(expected_positions)} pins for {component.reference}")

    for pin_number, (expected_x, expected_y) in expected_positions.items():
        assert_pin_position(component, pin_number, expected_x, expected_y, tolerance)

    logger.debug(f"✓ All {len(expected_positions)} pins match positions")


def assert_pins_differ(component1, component2, pin_number: str = "1"):
    """
    Assert that same pin number on different components are at different positions.

    Args:
        component1: First component
        component2: Second component
        pin_number: Pin number to compare

    Example:
        # Two resistors at different positions should have different pin 1 positions
        assert_pins_differ(r1, r2, "1")
    """
    logger.debug(f"Checking if pin {pin_number} differs between components")

    pin1 = component1.get_pin_position(pin_number)
    pin2 = component2.get_pin_position(pin_number)

    if pin1 is None or pin2 is None:
        pytest.fail("Both components must have the pin to compare")

    if pin1 == pin2:
        pytest.fail(
            f"{component1.reference} and {component2.reference} should have "
            f"different pin {pin_number} positions, but both are at {pin1}"
        )

    logger.debug(f"✓ Pins differ: {pin1} vs {pin2}")


# ============================================================================
# PIN SPACING AND DISTANCE ASSERTIONS
# ============================================================================

def assert_pin_distance(
    component,
    pin1_number: str,
    pin2_number: str,
    expected_distance: float,
    tolerance: float = 0.1,
    message: str = ""
):
    """
    Assert that two pins are at expected distance from each other.

    Args:
        component: Component object
        pin1_number: First pin number
        pin2_number: Second pin number
        expected_distance: Expected distance in mm
        tolerance: Maximum allowed difference in distance
        message: Optional custom error message

    Example:
        # Resistor pins should be 3.81mm apart
        assert_pin_distance(r1, "1", "2", 3.81, tolerance=0.1)
    """
    logger.debug(
        f"Checking distance between {component.reference} pins "
        f"{pin1_number} and {pin2_number}"
    )

    pin1 = component.get_pin_position(pin1_number)
    pin2 = component.get_pin_position(pin2_number)

    if pin1 is None or pin2 is None:
        pytest.fail(f"Both pins must exist to measure distance")

    actual_distance = math.sqrt((pin2.x - pin1.x)**2 + (pin2.y - pin1.y)**2)

    if not math.isclose(actual_distance, expected_distance, abs_tol=tolerance):
        error_msg = (
            message or
            f"{component.reference} pins {pin1_number}-{pin2_number} distance mismatch: "
            f"{actual_distance:.3f}mm vs expected {expected_distance:.3f}mm "
            f"(diff: {abs(actual_distance - expected_distance):.3f}mm)"
        )
        pytest.fail(error_msg)

    logger.debug(f"✓ Distance: {actual_distance:.3f}mm")


def assert_pin_distance_consistent(components: List, pin1: str, pin2: str):
    """
    Assert that pin spacing is consistent across multiple components.

    Useful for verifying that all resistors have same pin spacing regardless
    of position or rotation.

    Args:
        components: List of components to check
        pin1: First pin number
        pin2: Second pin number

    Example:
        # All resistors should have same pin spacing
        assert_pin_distance_consistent([r1, r2, r3], "1", "2")
    """
    logger.debug(f"Checking consistent spacing for {len(components)} components")

    if not components:
        pytest.fail("Need at least one component")

    distances = []

    for comp in components:
        pin1_pos = comp.get_pin_position(pin1)
        pin2_pos = comp.get_pin_position(pin2)

        if pin1_pos is None or pin2_pos is None:
            pytest.fail(f"{comp.reference} missing pins {pin1} or {pin2}")

        distance = math.sqrt((pin2_pos.x - pin1_pos.x)**2 + (pin2_pos.y - pin1_pos.y)**2)
        distances.append(distance)
        logger.debug(f"{comp.reference}: {distance:.3f}mm")

    # All distances should be close to each other
    first_distance = distances[0]
    for i, distance in enumerate(distances[1:], 1):
        if not math.isclose(distance, first_distance, rel_tol=0.01):
            pytest.fail(
                f"Component {i} has different pin spacing: "
                f"{distance:.3f}mm vs {first_distance:.3f}mm"
            )

    logger.debug(f"✓ All {len(components)} components have consistent spacing")


# ============================================================================
# PIN ORIENTATION ASSERTIONS
# ============================================================================

def assert_pins_vertical(
    component,
    pin1_number: str,
    pin2_number: str,
    tolerance: float = 0.1,
    message: str = ""
):
    """
    Assert that two pins are vertically aligned (same X coordinate).

    Useful for verifying components at 0° or 180° rotation.

    Args:
        component: Component object
        pin1_number: First pin number
        pin2_number: Second pin number
        tolerance: Maximum X difference allowed
        message: Optional custom error message

    Example:
        # At 0° rotation, resistor pins should be vertically aligned
        assert_pins_vertical(r1, "1", "2")
    """
    logger.debug(f"Checking if {component.reference} pins are vertical")

    pin1 = component.get_pin_position(pin1_number)
    pin2 = component.get_pin_position(pin2_number)

    if pin1 is None or pin2 is None:
        pytest.fail("Both pins must exist")

    if not math.isclose(pin1.x, pin2.x, abs_tol=tolerance):
        error_msg = (
            message or
            f"{component.reference} pins {pin1_number}-{pin2_number} should be vertical "
            f"(same X), but X differs: {pin1.x:.3f} vs {pin2.x:.3f}"
        )
        pytest.fail(error_msg)

    logger.debug(f"✓ Pins are vertical: both at X={pin1.x:.3f}")


def assert_pins_horizontal(
    component,
    pin1_number: str,
    pin2_number: str,
    tolerance: float = 0.1,
    message: str = ""
):
    """
    Assert that two pins are horizontally aligned (same Y coordinate).

    Useful for verifying components at 90° or 270° rotation.

    Args:
        component: Component object
        pin1_number: First pin number
        pin2_number: Second pin number
        tolerance: Maximum Y difference allowed
        message: Optional custom error message

    Example:
        # At 90° rotation, resistor pins should be horizontally aligned
        assert_pins_horizontal(r1, "1", "2")
    """
    logger.debug(f"Checking if {component.reference} pins are horizontal")

    pin1 = component.get_pin_position(pin1_number)
    pin2 = component.get_pin_position(pin2_number)

    if pin1 is None or pin2 is None:
        pytest.fail("Both pins must exist")

    if not math.isclose(pin1.y, pin2.y, abs_tol=tolerance):
        error_msg = (
            message or
            f"{component.reference} pins {pin1_number}-{pin2_number} should be horizontal "
            f"(same Y), but Y differs: {pin1.y:.3f} vs {pin2.y:.3f}"
        )
        pytest.fail(error_msg)

    logger.debug(f"✓ Pins are horizontal: both at Y={pin1.y:.3f}")


# ============================================================================
# WIRE-TO-PIN ASSERTIONS
# ============================================================================

def assert_wire_endpoint_at_pin(
    wire,
    component,
    pin_number: str,
    endpoint_index: int = 0,
    tolerance: float = 0.05
):
    """
    Assert that a wire endpoint is at a component's pin position.

    Args:
        wire: Wire object with points
        component: Component object
        pin_number: Pin number
        endpoint_index: Which endpoint of wire (0 or 1 for 2-point wire)
        tolerance: Maximum allowed distance

    Example:
        # Wire should start at R1 pin 1
        assert_wire_endpoint_at_pin(wire, r1, "1", endpoint_index=0)
    """
    logger.debug(f"Checking wire endpoint at {component.reference} pin {pin_number}")

    if endpoint_index >= len(wire.points):
        pytest.fail(f"Wire doesn't have endpoint {endpoint_index}")

    endpoint = wire.points[endpoint_index]
    pin_pos = component.get_pin_position(pin_number)

    if pin_pos is None:
        pytest.fail(f"{component.reference} pin {pin_number} not found")

    # Check if endpoint matches pin position
    distance = math.sqrt((endpoint.x - pin_pos.x)**2 + (endpoint.y - pin_pos.y)**2)

    if distance > tolerance:
        pytest.fail(
            f"Wire endpoint {endpoint_index} not at {component.reference} pin {pin_number}: "
            f"({endpoint.x:.3f}, {endpoint.y:.3f}) vs ({pin_pos.x:.3f}, {pin_pos.y:.3f}) "
            f"distance: {distance:.3f}mm"
        )

    logger.debug(f"✓ Wire endpoint at pin: distance {distance:.3f}mm")


def assert_wires_form_connection(
    schematic,
    component1,
    pin1_number: str,
    component2,
    pin2_number: str,
    message: str = ""
):
    """
    Assert that a wire connects two component pins.

    Args:
        schematic: Schematic containing wires
        component1: First component
        pin1_number: First component's pin
        component2: Second component
        pin2_number: Second component's pin
        message: Optional custom error message

    Example:
        # Check if R1 pin 2 and R2 pin 1 are connected by wire
        assert_wires_form_connection(sch, r1, "2", r2, "1")
    """
    logger.debug(f"Checking wire connects {component1.reference} pin {pin1_number} "
                 f"to {component2.reference} pin {pin2_number}")

    pin1_pos = component1.get_pin_position(pin1_number)
    pin2_pos = component2.get_pin_position(pin2_number)

    if pin1_pos is None or pin2_pos is None:
        pytest.fail("Both pins must exist")

    # Check each wire
    found = False
    for wire in schematic.wires:
        # Check if wire endpoints match the pin positions
        endpoints = [(p.x, p.y) for p in wire.points]

        if len(endpoints) >= 2:
            # Check both directions
            if ((math.isclose(endpoints[0][0], pin1_pos.x, abs_tol=0.05) and
                 math.isclose(endpoints[0][1], pin1_pos.y, abs_tol=0.05) and
                 math.isclose(endpoints[1][0], pin2_pos.x, abs_tol=0.05) and
                 math.isclose(endpoints[1][1], pin2_pos.y, abs_tol=0.05)) or
                (math.isclose(endpoints[0][0], pin2_pos.x, abs_tol=0.05) and
                 math.isclose(endpoints[0][1], pin2_pos.y, abs_tol=0.05) and
                 math.isclose(endpoints[1][0], pin1_pos.x, abs_tol=0.05) and
                 math.isclose(endpoints[1][1], pin1_pos.y, abs_tol=0.05))):
                found = True
                break

    if not found:
        error_msg = (
            message or
            f"No wire found connecting {component1.reference} pin {pin1_number} "
            f"to {component2.reference} pin {pin2_number}"
        )
        pytest.fail(error_msg)

    logger.debug(f"✓ Wire connects pins")


# ============================================================================
# ASSERTION TEST EXAMPLES
# ============================================================================

class TestAssertionHelpers:
    """Examples of using custom assertion helpers."""

    @pytest.fixture
    def test_schematic(self):
        """Create test schematic with components."""
        sch = ksa.create_schematic("Assertion Test")

        r1 = sch.components.add(
            lib_id="Device:R",
            reference="R1",
            value="10k",
            position=(100.0, 100.0),
            rotation=0
        )

        r2 = sch.components.add(
            lib_id="Device:R",
            reference="R2",
            value="20k",
            position=(150.0, 100.0),
            rotation=90
        )

        return sch

    def test_using_pin_exists_assertion(self, test_schematic):
        """Example: Using assert_pin_exists."""
        r1 = test_schematic.components.get("R1")

        # These should pass
        assert_pin_exists(r1, "1")
        assert_pin_exists(r1, "2")

        # This should fail (resistor has no pin 3)
        with pytest.raises(AssertionError):
            assert_pin_exists(r1, "3")

    def test_using_pin_position_assertion(self, test_schematic):
        """Example: Using assert_pin_position."""
        r1 = test_schematic.components.get("R1")

        # Get actual position first
        pin1 = r1.get_pin_position("1")

        # Assert position (with tolerance)
        assert_pin_position(r1, "1", pin1.x, pin1.y, tolerance=0.1)

    def test_using_distance_assertion(self, test_schematic):
        """Example: Using assert_pin_distance."""
        r1 = test_schematic.components.get("R1")

        # Check pin spacing
        assert_pin_distance(r1, "1", "2", 3.81, tolerance=0.1)

    def test_using_orientation_assertion(self, test_schematic):
        """Example: Using orientation assertions."""
        r1 = test_schematic.components.get("R1")
        r2 = test_schematic.components.get("R2")

        # R1 at 0° should be vertical
        assert_pins_vertical(r1, "1", "2")

        # R2 at 90° should be horizontal
        assert_pins_horizontal(r2, "1", "2")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
