"""
ERC data models: ERCViolation, ERCResult, ERCConfig.

These models represent validation results and configuration.
"""

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from kicad_sch_api.core.types import Point


@dataclass
class ERCViolation:
    """Single ERC violation.

    Represents one electrical rule violation found during validation.

    Attributes:
        violation_type: Category of violation (e.g., "pin_conflict", "dangling_wire")
        severity: "error", "warning", or "info"
        message: Human-readable description
        component_refs: List of affected component references
        error_code: Unique error code (e.g., "E001", "W042")
        net_name: Optional net name where violation occurred
        pin_numbers: List of affected pin numbers
        location: Optional schematic coordinates
        suggested_fix: Optional recommended fix
    """

    violation_type: str
    severity: str
    message: str
    component_refs: List[str]
    error_code: str
    net_name: Optional[str] = None
    pin_numbers: List[str] = field(default_factory=list)
    location: Optional[Point] = None
    suggested_fix: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert violation to dictionary for serialization."""
        return {
            "violation_type": self.violation_type,
            "severity": self.severity,
            "message": self.message,
            "component_refs": self.component_refs,
            "error_code": self.error_code,
            "net_name": self.net_name,
            "pin_numbers": self.pin_numbers,
            "location": {"x": self.location.x, "y": self.location.y} if self.location else None,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class ERCResult:
    """Complete ERC validation results.

    Aggregates all violations found during validation.

    Attributes:
        errors: List of error-level violations
        warnings: List of warning-level violations
        info: List of info-level violations
        total_checks: Total number of checks performed
        passed_checks: Number of checks that passed
        duration_ms: Execution time in milliseconds
    """

    errors: List[ERCViolation]
    warnings: List[ERCViolation]
    info: List[ERCViolation]
    total_checks: int
    passed_checks: int
    duration_ms: float

    def has_errors(self) -> bool:
        """Check if any errors were found."""
        return len(self.errors) > 0

    def summary(self) -> str:
        """Generate human-readable summary."""
        error_count = len(self.errors)
        warning_count = len(self.warnings)

        error_str = f"{error_count} error{'s' if error_count != 1 else ''}"
        warning_str = f"{warning_count} warning{'s' if warning_count != 1 else ''}"

        return f"{error_str}, {warning_str}"

    def filter_by_severity(self, severity: str) -> List[ERCViolation]:
        """Filter violations by severity level.

        Args:
            severity: "error", "warning", or "info"

        Returns:
            List of violations matching severity
        """
        if severity == "error":
            return self.errors
        elif severity == "warning":
            return self.warnings
        elif severity == "info":
            return self.info
        else:
            return []

    def filter_by_component(self, ref: str) -> List[ERCViolation]:
        """Filter violations affecting a specific component.

        Args:
            ref: Component reference (e.g., "R1")

        Returns:
            List of violations involving this component
        """
        all_violations = self.errors + self.warnings + self.info
        return [v for v in all_violations if ref in v.component_refs]

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "info": [i.to_dict() for i in self.info],
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks,
            "duration_ms": self.duration_ms,
            "summary": self.summary(),
        }

    def to_json(self) -> str:
        """Convert result to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class ERCConfig:
    """ERC configuration.

    Allows customizing validation behavior, severity levels, and rule suppression.

    Attributes:
        severity_overrides: Custom severity levels for specific rules
        suppressed_warnings: Set of suppressed warning codes
        custom_rules: List of custom validation rules (not yet implemented)
    """

    def __init__(self) -> None:
        """Initialize with default configuration."""
        self.severity_overrides: Dict[str, str] = {}
        self.suppressed_warnings: Set[str] = set()
        self.custom_rules: List[Any] = []

    def set_severity(self, rule: str, severity: str) -> None:
        """Override default severity for a rule.

        Args:
            rule: Rule identifier (e.g., "unconnected_input")
            severity: "error", "warning", or "info"
        """
        if severity not in ["error", "warning", "info"]:
            raise ValueError(f"Invalid severity: {severity}")
        self.severity_overrides[rule] = severity

    def suppress_warning(self, code: str, component: Optional[str] = None) -> None:
        """Suppress a specific warning.

        Args:
            code: Warning code (e.g., "W001")
            component: Optional component reference to suppress only for that component
        """
        if component:
            # Store as "code:component" for component-specific suppression
            self.suppressed_warnings.add(f"{code}:{component}")
        else:
            # Store as just "code" for global suppression
            self.suppressed_warnings.add(code)

    def is_suppressed(self, code: str, component: Optional[str] = None) -> bool:
        """Check if a warning is suppressed.

        Args:
            code: Warning code
            component: Optional component reference

        Returns:
            True if warning should be suppressed
        """
        # Check global suppression
        if code in self.suppressed_warnings:
            return True

        # Check component-specific suppression
        if component and f"{code}:{component}" in self.suppressed_warnings:
            return True

        return False
