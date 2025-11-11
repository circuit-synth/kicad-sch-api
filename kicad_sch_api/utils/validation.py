"""
Validation utilities for KiCAD schematic manipulation.

This module provides comprehensive validation capabilities including error collection,
syntax validation, and semantic checking for schematic operations.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Union

# Import ValidationError from new exception hierarchy for backward compatibility
from ..core.exceptions import ValidationError

logger = logging.getLogger(__name__)

# Export list for public API
__all__ = [
    "ValidationError",
    "ValidationIssue",
    "ValidationLevel",
    "SchematicValidator",
    "validate_schematic_file",
    "collect_validation_errors",
]


class ValidationLevel(Enum):
    """Validation issue severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Single validation issue with context."""

    category: str  # e.g., "syntax", "reference", "connection"
    message: str  # Human-readable description
    level: ValidationLevel
    context: Optional[Dict[str, Any]] = None  # Additional context data
    suggestion: Optional[str] = None  # Suggested fix

    def __post_init__(self):
        if isinstance(self.level, str):
            self.level = ValidationLevel(self.level)

    def __str__(self) -> str:
        context_str = f" ({self.context})" if self.context else ""
        suggestion_str = f" Suggestion: {self.suggestion}" if self.suggestion else ""
        return f"{self.level.value.upper()}: {self.category}: {self.message}{context_str}{suggestion_str}"


# ValidationError is now imported from core.exceptions (see imports at top)
# This provides backward compatibility for existing code while using the new
# exception hierarchy


class SchematicValidator:
    """
    Comprehensive validator for schematic data structures and operations.

    Provides validation for:
    - S-expression syntax
    - Component references and properties
    - Library references
    - Basic electrical connectivity
    """

    def __init__(self, strict: bool = False):
        """
        Initialize validator.

        Args:
            strict: If True, warnings are treated as errors
        """
        self.strict = strict
        self.issues = []
        self._valid_reference_pattern = re.compile(r"^(#[A-Z]+[0-9]+|[A-Z]+[0-9]*[A-Z]?|[A-Z]+\?)$")
        self._valid_lib_id_pattern = re.compile(r"^[^:]+:[^:]+$")

    def validate_schematic_data(self, schematic_data: Dict[str, Any]) -> List[ValidationIssue]:
        """
        Validate complete schematic data structure.

        Args:
            schematic_data: Parsed schematic data

        Returns:
            List of validation issues found
        """
        self.issues.clear()

        # Validate basic structure
        self._validate_basic_structure(schematic_data)

        # Validate components
        components = schematic_data.get("components", [])
        self._validate_components(components)

        # Validate references are unique
        self._validate_unique_references(components)

        # Validate wires and connections
        wires = schematic_data.get("wires", [])
        self._validate_wires(wires)

        # Validate nets
        nets = schematic_data.get("nets", [])
        self._validate_nets(nets, components)

        return self.issues.copy()

    def validate_component(self, component_data: Dict[str, Any]) -> List[ValidationIssue]:
        """Validate a single component."""
        self.issues.clear()
        self._validate_single_component(component_data)
        return self.issues.copy()

    def validate_reference(self, reference: str) -> bool:
        """
        Validate component reference format.

        Args:
            reference: Reference to validate (e.g., "R1", "U5", "#PWR01")

        Returns:
            True if reference is valid
        """
        if not reference:
            return False
        return bool(self._valid_reference_pattern.match(reference))

    def validate_lib_id(self, lib_id: str) -> bool:
        """
        Validate library ID format.

        Args:
            lib_id: Library ID to validate (e.g., "Device:R")

        Returns:
            True if lib_id is valid
        """
        if not lib_id:
            return False
        return bool(self._valid_lib_id_pattern.match(lib_id))

    def _validate_basic_structure(self, data: Dict[str, Any]):
        """Validate basic schematic structure."""
        required_fields = ["version", "components"]

        for field in required_fields:
            if field not in data:
                self.issues.append(
                    ValidationIssue(
                        category="structure",
                        message=f"Missing required field: {field}",
                        level=ValidationLevel.ERROR,
                    )
                )

        # Check version format
        version = data.get("version")
        if version and not isinstance(version, (int, str)):
            self.issues.append(
                ValidationIssue(
                    category="structure",
                    message=f"Invalid version type: {type(version)}",
                    level=ValidationLevel.WARNING,
                    suggestion="Version should be string or number",
                )
            )

    def _validate_components(self, components: List[Dict[str, Any]]):
        """Validate all components in schematic."""
        if not isinstance(components, list):
            self.issues.append(
                ValidationIssue(
                    category="components",
                    message="Components must be a list",
                    level=ValidationLevel.ERROR,
                )
            )
            return

        for i, component in enumerate(components):
            try:
                self._validate_single_component(component, f"component[{i}]")
            except Exception as e:
                self.issues.append(
                    ValidationIssue(
                        category="components",
                        message=f"Error validating component {i}: {e}",
                        level=ValidationLevel.ERROR,
                        context={"component_index": i},
                    )
                )

    def _validate_single_component(self, component: Dict[str, Any], context: str = "component"):
        """Validate a single component structure."""
        required_fields = ["lib_id", "reference", "position"]

        for field in required_fields:
            if field not in component:
                self.issues.append(
                    ValidationIssue(
                        category="component",
                        message=f"{context}: Missing required field: {field}",
                        level=ValidationLevel.ERROR,
                        context={"field": field},
                    )
                )

        # Validate reference format
        reference = component.get("reference")
        if reference and not self.validate_reference(reference):
            self.issues.append(
                ValidationIssue(
                    category="reference",
                    message=f"{context}: Invalid reference format: {reference}",
                    level=ValidationLevel.ERROR,
                    context={"reference": reference},
                    suggestion="Reference should match pattern: [A-Z]+[0-9]* or #[A-Z]+[0-9]* (for power symbols)",
                )
            )

        # Validate lib_id format
        lib_id = component.get("lib_id")
        if lib_id and not self.validate_lib_id(lib_id):
            self.issues.append(
                ValidationIssue(
                    category="lib_id",
                    message=f"{context}: Invalid lib_id format: {lib_id}",
                    level=ValidationLevel.ERROR,
                    context={"lib_id": lib_id},
                    suggestion="lib_id should match pattern: Library:Symbol",
                )
            )

        # Validate position
        position = component.get("position")
        if position:
            self._validate_position(position, f"{context}.position")

        # Validate UUID if present
        uuid = component.get("uuid")
        if uuid and not self._validate_uuid(uuid):
            self.issues.append(
                ValidationIssue(
                    category="uuid",
                    message=f"{context}: Invalid UUID format: {uuid}",
                    level=ValidationLevel.WARNING,
                    context={"uuid": uuid},
                )
            )

    def _validate_position(self, position: Any, context: str):
        """Validate position data."""
        if hasattr(position, "x") and hasattr(position, "y"):
            # Point object
            try:
                float(position.x)
                float(position.y)
            except (TypeError, ValueError):
                self.issues.append(
                    ValidationIssue(
                        category="position",
                        message=f"{context}: Position coordinates must be numeric",
                        level=ValidationLevel.ERROR,
                        context={"position": str(position)},
                    )
                )
        else:
            self.issues.append(
                ValidationIssue(
                    category="position",
                    message=f"{context}: Invalid position format",
                    level=ValidationLevel.ERROR,
                    context={"position": position},
                    suggestion="Position should be Point object with x,y coordinates",
                )
            )

    def _validate_unique_references(self, components: List[Dict[str, Any]]):
        """
        Validate that all (reference, unit) pairs are unique.

        Multi-unit components (like op-amps) can share the same reference
        as long as they have different unit numbers.
        """
        reference_unit_pairs = []
        duplicates = set()

        for component in components:
            ref = component.get("reference")
            unit = component.get("unit", 1)  # Default to unit 1 if not specified
            if ref:
                pair = (ref, unit)
                if pair in reference_unit_pairs:
                    duplicates.add(pair)
                reference_unit_pairs.append(pair)

        for ref, unit in duplicates:
            self.issues.append(
                ValidationIssue(
                    category="reference",
                    message=f"Duplicate component reference and unit: {ref} (unit {unit})",
                    level=ValidationLevel.ERROR,
                    context={"reference": ref, "unit": unit},
                    suggestion="Each (reference, unit) pair must be unique. Multi-unit components should have the same reference but different unit numbers.",
                )
            )

    def _validate_wires(self, wires: List[Dict[str, Any]]):
        """Validate wire connections."""
        for i, wire in enumerate(wires):
            context = f"wire[{i}]"

            # Validate start and end points
            for point_name in ["start", "end"]:
                point = wire.get(point_name)
                if point:
                    self._validate_position(point, f"{context}.{point_name}")

            # Validate wire has valid length
            start = wire.get("start")
            end = wire.get("end")
            if start and end and hasattr(start, "x") and hasattr(end, "x"):
                if start.x == end.x and start.y == end.y:
                    self.issues.append(
                        ValidationIssue(
                            category="wire",
                            message=f"{context}: Wire has zero length",
                            level=ValidationLevel.WARNING,
                            context={"start": str(start), "end": str(end)},
                        )
                    )

    def _validate_nets(self, nets: List[Dict[str, Any]], components: List[Dict[str, Any]]):
        """Validate electrical nets."""
        component_refs = {comp.get("reference") for comp in components if comp.get("reference")}

        for i, net in enumerate(nets):
            context = f"net[{i}]"

            # Validate net has connections
            connections = net.get("components", [])
            if not connections:
                self.issues.append(
                    ValidationIssue(
                        category="net",
                        message=f"{context}: Net has no connections",
                        level=ValidationLevel.WARNING,
                        context={"net_name": net.get("name", "unnamed")},
                    )
                )

            # Validate all referenced components exist
            for ref, pin in connections:
                if ref not in component_refs:
                    self.issues.append(
                        ValidationIssue(
                            category="net",
                            message=f"{context}: References non-existent component: {ref}",
                            level=ValidationLevel.ERROR,
                            context={"reference": ref, "net_name": net.get("name", "unnamed")},
                        )
                    )

    def _validate_uuid(self, uuid_str: str) -> bool:
        """Validate UUID format."""
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
        )
        return bool(uuid_pattern.match(uuid_str))

    def has_errors(self) -> bool:
        """Check if any error-level issues were found."""
        return any(
            issue.level in (ValidationLevel.ERROR, ValidationLevel.CRITICAL)
            for issue in self.issues
        )

    def has_warnings(self) -> bool:
        """Check if any warning-level issues were found."""
        return any(issue.level == ValidationLevel.WARNING for issue in self.issues)

    def get_summary(self) -> Dict[str, int]:
        """Get summary of validation issues by level."""
        summary = {level.value: 0 for level in ValidationLevel}
        for issue in self.issues:
            summary[issue.level.value] += 1
        return summary


def validate_schematic_file(file_path: str) -> List[ValidationIssue]:
    """
    Convenience function to validate a schematic file.

    Args:
        file_path: Path to .kicad_sch file

    Returns:
        List of validation issues
    """
    from ..core.parser import SExpressionParser

    parser = SExpressionParser()
    try:
        schematic_data = parser.parse_file(file_path)
        validator = SchematicValidator()
        return validator.validate_schematic_data(schematic_data)
    except Exception as e:
        return [
            ValidationIssue(
                category="file",
                message=f"Failed to validate file {file_path}: {e}",
                level=ValidationLevel.CRITICAL,
            )
        ]


def collect_validation_errors(func):
    """
    Decorator to collect validation errors from operations.

    Usage:
        @collect_validation_errors
        def my_operation():
            # ... operation that might have validation issues
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation failed in {func.__name__}: {e}")
            # Log individual issues
            for issue in e.issues:
                logger.warning(f"  {issue}")
            raise

    return wrapper
