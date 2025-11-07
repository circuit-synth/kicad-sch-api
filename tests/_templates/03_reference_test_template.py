#!/usr/bin/env python3
"""
REFERENCE TEST TEMPLATE: Testing Against Real KiCAD Schematics

This template demonstrates testing your pin connection implementation against
real KiCAD reference schematics manually created in KiCAD.

Use this for testing:
  - Exact KiCAD format compatibility
  - Pin positions matching real KiCAD calculations
  - Rotation transformations against reference data
  - Wire endpoints connected to correct pins
  - Schematic persistence and format preservation

Key Features:
  - Load manually created KiCAD reference schematics
  - Extract exact values from reference files
  - Compare implementation against real KiCAD behavior
  - Clear documentation of expected values
  - Helper methods for common operations
  - Detailed logging of discrepancies
  - Comments explaining where reference values come from

Workflow to create reference tests:
  1. Create blank schematic with: `sch = ksa.create_schematic("Reference"); sch.save(...)`
  2. Open in KiCAD and manually add/arrange elements
  3. Save in KiCAD and open the file
  4. Extract exact values from S-expressions (coordinates, properties)
  5. Use those exact values in your tests

Copy and customize for your pin connection reference schematics.
"""

import logging
import math
import os

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.library.cache import get_symbol_cache

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TestPinPositionAgainstReferences:
    """
    Test suite comparing pin position calculations to reference KiCAD schematics.

    For each reference schematic:
      1. It was manually created and saved by a human in KiCAD
      2. Pin positions are extracted from KiCAD's saved coordinates
      3. Our implementation must calculate the exact same positions

    This ensures our pin calculation is 100% compatible with KiCAD.
    """

    REFERENCE_PROJECTS_PATH = "tests/reference_kicad_projects"

    @staticmethod
    def get_component_by_reference(sch, reference):
        """
        Helper: Get component from schematic and ensure pins are loaded.

        When loading a KiCAD file, symbol pins may need to be loaded from
        the symbol library. This helper handles that.
        """
        logger.debug(f"Looking for component: {reference}")

        for comp in sch.components:
            if comp.reference == reference:
                logger.debug(f"Found component {reference}: {comp}")

                # If pins aren't populated, load from symbol library
                if not comp.pins or len(comp.pins) == 0:
                    logger.debug(f"Loading pins from library for {reference}")
                    cache = get_symbol_cache()
                    symbol_def = cache.get_symbol(comp.lib_id)

                    if symbol_def and symbol_def.pins:
                        comp._data.pins = symbol_def.pins.copy()
                        logger.debug(f"Loaded {len(comp.pins)} pins for {reference}")

                return comp

        logger.warning(f"Component {reference} not found in schematic")
        return None

    def test_pin_position_0_degree_rotation_reference(self):
        """
        Test: Pin positions at 0° rotation match KiCAD reference file.

        Reference Setup:
          - Created blank schematic
          - Added Device:R component at position (96.52, 100.33)
          - Rotated 0° (default vertical orientation)
          - Saved and extracted wire endpoint coordinates

        Expected Values (from KiCAD reference file):
          - Component position: (96.52, 100.33)
          - Pin 1 (top): (96.52, 104.14) - derived from wire endpoint
          - Pin 2 (bottom): (96.52, 96.52) - derived from wire endpoint

        These values are in schematic space (inverted Y-axis).
        """
        logger.info("Reference test: Pin position at 0° rotation")

        # Reference file path
        ref_path = os.path.join(
            self.REFERENCE_PROJECTS_PATH,
            "pin_rotation_0deg",
            "pin_rotation_0deg.kicad_sch"
        )

        logger.info(f"Loading reference schematic: {ref_path}")

        # Assert reference file exists
        if not os.path.exists(ref_path):
            pytest.skip(f"Reference file not found: {ref_path}")

        # Act: Load reference schematic
        sch = ksa.Schematic.load(ref_path)
        logger.info(f"Loaded schematic with {len(sch.components)} components")

        # Act: Get component from reference
        comp = self.get_component_by_reference(sch, "R1")

        # Assert: Component should be found
        assert comp is not None, "R1 component should exist in reference"
        logger.info(f"Component R1: position={comp.position}, rotation={comp.rotation}")

        # Assert: Component should be at correct rotation
        assert comp.rotation == 0.0, f"Expected 0° rotation, got {comp.rotation}°"

        # Act: Get calculated pin positions
        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        logger.info(f"Calculated pin positions: pin1={pin1_pos}, pin2={pin2_pos}")

        # Assert: Both pins should be found
        assert pin1_pos is not None, "Pin 1 should be calculated"
        assert pin2_pos is not None, "Pin 2 should be calculated"

        # Expected coordinates extracted from reference KiCAD file
        # These are exact wire endpoint coordinates from KiCAD
        EXPECTED_PIN1_X = 96.52
        EXPECTED_PIN1_Y = 104.14
        EXPECTED_PIN2_X = 96.52
        EXPECTED_PIN2_Y = 96.52

        # Tolerance: ±0.05mm (grid precision)
        TOLERANCE = 0.05

        # Assert: Pin positions match reference exactly
        assert math.isclose(pin1_pos.x, EXPECTED_PIN1_X, abs_tol=TOLERANCE), \
            f"Pin 1 X mismatch: calculated={pin1_pos.x:.2f}, expected={EXPECTED_PIN1_X}"

        assert math.isclose(pin1_pos.y, EXPECTED_PIN1_Y, abs_tol=TOLERANCE), \
            f"Pin 1 Y mismatch: calculated={pin1_pos.y:.2f}, expected={EXPECTED_PIN1_Y}"

        assert math.isclose(pin2_pos.x, EXPECTED_PIN2_X, abs_tol=TOLERANCE), \
            f"Pin 2 X mismatch: calculated={pin2_pos.x:.2f}, expected={EXPECTED_PIN2_X}"

        assert math.isclose(pin2_pos.y, EXPECTED_PIN2_Y, abs_tol=TOLERANCE), \
            f"Pin 2 Y mismatch: calculated={pin2_pos.y:.2f}, expected={EXPECTED_PIN2_Y}"

        logger.info("✓ Pin positions match KiCAD reference")

    def test_pin_position_90_degree_rotation_reference(self):
        """
        Test: Pin positions at 90° rotation match KiCAD reference.

        Reference Setup:
          - Device:R component at (98.425, 102.235)
          - Rotated 90° (horizontal orientation)
          - Wire endpoints extracted: left=(94.615, 102.235), right=(102.235, 102.235)

        At 90° rotation, pins should be:
          - Pin 1: left side of component
          - Pin 2: right side of component
        """
        logger.info("Reference test: Pin position at 90° rotation")

        ref_path = os.path.join(
            self.REFERENCE_PROJECTS_PATH,
            "pin_rotation_90deg",
            "pin_rotation_90deg.kicad_sch"
        )

        if not os.path.exists(ref_path):
            pytest.skip(f"Reference file not found: {ref_path}")

        # Act: Load and get component
        sch = ksa.Schematic.load(ref_path)
        comp = self.get_component_by_reference(sch, "R1")

        assert comp is not None
        assert comp.rotation == 90.0, f"Expected 90° rotation, got {comp.rotation}°"

        # Act: Get pin positions
        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        assert pin1_pos is not None
        assert pin2_pos is not None

        # Expected: Wire endpoints from reference file
        # At 90°, resistor pins are on left and right
        EXPECTED_PIN1_X = 94.615    # Left side
        EXPECTED_PIN1_Y = 102.235
        EXPECTED_PIN2_X = 102.235   # Right side
        EXPECTED_PIN2_Y = 102.235

        TOLERANCE = 0.05

        # Assert: Pin positions match
        assert math.isclose(pin1_pos.x, EXPECTED_PIN1_X, abs_tol=TOLERANCE), \
            f"Pin 1 X at 90°: {pin1_pos.x:.2f} vs expected {EXPECTED_PIN1_X}"

        assert math.isclose(pin1_pos.y, EXPECTED_PIN1_Y, abs_tol=TOLERANCE), \
            f"Pin 1 Y at 90°: {pin1_pos.y:.2f} vs expected {EXPECTED_PIN1_Y}"

        assert math.isclose(pin2_pos.x, EXPECTED_PIN2_X, abs_tol=TOLERANCE), \
            f"Pin 2 X at 90°: {pin2_pos.x:.2f} vs expected {EXPECTED_PIN2_X}"

        assert math.isclose(pin2_pos.y, EXPECTED_PIN2_Y, abs_tol=TOLERANCE), \
            f"Pin 2 Y at 90°: {pin2_pos.y:.2f} vs expected {EXPECTED_PIN2_Y}"

        logger.info("✓ 90° rotation pin positions match KiCAD reference")

    @pytest.mark.parametrize("rotation,description", [
        (0, "0° - vertical"),
        (90, "90° - horizontal right"),
        (180, "180° - vertical flipped"),
        (270, "270° - horizontal left"),
    ])
    def test_all_rotation_angles_reference(self, rotation, description):
        """
        Test: Pin positions at all rotation angles against references.

        Parametrized test loading different reference files for each rotation.
        """
        logger.info(f"Reference test: All rotations - {description}")

        # Map rotation to reference file name
        rotation_to_dir = {
            0: "pin_rotation_0deg",
            90: "pin_rotation_90deg",
            180: "pin_rotation_180deg",
            270: "pin_rotation_270deg",
        }

        ref_dir = rotation_to_dir.get(rotation)
        ref_path = os.path.join(
            self.REFERENCE_PROJECTS_PATH,
            ref_dir,
            f"{ref_dir}.kicad_sch"
        )

        if not os.path.exists(ref_path):
            pytest.skip(f"Reference file not found: {ref_path}")

        # Act: Load schematic
        sch = ksa.Schematic.load(ref_path)
        comp = self.get_component_by_reference(sch, "R1")

        # Assert: Component found with correct rotation
        assert comp is not None, f"R1 not found for {rotation}°"
        assert math.isclose(comp.rotation, rotation, abs_tol=0.1), \
            f"Rotation mismatch: {comp.rotation} vs expected {rotation}"

        # Act: Get pins
        pin1_pos = comp.get_pin_position("1")
        pin2_pos = comp.get_pin_position("2")

        # Assert: Pins exist
        assert pin1_pos is not None, f"Pin 1 not found at {rotation}°"
        assert pin2_pos is not None, f"Pin 2 not found at {rotation}°"

        # Assert: Distance between pins consistent (resistor spacing invariant)
        distance = math.sqrt(
            (pin2_pos.x - pin1_pos.x)**2 + (pin2_pos.y - pin1_pos.y)**2
        )

        # Resistor pins are ~3.81mm apart (standard KiCAD grid)
        assert 3.7 < distance < 3.9, \
            f"Pin spacing should be ~3.81mm at {rotation}°, got {distance:.2f}mm"

        logger.info(f"✓ {rotation}° rotation: pins={pin1_pos}, {pin2_pos}, distance={distance:.2f}mm")


class TestWireEndpointsToPins:
    """
    Test suite verifying that wires in reference schematics connect to correct pins.

    Reference files have manually drawn wires. We verify that:
      1. Wire endpoints match calculated pin positions
      2. This proves pin calculation is correct
    """

    @staticmethod
    def get_wires_for_component(sch, component_ref):
        """
        Helper: Get all wires connected to a component's pins.

        Searches through wires to find those connecting to given component.
        """
        logger.debug(f"Finding wires for {component_ref}")

        comp_pins = {}
        comp = sch.components.get(component_ref)

        if comp is None:
            return []

        # Get all pin positions for this component
        # This depends on the component having multiple pins
        # For a resistor, just pins 1 and 2
        for i in range(1, 10):
            pin_pos = comp.get_pin_position(str(i))
            if pin_pos:
                comp_pins[str(i)] = pin_pos
                logger.debug(f"  Pin {i}: {pin_pos}")

        connected_wires = []

        # Check each wire's endpoints against pin positions
        for wire in sch.wires:
            for pin_num, pin_pos in comp_pins.items():
                for point in wire.points:
                    # Check if wire endpoint matches pin position (within tolerance)
                    if (math.isclose(point.x, pin_pos.x, abs_tol=0.1) and
                        math.isclose(point.y, pin_pos.y, abs_tol=0.1)):
                        connected_wires.append((wire, pin_num, point))
                        logger.debug(f"  Wire connects to pin {pin_num}")
                        break

        return connected_wires

    def test_wire_endpoints_match_pin_positions_reference(self):
        """
        Test: Wires in reference schematic connect to calculated pin positions.

        This is the gold-standard test: manually drawn wires in a real KiCAD
        file should have endpoints at the exact positions we calculate.
        """
        logger.info("Reference test: Wire endpoints match pin positions")

        ref_path = os.path.join(
            "tests",
            "reference_kicad_projects",
            "simple_connections",
            "simple_connections.kicad_sch"
        )

        if not os.path.exists(ref_path):
            pytest.skip(f"Reference file not found: {ref_path}")

        # Act: Load reference
        sch = ksa.Schematic.load(ref_path)
        logger.info(f"Loaded reference with {len(sch.wires)} wires")

        # Act: Get wires for R1
        r1 = sch.components.get("R1")
        assert r1 is not None, "R1 should exist"

        pin1_pos = r1.get_pin_position("1")
        pin2_pos = r1.get_pin_position("2")

        logger.info(f"R1 pin positions: pin1={pin1_pos}, pin2={pin2_pos}")

        # Act: Find wires connected to these pins
        connected_wires = self.get_wires_for_component(sch, "R1")
        logger.info(f"Found {len(connected_wires)} wires connected to R1")

        # Assert: Should have wires (reference file has connections)
        assert len(connected_wires) > 0, "Reference should have wires connected to R1"

        # Assert: Each wire endpoint should match a pin position exactly
        for wire, pin_num, endpoint in connected_wires:
            pin_pos = r1.get_pin_position(pin_num)
            logger.debug(f"Wire to pin {pin_num}: endpoint={endpoint}, pin_pos={pin_pos}")

            assert pin_pos is not None
            assert math.isclose(endpoint.x, pin_pos.x, abs_tol=0.05), \
                f"Wire to pin {pin_num} X mismatch: {endpoint.x} vs {pin_pos.x}"
            assert math.isclose(endpoint.y, pin_pos.y, abs_tol=0.05), \
                f"Wire to pin {pin_num} Y mismatch: {endpoint.y} vs {pin_pos.y}"

        logger.info("✓ All wires connect to correct pin positions")


class TestReferenceFileIntegrity:
    """
    Test suite for reference file validation and integrity.

    Ensures reference files are properly formatted and usable.
    """

    def test_reference_files_exist(self):
        """
        Test: Required reference files exist.

        Helps debugging when reference files are missing.
        """
        required_references = [
            "pin_rotation_0deg/pin_rotation_0deg.kicad_sch",
            "pin_rotation_90deg/pin_rotation_90deg.kicad_sch",
        ]

        ref_base = "tests/reference_kicad_projects"

        for ref_file in required_references:
            full_path = os.path.join(ref_base, ref_file)
            if not os.path.exists(full_path):
                logger.warning(f"Missing reference file: {full_path}")
            # Don't assert here - some tests may skip if missing


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
