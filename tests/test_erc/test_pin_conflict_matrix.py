"""
Tests for Pin Conflict Matrix.

Tests the ERC pin type compatibility matrix matching KiCAD behavior.
"""

import pytest
from kicad_sch_api.validation.pin_matrix import PinConflictMatrix, PinSeverity


class TestPinConflictMatrix:
    """Test pin conflict matrix functionality."""

    def test_create_default_matrix(self):
        """Test creating matrix with KiCAD defaults."""
        matrix = PinConflictMatrix()

        # Should have default matrix loaded
        assert matrix is not None
        assert len(matrix.matrix) > 0

    def test_severity_constants(self):
        """Test severity level constants."""
        assert PinSeverity.OK == 0
        assert PinSeverity.WARNING == 1
        assert PinSeverity.ERROR == 2

    def test_output_to_output_is_error(self):
        """Test that Output-to-Output connection is ERROR."""
        matrix = PinConflictMatrix()

        severity = matrix.check_connection("output", "output")

        assert severity == PinSeverity.ERROR

    def test_power_output_to_power_output_is_error(self):
        """Test that Power Output-to-Power Output is ERROR (short circuit)."""
        matrix = PinConflictMatrix()

        severity = matrix.check_connection("power_output", "power_output")

        assert severity == PinSeverity.ERROR

    def test_output_to_power_output_is_error(self):
        """Test that Output-to-Power Output is ERROR (logic/power conflict)."""
        matrix = PinConflictMatrix()

        severity = matrix.check_connection("output", "power_output")

        # Should be error in both directions
        assert matrix.check_connection("output", "power_output") == PinSeverity.ERROR
        assert matrix.check_connection("power_output", "output") == PinSeverity.ERROR

    def test_input_to_output_is_ok(self):
        """Test that Input-to-Output is OK (normal connection)."""
        matrix = PinConflictMatrix()

        severity = matrix.check_connection("input", "output")

        assert severity == PinSeverity.OK

    def test_bidirectional_to_output_is_ok(self):
        """Test that Bidirectional-to-Output is OK."""
        matrix = PinConflictMatrix()

        severity = matrix.check_connection("bidirectional", "output")

        assert severity == PinSeverity.OK

    def test_passive_to_anything_is_ok(self):
        """Test that Passive pins can connect to anything without error."""
        matrix = PinConflictMatrix()

        # Passive should be OK with all pin types
        pin_types = [
            "input", "output", "bidirectional", "tristate",
            "passive", "power_input", "power_output",
            "open_collector", "open_emitter", "unspecified"
        ]

        for pin_type in pin_types:
            severity = matrix.check_connection("passive", pin_type)
            assert severity in [PinSeverity.OK, PinSeverity.WARNING], \
                f"Passive-to-{pin_type} should be OK or WARNING, got {severity}"

    def test_unspecified_generates_warning(self):
        """Test that Unspecified pins generate warnings."""
        matrix = PinConflictMatrix()

        # Unspecified should warn with most pin types
        severity = matrix.check_connection("unspecified", "output")

        assert severity == PinSeverity.WARNING

    def test_power_input_to_power_output_is_ok(self):
        """Test that Power Input-to-Power Output is OK (proper power connection)."""
        matrix = PinConflictMatrix()

        severity = matrix.check_connection("power_input", "power_output")

        assert severity == PinSeverity.OK

    def test_tristate_to_output_is_warning(self):
        """Test that Tri-state-to-Output connection generates warning."""
        matrix = PinConflictMatrix()

        severity = matrix.check_connection("tristate", "output")

        assert severity == PinSeverity.WARNING

    def test_open_collector_connections(self):
        """Test open collector pin connections."""
        matrix = PinConflictMatrix()

        # Open collector should be OK with most inputs
        assert matrix.check_connection("open_collector", "input") in [PinSeverity.OK, PinSeverity.WARNING]

    def test_matrix_is_symmetric(self):
        """Test that matrix is symmetric (pin1-pin2 == pin2-pin1)."""
        matrix = PinConflictMatrix()

        pin_types = ["input", "output", "bidirectional", "passive"]

        for pin1 in pin_types:
            for pin2 in pin_types:
                severity1 = matrix.check_connection(pin1, pin2)
                severity2 = matrix.check_connection(pin2, pin1)

                assert severity1 == severity2, \
                    f"{pin1}-{pin2} ({severity1}) != {pin2}-{pin1} ({severity2})"

    def test_set_custom_rule(self):
        """Test setting custom rule in matrix."""
        matrix = PinConflictMatrix()

        # Override default: make Output-Output a warning instead of error
        matrix.set_rule("output", "output", PinSeverity.WARNING)

        severity = matrix.check_connection("output", "output")

        assert severity == PinSeverity.WARNING

    def test_normalize_pin_type(self):
        """Test pin type normalization (case insensitive, handles PT_ prefix)."""
        matrix = PinConflictMatrix()

        # All these should be equivalent
        assert matrix.check_connection("output", "output") == \
               matrix.check_connection("OUTPUT", "output")
        assert matrix.check_connection("output", "output") == \
               matrix.check_connection("PT_OUTPUT", "PT_OUTPUT")

    def test_invalid_pin_type(self):
        """Test handling of invalid pin type."""
        matrix = PinConflictMatrix()

        # Should raise ValueError for invalid pin type
        with pytest.raises(ValueError):
            matrix.check_connection("invalid_pin_type", "output")

    def test_all_kicad_pin_types_supported(self):
        """Test that all 12 KiCAD pin types are supported."""
        matrix = PinConflictMatrix()

        kicad_pin_types = [
            "input",          # PT_INPUT
            "output",         # PT_OUTPUT
            "bidirectional",  # PT_BIDI
            "tristate",       # PT_TRISTATE
            "passive",        # PT_PASSIVE
            "free",           # PT_NIC (not internally connected)
            "unspecified",    # PT_UNSPECIFIED
            "power_input",    # PT_POWER_IN
            "power_output",   # PT_POWER_OUT
            "open_collector", # PT_OPENCOLLECTOR
            "open_emitter",   # PT_OPENEMITTER
            "nc"              # PT_NC (not connected)
        ]

        # All should be valid (not raise exception)
        for pin_type in kicad_pin_types:
            severity = matrix.check_connection(pin_type, "passive")
            assert severity in [PinSeverity.OK, PinSeverity.WARNING, PinSeverity.ERROR]

    def test_get_default_matrix(self):
        """Test getting default KiCAD matrix."""
        default_matrix = PinConflictMatrix.get_default_matrix()

        assert isinstance(default_matrix, dict)
        assert len(default_matrix) > 0

        # Spot check some critical rules
        assert default_matrix[("output", "output")] == PinSeverity.ERROR
        assert default_matrix[("power_output", "power_output")] == PinSeverity.ERROR
        assert default_matrix[("input", "output")] == PinSeverity.OK

    def test_load_from_dict(self):
        """Test loading custom matrix from dictionary."""
        custom_dict = {
            ("output", "output"): PinSeverity.WARNING,  # Override default
            ("input", "input"): PinSeverity.WARNING,    # Custom rule
        }

        matrix = PinConflictMatrix.from_dict(custom_dict)

        assert matrix.check_connection("output", "output") == PinSeverity.WARNING
        assert matrix.check_connection("input", "input") == PinSeverity.WARNING

    def test_pin_type_aliases(self):
        """Test that pin type aliases are handled correctly."""
        matrix = PinConflictMatrix()

        # "free" and "nic" should both map to PT_NIC
        severity1 = matrix.check_connection("free", "output")
        severity2 = matrix.check_connection("nic", "output")

        assert severity1 == severity2

    def test_multiple_outputs_to_passive(self):
        """Test multiple outputs can drive passive (pull-up/pull-down scenario)."""
        matrix = PinConflictMatrix()

        # This is common in circuits (multiple outputs with pull-up resistor)
        severity = matrix.check_connection("output", "passive")

        assert severity == PinSeverity.OK

    def test_nc_pin_to_anything_is_error(self):
        """Test that NC (not connected) pin connected to anything is error."""
        matrix = PinConflictMatrix()

        # NC pins should not be connected
        severity = matrix.check_connection("nc", "output")

        assert severity == PinSeverity.ERROR

    def test_matrix_completeness(self):
        """Test that matrix has rules for all pin type combinations."""
        matrix = PinConflictMatrix()

        pin_types = [
            "input", "output", "bidirectional", "tristate", "passive",
            "free", "unspecified", "power_input", "power_output",
            "open_collector", "open_emitter", "nc"
        ]

        # Check all combinations have rules
        for pin1 in pin_types:
            for pin2 in pin_types:
                try:
                    severity = matrix.check_connection(pin1, pin2)
                    assert severity in [PinSeverity.OK, PinSeverity.WARNING, PinSeverity.ERROR]
                except Exception as e:
                    pytest.fail(f"No rule for {pin1}-{pin2}: {e}")
