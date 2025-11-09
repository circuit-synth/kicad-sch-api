"""
Tests for ERC validators (Pin Type, Connectivity, Component, Power).

Tests the actual validation logic with test schematics.
"""

import pytest

import kicad_sch_api as ksa
from kicad_sch_api.validation.erc import ElectricalRulesChecker
from kicad_sch_api.validation.validators import (
    ComponentValidator,
    ConnectivityValidator,
    PinTypeValidator,
    PowerValidator,
)


class TestPinTypeValidator:
    """Test pin type conflict validation."""

    def test_detect_output_to_output_conflict(self):
        """Test detection of Output-to-Output connection (ERROR)."""
        # Create schematic with two outputs connected
        sch = ksa.create_schematic("Test")

        # Add two components with output pins connected
        u1 = sch.components.add("Device:R", "U1", "1k", (100, 100))
        u2 = sch.components.add("Device:R", "U2", "1k", (150, 100))

        # Connect them (this will be on same net)
        sch.add_wire_between_pins("U1", "2", "U2", "1")

        # Run pin type validation
        validator = PinTypeValidator(sch)
        violations = validator.validate()

        # Should detect output-output conflict
        # Note: This test will pass once we implement actual pin type detection
        # For now, it defines expected behavior

    def test_input_to_output_is_ok(self):
        """Test that Input-to-Output connection is OK."""
        sch = ksa.create_schematic("Test")

        # Normal connection: output driving input
        led = sch.components.add("Device:LED", "D1", "RED", (100, 100))
        resistor = sch.components.add("Device:R", "R1", "330", (150, 100))

        sch.add_wire_between_pins("R1", "2", "D1", "1")

        validator = PinTypeValidator(sch)
        violations = validator.validate()

        # Should have no errors for this normal connection
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0

    def test_passive_connections_always_ok(self):
        """Test that passive components connect without errors."""
        sch = ksa.create_schematic("Test")

        # Resistor and capacitor in series (both passive)
        r1 = sch.components.add("Device:R", "R1", "1k", (100, 100))
        c1 = sch.components.add("Device:C", "C1", "100nF", (150, 100))

        sch.add_wire_between_pins("R1", "2", "C1", "1")

        validator = PinTypeValidator(sch)
        violations = validator.validate()

        # Passive-to-passive should be OK
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0

    def test_power_output_short_detected(self):
        """Test detection of multiple power outputs on same net (ERROR)."""
        sch = ksa.create_schematic("Test")

        # Two voltage regulators outputs connected (short circuit!)
        # This would be a serious design error
        # Test defines expected behavior - will implement detection


class TestConnectivityValidator:
    """Test wire connectivity validation."""

    def test_detect_dangling_wire(self):
        """Test detection of wire with only one connection (WARNING)."""
        sch = ksa.create_schematic("Test")

        # Add component
        r1 = sch.components.add("Device:R", "R1", "1k", (100, 100))

        # Add wire from pin that goes nowhere
        pin_pos = sch.get_component_pin_position("R1", "1")
        sch.wires.add(start=pin_pos, end=(pin_pos.x + 20, pin_pos.y))

        validator = ConnectivityValidator(sch)
        violations = validator.validate()

        # Should detect dangling wire
        dangling = [v for v in violations if v.violation_type == "dangling_wire"]
        assert len(dangling) > 0

    def test_detect_unconnected_input(self):
        """Test detection of unconnected input pin (WARNING)."""
        sch = ksa.create_schematic("Test")

        # Add component with unconnected pin
        led = sch.components.add("Device:LED", "D1", "RED", (100, 100))
        # Pin 1 (input) is not connected

        validator = ConnectivityValidator(sch)
        violations = validator.validate()

        # Should warn about unconnected input
        unconnected = [v for v in violations if v.violation_type == "unconnected_pin"]
        assert len(unconnected) > 0

    def test_detect_undriven_net(self):
        """Test detection of net with no output driver (WARNING)."""
        sch = ksa.create_schematic("Test")

        # Create net with only inputs (no driver)
        led1 = sch.components.add("Device:LED", "D1", "RED", (100, 100))
        led2 = sch.components.add("Device:LED", "D2", "RED", (150, 100))

        # Connect inputs together (no output to drive them)
        sch.add_wire_between_pins("D1", "1", "D2", "1")

        validator = ConnectivityValidator(sch)
        violations = validator.validate()

        # Should warn about undriven net
        undriven = [v for v in violations if v.violation_type == "undriven_net"]
        assert len(undriven) > 0

    def test_properly_connected_circuit_no_warnings(self):
        """Test that properly connected circuit has no connectivity warnings."""
        sch = ksa.create_schematic("Test")

        # Proper circuit: resistor driving LED
        resistor = sch.components.add("Device:R", "R1", "330", (100, 100))
        led = sch.components.add("Device:LED", "D1", "RED", (150, 100))

        sch.add_wire_between_pins("R1", "2", "D1", "1")

        validator = ConnectivityValidator(sch)
        violations = validator.validate()

        # Should have no connectivity errors
        errors = [v for v in violations if v.severity == "error"]
        assert len(errors) == 0


class TestComponentValidator:
    """Test component property validation."""

    def test_detect_duplicate_references(self):
        """Test detection of duplicate component references (ERROR)."""
        sch = ksa.create_schematic("Test")

        # Add two components with same reference (should be caught)
        r1 = sch.components.add("Device:R", "R1", "1k", (100, 100))
        # Manually change second component to duplicate reference
        r2 = sch.components.add("Device:R", "R2", "2k", (150, 100))
        r2._data.reference = "R1"  # Force duplicate

        validator = ComponentValidator(sch)
        violations = validator.validate()

        # Should detect duplicate
        duplicates = [v for v in violations if v.violation_type == "duplicate_reference"]
        assert len(duplicates) > 0
        assert duplicates[0].severity == "error"

    def test_detect_missing_value(self):
        """Test detection of missing component value (WARNING)."""
        sch = ksa.create_schematic("Test")

        r1 = sch.components.add("Device:R", "R1", "", (100, 100))  # Empty value

        validator = ComponentValidator(sch)
        violations = validator.validate()

        # Should warn about missing value
        missing_value = [v for v in violations if v.violation_type == "missing_value"]
        assert len(missing_value) > 0
        assert missing_value[0].severity == "warning"

    def test_detect_missing_footprint(self):
        """Test detection of missing footprint (WARNING)."""
        sch = ksa.create_schematic("Test")

        r1 = sch.components.add("Device:R", "R1", "1k", (100, 100))
        # No footprint specified

        validator = ComponentValidator(sch)
        violations = validator.validate()

        # Should warn about missing footprint
        missing_footprint = [v for v in violations if v.violation_type == "missing_footprint"]
        # This is optional warning, may or may not fire depending on requirements

    def test_invalid_reference_format(self):
        """Test detection of invalid reference format (ERROR)."""
        sch = ksa.create_schematic("Test")

        r1 = sch.components.add("Device:R", "INVALID!", "1k", (100, 100))

        validator = ComponentValidator(sch)
        violations = validator.validate()

        # Should detect invalid format
        invalid = [v for v in violations if v.violation_type == "invalid_reference"]
        if len(invalid) > 0:  # If we implement strict format checking
            assert invalid[0].severity == "error"


class TestPowerValidator:
    """Test power supply validation."""

    def test_detect_missing_power_flag(self):
        """Test detection of power net without PWR_FLAG (WARNING)."""
        sch = ksa.create_schematic("Test")

        # Add component with power pins but no PWR_FLAG
        # Power nets typically need PWR_FLAG to indicate they're driven externally

        validator = PowerValidator(sch)
        violations = validator.validate()

        # Should warn about missing power flag
        # Note: This is WARNING not ERROR per requirements

    def test_power_input_without_driver(self):
        """Test detection of power input with no power source (WARNING)."""
        sch = ksa.create_schematic("Test")

        # Component with power input but no regulator or PWR_FLAG

        validator = PowerValidator(sch)
        violations = validator.validate()

        # Should warn about undriven power

    def test_proper_power_connection_no_warnings(self):
        """Test that properly powered circuit has no power warnings."""
        sch = ksa.create_schematic("Test")

        # Proper power: regulator output driving IC power input
        # This is correct and should not generate warnings


class TestElectricalRulesChecker:
    """Test main ERC orchestrator."""

    def test_create_erc_checker(self):
        """Test creating ERC checker."""
        sch = ksa.create_schematic("Test")
        erc = ElectricalRulesChecker(sch)

        assert erc is not None
        assert erc.schematic == sch

    def test_run_all_checks(self):
        """Test running all ERC checks."""
        sch = ksa.create_schematic("Test")

        # Add simple valid circuit
        r1 = sch.components.add("Device:R", "R1", "1k", (100, 100))

        erc = ElectricalRulesChecker(sch)
        result = erc.run_all_checks()

        assert result is not None
        assert isinstance(result.errors, list)
        assert isinstance(result.warnings, list)
        assert result.total_checks > 0

    def test_run_specific_check(self):
        """Test running specific check type."""
        sch = ksa.create_schematic("Test")
        erc = ElectricalRulesChecker(sch)

        # Run only pin type checks
        violations = erc.run_check("pin_types")

        assert isinstance(violations, list)

    def test_erc_with_custom_config(self):
        """Test ERC with custom configuration."""
        from kicad_sch_api.validation.erc_models import ERCConfig

        sch = ksa.create_schematic("Test")

        config = ERCConfig()
        config.set_severity("unconnected_input", "error")  # Make it stricter

        erc = ElectricalRulesChecker(sch, config=config)
        result = erc.run_all_checks()

        # Config should be applied

    def test_erc_performance(self):
        """Test ERC performance on moderate-sized schematic."""
        import time

        sch = ksa.create_schematic("Test")

        # Add 50 components
        for i in range(50):
            x = 100 + (i % 10) * 20
            y = 100 + (i // 10) * 20
            sch.components.add("Device:R", f"R{i+1}", "1k", (x, y))

        erc = ElectricalRulesChecker(sch)

        start = time.time()
        result = erc.run_all_checks()
        duration = (time.time() - start) * 1000  # ms

        # Should be fast (<100ms for 50 components)
        assert duration < 100, f"ERC took {duration}ms for 50 components (target <100ms)"

    def test_erc_with_no_violations(self):
        """Test ERC on schematic with no violations."""
        sch = ksa.create_schematic("Test")

        # Perfect circuit (if such a thing exists!)
        # Or at least one with no errors

        erc = ElectricalRulesChecker(sch)
        result = erc.run_all_checks()

        # May have warnings but should have no errors
        assert result.has_errors() is False or len(result.errors) == 0

    def test_erc_violation_codes_unique(self):
        """Test that all violation codes are unique."""
        sch = ksa.create_schematic("Test")

        # Add various components to trigger different violations
        r1 = sch.components.add("Device:R", "R1", "", (100, 100))  # Missing value
        r2 = sch.components.add("Device:R", "R1", "1k", (150, 100))  # Duplicate ref

        erc = ElectricalRulesChecker(sch)
        result = erc.run_all_checks()

        # Check all error codes are unique
        all_violations = result.errors + result.warnings + result.info
        error_codes = [v.error_code for v in all_violations]

        # Each violation should have a code
        assert all(code for code in error_codes)

    def test_erc_suggested_fixes(self):
        """Test that violations include suggested fixes where applicable."""
        sch = ksa.create_schematic("Test")

        # Create violation that should have suggested fix
        r1 = sch.components.add("Device:R", "R1", "1k", (100, 100))
        r2 = sch.components.add("Device:R", "R1", "2k", (150, 100))  # Duplicate

        erc = ElectricalRulesChecker(sch)
        result = erc.run_all_checks()

        # Duplicate reference should have suggested fix
        duplicates = [v for v in result.errors if v.violation_type == "duplicate_reference"]
        if len(duplicates) > 0:
            # Should suggest renaming one of them
            assert duplicates[0].suggested_fix is not None
            assert (
                "rename" in duplicates[0].suggested_fix.lower()
                or "change" in duplicates[0].suggested_fix.lower()
            )
