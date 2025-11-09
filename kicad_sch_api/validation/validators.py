"""
ERC validators: PinType, Connectivity, Component, Power.

Individual validators for different categories of electrical rules.
"""

import re
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple

from kicad_sch_api.validation.erc_models import ERCViolation
from kicad_sch_api.validation.pin_matrix import PinConflictMatrix, PinSeverity

if TYPE_CHECKING:
    from kicad_sch_api.core.schematic import Schematic


class BaseValidator:
    """Base class for ERC validators."""

    def __init__(self, schematic: "Schematic") -> None:
        """Initialize validator.

        Args:
            schematic: Schematic to validate
        """
        self.schematic = schematic

    def validate(self) -> List[ERCViolation]:
        """Run validation and return violations.

        Returns:
            List of violations found
        """
        raise NotImplementedError("Subclasses must implement validate()")


class PinTypeValidator(BaseValidator):
    """Validates pin-to-pin connections for electrical conflicts.

    Checks all nets for pin type compatibility using the pin conflict matrix.
    """

    def __init__(
        self, schematic: "Schematic", pin_matrix: Optional[PinConflictMatrix] = None
    ) -> None:
        """Initialize pin type validator.

        Args:
            schematic: Schematic to validate
            pin_matrix: Optional custom pin conflict matrix
        """
        super().__init__(schematic)
        self.pin_matrix = pin_matrix or PinConflictMatrix()

    def validate(self) -> List[ERCViolation]:
        """Validate pin connections on all nets.

        Returns:
            List of pin conflict violations
        """
        violations: List[ERCViolation] = []

        # Build nets from wires and components
        nets = self._build_nets()

        # Check each net for pin conflicts
        for net_name, pins in nets.items():
            net_violations = self._check_net_pins(net_name, pins)
            violations.extend(net_violations)

        return violations

    def _build_nets(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Build net connectivity map.

        Returns:
            Dict mapping net name to list of (component_ref, pin_num, pin_type) tuples
        """
        # TODO: Implement net tracing from wires and components
        # For now, return placeholder
        # This will be implemented when we have full net connectivity analysis
        return {}

    def _check_net_pins(
        self, net_name: str, pins: List[Tuple[str, str, str]]
    ) -> List[ERCViolation]:
        """Check all pin pairs on a net for conflicts.

        Args:
            net_name: Net name
            pins: List of (component_ref, pin_num, pin_type) tuples

        Returns:
            List of violations found on this net
        """
        violations: List[ERCViolation] = []

        # Check all pairs of pins
        for i, (ref1, pin1_num, pin1_type) in enumerate(pins):
            for ref2, pin2_num, pin2_type in pins[i + 1 :]:
                severity = self.pin_matrix.check_connection(pin1_type, pin2_type)

                if severity == PinSeverity.ERROR:
                    violations.append(
                        ERCViolation(
                            violation_type="pin_conflict",
                            severity="error",
                            message=f"Pin conflict: {pin1_type} ({ref1}) connected to {pin2_type} ({ref2})",
                            component_refs=[ref1, ref2],
                            net_name=net_name,
                            pin_numbers=[pin1_num, pin2_num],
                            error_code="E001",
                            suggested_fix=f"Remove one output or add buffer between {ref1} and {ref2}",
                        )
                    )
                elif severity == PinSeverity.WARNING:
                    violations.append(
                        ERCViolation(
                            violation_type="pin_conflict",
                            severity="warning",
                            message=f"Pin warning: {pin1_type} ({ref1}) connected to {pin2_type} ({ref2})",
                            component_refs=[ref1, ref2],
                            net_name=net_name,
                            pin_numbers=[pin1_num, pin2_num],
                            error_code="W005",
                            suggested_fix="Verify this connection is intentional",
                        )
                    )

        return violations


class ConnectivityValidator(BaseValidator):
    """Validates wire connectivity and net driving.

    Checks for dangling wires, unconnected pins, and undriven nets.
    """

    def validate(self) -> List[ERCViolation]:
        """Validate connectivity.

        Returns:
            List of connectivity violations
        """
        violations: List[ERCViolation] = []

        violations.extend(self.find_dangling_wires())
        violations.extend(self.find_unconnected_pins())
        violations.extend(self.find_undriven_nets())

        return violations

    def find_dangling_wires(self) -> List[ERCViolation]:
        """Find wires with only one connection.

        Returns:
            List of dangling wire violations
        """
        violations: List[ERCViolation] = []

        for wire in self.schematic.wires:
            # Check endpoints for connections
            start_connections = self._count_connections_at_point(wire.start)
            end_connections = self._count_connections_at_point(wire.end)

            if start_connections < 2 or end_connections < 2:
                violations.append(
                    ERCViolation(
                        violation_type="dangling_wire",
                        severity="warning",
                        message=f"Wire has unconnected endpoint at ({wire.start.x}, {wire.start.y})",
                        component_refs=[],
                        location=wire.start if start_connections < 2 else wire.end,
                        error_code="W002",
                        suggested_fix="Connect wire to component pin or remove if unused",
                    )
                )

        return violations

    def find_unconnected_pins(self) -> List[ERCViolation]:
        """Find input pins with no connections.

        Returns:
            List of unconnected pin violations
        """
        violations: List[ERCViolation] = []

        for component in self.schematic.components:
            # TODO: Get pin types from symbol library
            # For now, check if any pins have no wires
            pass

        return violations

    def find_undriven_nets(self) -> List[ERCViolation]:
        """Find nets with only input pins (no output driver).

        Returns:
            List of undriven net violations
        """
        violations: List[ERCViolation] = []

        # TODO: Implement net tracing and driver detection
        # This requires full net connectivity analysis

        return violations

    def _count_connections_at_point(self, point) -> int:
        """Count number of connections at a point.

        Args:
            point: Point to check

        Returns:
            Number of wires/pins at this point
        """
        # TODO: Implement proper connection counting
        # For now, return 2 (assume connected)
        return 2


class ComponentValidator(BaseValidator):
    """Validates component properties and references.

    Checks for duplicate references, missing values, invalid formats.
    """

    # Valid reference format: Letter(s) followed by number(s)
    REFERENCE_PATTERN = re.compile(r"^[A-Z]+[0-9]+$", re.IGNORECASE)

    def validate(self) -> List[ERCViolation]:
        """Validate components.

        Returns:
            List of component violations
        """
        violations: List[ERCViolation] = []

        violations.extend(self.find_duplicate_references())
        violations.extend(self.validate_component_properties())

        return violations

    def find_duplicate_references(self) -> List[ERCViolation]:
        """Find components with duplicate reference designators.

        Returns:
            List of duplicate reference violations
        """
        violations: List[ERCViolation] = []

        # Build reference count map
        ref_to_components: Dict[str, List[str]] = {}

        for component in self.schematic.components:
            ref = component.reference
            if ref not in ref_to_components:
                ref_to_components[ref] = []
            ref_to_components[ref].append(ref)

        # Find duplicates
        for ref, components in ref_to_components.items():
            if len(components) > 1:
                violations.append(
                    ERCViolation(
                        violation_type="duplicate_reference",
                        severity="error",
                        message=f"Duplicate reference designator: {ref}",
                        component_refs=[ref] * len(components),
                        error_code="E004",
                        suggested_fix=f"Rename duplicate components (e.g., {ref}, {ref}A, {ref}B)",
                    )
                )

        return violations

    def validate_component_properties(self) -> List[ERCViolation]:
        """Validate component properties (value, footprint, etc.).

        Returns:
            List of property violations
        """
        violations: List[ERCViolation] = []

        for component in self.schematic.components:
            # Check for missing value
            if not component.value or component.value.strip() == "":
                violations.append(
                    ERCViolation(
                        violation_type="missing_value",
                        severity="warning",
                        message=f"Component {component.reference} has no value",
                        component_refs=[component.reference],
                        error_code="W008",
                        suggested_fix=f"Add value to {component.reference}",
                    )
                )

            # Check for missing footprint
            if not component.footprint or component.footprint.strip() == "":
                violations.append(
                    ERCViolation(
                        violation_type="missing_footprint",
                        severity="warning",
                        message=f"Component {component.reference} has no footprint",
                        component_refs=[component.reference],
                        error_code="W007",
                        suggested_fix=f"Assign footprint to {component.reference}",
                    )
                )

            # Check reference format
            if not self.REFERENCE_PATTERN.match(component.reference):
                violations.append(
                    ERCViolation(
                        violation_type="invalid_reference",
                        severity="error",
                        message=f"Invalid reference format: {component.reference}",
                        component_refs=[component.reference],
                        error_code="E005",
                        suggested_fix="Use format like R1, U1, C1 (letter + number)",
                    )
                )

        return violations


class PowerValidator(BaseValidator):
    """Validates power supply connections.

    Checks for power flags, power input drivers, and power conflicts.
    """

    # Common power net names
    POWER_NET_NAMES = {
        "VCC",
        "VDD",
        "V+",
        "+5V",
        "+3V3",
        "+12V",
        "+24V",
        "GND",
        "GNDA",
        "GNDD",
        "VSS",
        "V-",
    }

    def validate(self) -> List[ERCViolation]:
        """Validate power connections.

        Returns:
            List of power violations
        """
        violations: List[ERCViolation] = []

        violations.extend(self.validate_power_flags())
        violations.extend(self.check_power_continuity())

        return violations

    def validate_power_flags(self) -> List[ERCViolation]:
        """Check for missing PWR_FLAG on power nets.

        Returns:
            List of missing power flag violations
        """
        violations: List[ERCViolation] = []

        # TODO: Implement power net detection and PWR_FLAG checking
        # This requires:
        # 1. Identify power nets (by name or power input pins)
        # 2. Check for PWR_FLAG symbol or power output on net
        # 3. Generate WARNING (not ERROR per requirements) if missing

        return violations

    def check_power_continuity(self) -> List[ERCViolation]:
        """Check that power inputs are driven by power outputs.

        Returns:
            List of power continuity violations
        """
        violations: List[ERCViolation] = []

        # TODO: Implement power driver checking
        # This requires full net tracing with pin type detection

        return violations

    def is_power_net(self, net_name: str) -> bool:
        """Check if net name suggests it's a power net.

        Args:
            net_name: Net name to check

        Returns:
            True if likely a power net
        """
        if not net_name:
            return False

        net_upper = net_name.upper().strip()

        # Check against known power names
        if net_upper in self.POWER_NET_NAMES:
            return True

        # Check for common patterns
        if any(pattern in net_upper for pattern in ["VCC", "VDD", "GND", "VSS"]):
            return True

        # Check for voltage patterns (+5V, +3.3V, etc.)
        if re.match(r"^\+?\d+\.?\d*V$", net_upper):
            return True

        return False
