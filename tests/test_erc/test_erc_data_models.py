"""
Tests for ERC data models (ERCViolation, ERCResult).

Following TDD approach - these tests define the expected behavior.
"""

import pytest

from kicad_sch_api.core.types import Point
from kicad_sch_api.validation.erc_models import ERCConfig, ERCResult, ERCViolation


class TestERCViolation:
    """Test ERCViolation data model."""

    def test_create_basic_violation(self):
        """Test creating a basic violation."""
        violation = ERCViolation(
            violation_type="pin_conflict",
            severity="error",
            message="Output pin connected to another output pin",
            component_refs=["U1", "U2"],
            error_code="E001"
        )

        assert violation.violation_type == "pin_conflict"
        assert violation.severity == "error"
        assert violation.message == "Output pin connected to another output pin"
        assert violation.component_refs == ["U1", "U2"]
        assert violation.error_code == "E001"
        assert violation.net_name is None
        assert violation.pin_numbers == []
        assert violation.location is None
        assert violation.suggested_fix is None

    def test_create_violation_with_all_fields(self):
        """Test creating violation with all optional fields."""
        violation = ERCViolation(
            violation_type="pin_conflict",
            severity="error",
            message="Output pins shorted",
            component_refs=["U1", "U2"],
            net_name="NET1",
            pin_numbers=["1", "2"],
            location=Point(100.0, 100.0),
            suggested_fix="Remove one output or add buffer",
            error_code="E001"
        )

        assert violation.net_name == "NET1"
        assert violation.pin_numbers == ["1", "2"]
        assert violation.location == Point(100.0, 100.0)
        assert violation.suggested_fix == "Remove one output or add buffer"

    def test_violation_to_dict(self):
        """Test converting violation to dictionary."""
        violation = ERCViolation(
            violation_type="pin_conflict",
            severity="error",
            message="Test message",
            component_refs=["U1"],
            error_code="E001"
        )

        data = violation.to_dict()

        assert data["violation_type"] == "pin_conflict"
        assert data["severity"] == "error"
        assert data["message"] == "Test message"
        assert data["component_refs"] == ["U1"]
        assert data["error_code"] == "E001"

    def test_violation_severity_levels(self):
        """Test different severity levels."""
        error = ERCViolation(
            violation_type="test",
            severity="error",
            message="Error",
            component_refs=[],
            error_code="E001"
        )
        warning = ERCViolation(
            violation_type="test",
            severity="warning",
            message="Warning",
            component_refs=[],
            error_code="W001"
        )
        info = ERCViolation(
            violation_type="test",
            severity="info",
            message="Info",
            component_refs=[],
            error_code="I001"
        )

        assert error.severity == "error"
        assert warning.severity == "warning"
        assert info.severity == "info"


class TestERCResult:
    """Test ERCResult aggregation model."""

    def test_create_empty_result(self):
        """Test creating empty ERC result."""
        result = ERCResult(
            errors=[],
            warnings=[],
            info=[],
            total_checks=10,
            passed_checks=10,
            duration_ms=5.2
        )

        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert len(result.info) == 0
        assert result.total_checks == 10
        assert result.passed_checks == 10
        assert result.duration_ms == 5.2

    def test_has_errors_method(self):
        """Test has_errors() method."""
        # No errors
        result = ERCResult(
            errors=[],
            warnings=[],
            info=[],
            total_checks=5,
            passed_checks=5,
            duration_ms=1.0
        )
        assert result.has_errors() is False

        # With errors
        error = ERCViolation(
            violation_type="test",
            severity="error",
            message="Test",
            component_refs=[],
            error_code="E001"
        )
        result = ERCResult(
            errors=[error],
            warnings=[],
            info=[],
            total_checks=5,
            passed_checks=4,
            duration_ms=1.0
        )
        assert result.has_errors() is True

    def test_summary_method(self):
        """Test summary() method."""
        error = ERCViolation(
            violation_type="test",
            severity="error",
            message="Error",
            component_refs=[],
            error_code="E001"
        )
        warning1 = ERCViolation(
            violation_type="test",
            severity="warning",
            message="Warning 1",
            component_refs=[],
            error_code="W001"
        )
        warning2 = ERCViolation(
            violation_type="test",
            severity="warning",
            message="Warning 2",
            component_refs=[],
            error_code="W002"
        )

        result = ERCResult(
            errors=[error],
            warnings=[warning1, warning2],
            info=[],
            total_checks=10,
            passed_checks=7,
            duration_ms=10.5
        )

        summary = result.summary()
        assert "1 error" in summary or "1 errors" in summary
        assert "2 warning" in summary

    def test_filter_by_severity(self):
        """Test filtering violations by severity."""
        error = ERCViolation(
            violation_type="test",
            severity="error",
            message="Error",
            component_refs=[],
            error_code="E001"
        )
        warning = ERCViolation(
            violation_type="test",
            severity="warning",
            message="Warning",
            component_refs=[],
            error_code="W001"
        )

        result = ERCResult(
            errors=[error],
            warnings=[warning],
            info=[],
            total_checks=5,
            passed_checks=3,
            duration_ms=1.0
        )

        errors_only = result.filter_by_severity("error")
        assert len(errors_only) == 1
        assert errors_only[0].severity == "error"

        warnings_only = result.filter_by_severity("warning")
        assert len(warnings_only) == 1
        assert warnings_only[0].severity == "warning"

    def test_filter_by_component(self):
        """Test filtering violations by component reference."""
        violation1 = ERCViolation(
            violation_type="test",
            severity="error",
            message="Error on U1",
            component_refs=["U1"],
            error_code="E001"
        )
        violation2 = ERCViolation(
            violation_type="test",
            severity="error",
            message="Error on U2",
            component_refs=["U2"],
            error_code="E002"
        )
        violation3 = ERCViolation(
            violation_type="test",
            severity="error",
            message="Error on U1 and U2",
            component_refs=["U1", "U2"],
            error_code="E003"
        )

        result = ERCResult(
            errors=[violation1, violation2, violation3],
            warnings=[],
            info=[],
            total_checks=5,
            passed_checks=2,
            duration_ms=1.0
        )

        u1_violations = result.filter_by_component("U1")
        assert len(u1_violations) == 2  # violation1 and violation3

        u2_violations = result.filter_by_component("U2")
        assert len(u2_violations) == 2  # violation2 and violation3

    def test_to_dict(self):
        """Test converting result to dictionary."""
        error = ERCViolation(
            violation_type="test",
            severity="error",
            message="Test",
            component_refs=["U1"],
            error_code="E001"
        )

        result = ERCResult(
            errors=[error],
            warnings=[],
            info=[],
            total_checks=5,
            passed_checks=4,
            duration_ms=10.5
        )

        data = result.to_dict()

        assert len(data["errors"]) == 1
        assert len(data["warnings"]) == 0
        assert len(data["info"]) == 0
        assert data["total_checks"] == 5
        assert data["passed_checks"] == 4
        assert data["duration_ms"] == 10.5

    def test_to_json(self):
        """Test converting result to JSON string."""
        import json

        error = ERCViolation(
            violation_type="test",
            severity="error",
            message="Test",
            component_refs=["U1"],
            error_code="E001"
        )

        result = ERCResult(
            errors=[error],
            warnings=[],
            info=[],
            total_checks=5,
            passed_checks=4,
            duration_ms=10.5
        )

        json_str = result.to_json()
        data = json.loads(json_str)

        assert len(data["errors"]) == 1
        assert data["total_checks"] == 5


class TestERCConfig:
    """Test ERCConfig configuration model."""

    def test_create_default_config(self):
        """Test creating default configuration."""
        config = ERCConfig()

        assert config.severity_overrides == {}
        assert config.suppressed_warnings == set()
        assert config.custom_rules == []

    def test_set_severity_override(self):
        """Test setting severity override."""
        config = ERCConfig()
        config.set_severity("unconnected_input", "warning")

        assert config.severity_overrides["unconnected_input"] == "warning"

    def test_suppress_warning(self):
        """Test suppressing specific warning."""
        config = ERCConfig()
        config.suppress_warning("W001")

        assert "W001" in config.suppressed_warnings

    def test_suppress_warning_for_component(self):
        """Test suppressing warning for specific component."""
        config = ERCConfig()
        config.suppress_warning("W001", component="R1")

        # Should be stored as "W001:R1"
        assert "W001:R1" in config.suppressed_warnings

    def test_is_suppressed(self):
        """Test checking if warning is suppressed."""
        config = ERCConfig()
        config.suppress_warning("W001")
        config.suppress_warning("W002", component="R1")

        assert config.is_suppressed("W001") is True
        assert config.is_suppressed("W001", component="R1") is True
        assert config.is_suppressed("W002") is False
        assert config.is_suppressed("W002", component="R1") is True
        assert config.is_suppressed("W002", component="R2") is False
        assert config.is_suppressed("W003") is False
