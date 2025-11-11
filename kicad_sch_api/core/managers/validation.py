"""
Validation Manager for KiCAD schematic integrity checking.

Provides comprehensive validation for schematic integrity, design rules,
connectivity analysis, and format compliance while collecting and reporting
validation issues systematically.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from ...utils.validation import ValidationError, ValidationIssue
from ..types import Point
from .base import BaseManager

logger = logging.getLogger(__name__)


class ValidationManager(BaseManager):
    """
    Comprehensive validation manager for schematic integrity.

    Responsible for:
    - Schematic-wide integrity checks
    - Component reference validation
    - Connectivity analysis
    - Design rule checking
    - Format compliance validation
    - Validation issue collection and reporting
    """

    def __init__(
        self, schematic_data: Dict[str, Any], component_collection=None, wire_collection=None
    ):
        """
        Initialize ValidationManager.

        Args:
            schematic_data: Reference to schematic data
            component_collection: Component collection for validation
            wire_collection: Wire collection for connectivity analysis
        """
        super().__init__(schematic_data)
        self._components = component_collection
        self._wires = wire_collection
        self._validation_rules = self._initialize_validation_rules()

    def validate_schematic(self) -> List[ValidationIssue]:
        """
        Perform comprehensive schematic validation.

        Returns:
            List of all validation issues found
        """
        issues = []

        # Run all validation rules
        for rule_name, rule_func in self._validation_rules.items():
            try:
                rule_issues = rule_func()
                issues.extend(rule_issues)
                logger.debug(f"Validation rule '{rule_name}' found {len(rule_issues)} issues")
            except Exception as e:
                issues.append(
                    ValidationIssue(
                        category="validation_system",
                        message=f"Validation rule '{rule_name}' failed: {e}",
                        level="error",
                        context={"rule": rule_name, "error": str(e)},
                    )
                )
                logger.error(f"Validation rule '{rule_name}' failed: {e}")

        logger.info(f"Schematic validation completed with {len(issues)} issues")
        return issues

    def validate_component_references(self) -> List[ValidationIssue]:
        """
        Validate component references for duplicates and format.

        Returns:
            List of reference validation issues
        """
        issues = []

        if not self._components:
            return issues

        references = []
        reference_positions = {}
        reference_unit_pairs = []  # Track (reference, unit) pairs

        # Collect all component references and units
        for component in self._components:
            ref = component.reference
            unit = component._data.unit if hasattr(component._data, "unit") else 1
            references.append(ref)
            reference_unit_pairs.append((ref, unit))
            reference_positions[ref] = component.position

        # Check for duplicate (reference, unit) pairs
        # Multiple components can have the same reference if they have different unit numbers
        # (this is how multi-unit components like op-amps work in KiCAD)
        seen_pairs = {}
        for ref, unit in reference_unit_pairs:
            pair_key = (ref, unit)
            if pair_key in seen_pairs:
                issues.append(
                    ValidationIssue(
                        category="component_references",
                        message=f"Duplicate component reference and unit: {ref} (unit {unit})",
                        level="error",
                        context={"reference": ref, "unit": unit},
                    )
                )
            else:
                seen_pairs[pair_key] = True

        # Check reference format
        for ref in set(references):
            if not self._validate_reference_format(ref):
                issues.append(
                    ValidationIssue(
                        category="component_references",
                        message=f"Invalid reference format: {ref}",
                        level="warning",
                        context={"reference": ref},
                    )
                )

        return issues

    def validate_connectivity(self) -> List[ValidationIssue]:
        """
        Validate electrical connectivity and nets.

        Returns:
            List of connectivity validation issues
        """
        issues = []

        if not self._wires or not self._components:
            return issues

        # Check for unconnected pins
        unconnected_pins = self._find_unconnected_pins()
        for component_ref, pin_number in unconnected_pins:
            issues.append(
                ValidationIssue(
                    category="connectivity",
                    message=f"Unconnected pin: {component_ref}.{pin_number}",
                    level="warning",
                    context={"component": component_ref, "pin": pin_number},
                )
            )

        # Check for floating wires
        floating_wires = self._find_floating_wires()
        for wire_uuid in floating_wires:
            issues.append(
                ValidationIssue(
                    category="connectivity",
                    message=f"Floating wire (not connected to components): {wire_uuid}",
                    level="warning",
                    context={"wire": wire_uuid},
                )
            )

        # Check for short circuits
        short_circuits = self._find_potential_short_circuits()
        for circuit_info in short_circuits:
            issues.append(
                ValidationIssue(
                    category="connectivity",
                    message=f"Potential short circuit: {circuit_info['description']}",
                    level="error",
                    context=circuit_info,
                )
            )

        return issues

    def validate_positioning(self) -> List[ValidationIssue]:
        """
        Validate component and element positioning.

        Returns:
            List of positioning validation issues
        """
        issues = []

        # Check for overlapping components
        if self._components:
            overlapping_components = self._find_overlapping_components()
            for comp1_ref, comp2_ref, distance in overlapping_components:
                issues.append(
                    ValidationIssue(
                        category="positioning",
                        message=f"Components too close: {comp1_ref} and {comp2_ref} (distance: {distance:.2f})",
                        level="warning",
                        context={
                            "component1": comp1_ref,
                            "component2": comp2_ref,
                            "distance": distance,
                        },
                    )
                )

        # Check for components outside typical bounds
        if self._components:
            out_of_bounds = self._find_components_out_of_bounds()
            for component_ref, position in out_of_bounds:
                issues.append(
                    ValidationIssue(
                        category="positioning",
                        message=f"Component outside typical bounds: {component_ref} at {position}",
                        level="info",
                        context={"component": component_ref, "position": (position.x, position.y)},
                    )
                )

        return issues

    def validate_design_rules(self) -> List[ValidationIssue]:
        """
        Validate against design rules and best practices.

        Returns:
            List of design rule validation issues
        """
        issues = []

        # Check minimum wire spacing
        wire_spacing_issues = self._check_wire_spacing()
        issues.extend(wire_spacing_issues)

        # Check power and ground connections
        power_issues = self._check_power_connections()
        issues.extend(power_issues)

        # Check for missing bypass capacitors (simplified check)
        bypass_issues = self._check_bypass_capacitors()
        issues.extend(bypass_issues)

        return issues

    def validate_metadata(self) -> List[ValidationIssue]:
        """
        Validate schematic metadata and structure.

        Returns:
            List of metadata validation issues
        """
        issues = []

        # Check required metadata fields
        if not self._data.get("version"):
            issues.append(
                ValidationIssue(
                    category="metadata",
                    message="Missing KiCAD version information",
                    level="warning",
                    context={},
                )
            )

        if not self._data.get("generator"):
            issues.append(
                ValidationIssue(
                    category="metadata",
                    message="Missing generator information",
                    level="info",
                    context={},
                )
            )

        # Check title block
        title_block = self._data.get("title_block", {})
        if not title_block.get("title"):
            issues.append(
                ValidationIssue(
                    category="metadata", message="Missing schematic title", level="info", context={}
                )
            )

        # Check paper size
        from ..config import config

        paper = self._data.get("paper")
        if paper and paper not in config.paper.valid_sizes:
            issues.append(
                ValidationIssue(
                    category="metadata",
                    message=f"Non-standard paper size: {paper}",
                    level="info",
                    context={"paper": paper},
                )
            )

        return issues

    def get_validation_summary(self, issues: List[ValidationIssue]) -> Dict[str, Any]:
        """
        Generate validation summary statistics.

        Args:
            issues: List of validation issues

        Returns:
            Summary dictionary with counts and severity
        """
        summary = {
            "total_issues": len(issues),
            "error_count": len([i for i in issues if i.level == "error"]),
            "warning_count": len([i for i in issues if i.level == "warning"]),
            "info_count": len([i for i in issues if i.level == "info"]),
            "categories": {},
            "severity": "info",
        }

        # Count by category
        for issue in issues:
            category = issue.category
            if category not in summary["categories"]:
                summary["categories"][category] = 0
            summary["categories"][category] += 1

        # Determine overall severity
        if summary["error_count"] > 0:
            summary["severity"] = "error"
        elif summary["warning_count"] > 0:
            summary["severity"] = "warning"

        return summary

    def _initialize_validation_rules(self) -> Dict[str, callable]:
        """Initialize all validation rules."""
        return {
            "component_references": self.validate_component_references,
            "connectivity": self.validate_connectivity,
            "positioning": self.validate_positioning,
            "design_rules": self.validate_design_rules,
            "metadata": self.validate_metadata,
        }

    def _validate_reference_format(self, reference: str) -> bool:
        """Validate component reference format."""
        if not reference:
            return False

        # Must start with letter(s), followed by numbers
        if not reference[0].isalpha():
            return False

        # Find where numbers start
        alpha_end = 0
        for i, char in enumerate(reference):
            if char.isdigit():
                alpha_end = i
                break
        else:
            return False  # No numbers found

        # Check alpha part
        alpha_part = reference[:alpha_end]
        if not alpha_part.isalpha():
            return False

        # Check numeric part
        numeric_part = reference[alpha_end:]
        if not numeric_part.isdigit():
            return False

        return True

    def _find_unconnected_pins(self) -> List[Tuple[str, str]]:
        """Find component pins that are not connected to any wires."""
        unconnected = []

        if not self._components or not self._wires:
            return unconnected

        # Get all wire endpoints
        wire_points = set()
        for wire in self._wires:
            wire_points.add((wire.start.x, wire.start.y))
            wire_points.add((wire.end.x, wire.end.y))

        # Check each component pin
        for component in self._components:
            # This would need actual pin position calculation
            # Simplified for now - would use component's pin positions
            pass

        return unconnected

    def _find_floating_wires(self) -> List[str]:
        """Find wires that don't connect to any components."""
        floating = []

        if not self._wires or not self._components:
            return floating

        # This would need actual connectivity analysis
        # Simplified implementation
        return floating

    def _find_potential_short_circuits(self) -> List[Dict[str, Any]]:
        """Find potential short circuits in the design."""
        short_circuits = []

        # This would need sophisticated electrical analysis
        # Simplified implementation
        return short_circuits

    def _find_overlapping_components(self) -> List[Tuple[str, str, float]]:
        """Find components that are positioned too close together."""
        overlapping = []

        if not self._components:
            return overlapping

        components = list(self._components)
        min_distance = 10.0  # Minimum distance threshold

        for i, comp1 in enumerate(components):
            for comp2 in components[i + 1 :]:
                distance = comp1.position.distance_to(comp2.position)
                if distance < min_distance:
                    overlapping.append((comp1.reference, comp2.reference, distance))

        return overlapping

    def _find_components_out_of_bounds(self) -> List[Tuple[str, Point]]:
        """Find components positioned outside typical schematic bounds."""
        out_of_bounds = []

        if not self._components:
            return out_of_bounds

        # Define typical bounds (these could be configurable)
        min_x, min_y = 0, 0
        max_x, max_y = 1000, 1000  # Adjust based on paper size

        for component in self._components:
            pos = component.position
            if pos.x < min_x or pos.x > max_x or pos.y < min_y or pos.y > max_y:
                out_of_bounds.append((component.reference, pos))

        return out_of_bounds

    def _check_wire_spacing(self) -> List[ValidationIssue]:
        """Check minimum wire spacing requirements."""
        issues = []

        if not self._wires:
            return issues

        # This would check wire-to-wire spacing
        # Simplified implementation
        return issues

    def _check_power_connections(self) -> List[ValidationIssue]:
        """Check power and ground connection integrity."""
        issues = []

        if not self._components:
            return issues

        # Look for power components without proper connections
        # This would need symbol analysis to identify power pins
        # Simplified implementation
        return issues

    def _check_bypass_capacitors(self) -> List[ValidationIssue]:
        """Check for missing bypass capacitors near ICs."""
        issues = []

        if not self._components:
            return issues

        # Find ICs and check for nearby capacitors
        # This would need symbol analysis and proximity checking
        # Simplified implementation
        return issues
