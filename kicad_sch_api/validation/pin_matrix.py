"""
Pin Conflict Matrix for ERC validation.

Defines electrical compatibility rules between different pin types,
matching KiCAD's default ERC matrix.
"""

from enum import IntEnum
from typing import Dict, Tuple


class PinSeverity(IntEnum):
    """Severity levels for pin connections."""

    OK = 0
    WARNING = 1
    ERROR = 2


class PinConflictMatrix:
    """Pin type compatibility matrix.

    Defines which pin type combinations are OK, WARNING, or ERROR.
    Based on KiCAD's default ERC matrix.
    """

    # Pin type aliases for normalization
    PIN_TYPE_ALIASES = {
        "input": "input",
        "pt_input": "input",
        "i": "input",
        "output": "output",
        "pt_output": "output",
        "o": "output",
        "bidirectional": "bidirectional",
        "pt_bidi": "bidirectional",
        "bidi": "bidirectional",
        "b": "bidirectional",
        "tristate": "tristate",
        "pt_tristate": "tristate",
        "tri": "tristate",
        "t": "tristate",
        "passive": "passive",
        "pt_passive": "passive",
        "p": "passive",
        "free": "free",
        "nic": "free",
        "pt_nic": "free",
        "not_connected": "free",
        "f": "free",
        "unspecified": "unspecified",
        "pt_unspecified": "unspecified",
        "u": "unspecified",
        "power_input": "power_input",
        "pt_power_in": "power_input",
        "pwr_in": "power_input",
        "w": "power_input",
        "power_output": "power_output",
        "pt_power_out": "power_output",
        "pwr_out": "power_output",
        "open_collector": "open_collector",
        "pt_opencollector": "open_collector",
        "oc": "open_collector",
        "c": "open_collector",
        "open_emitter": "open_emitter",
        "pt_openemitter": "open_emitter",
        "oe": "open_emitter",
        "e": "open_emitter",
        "nc": "nc",
        "pt_nc": "nc",
        "not_connected": "nc",
        "n": "nc",
    }

    def __init__(self) -> None:
        """Initialize with KiCAD default matrix."""
        self.matrix = self.get_default_matrix()

    @staticmethod
    def get_default_matrix() -> Dict[Tuple[str, str], int]:
        """Get KiCAD default pin conflict matrix.

        Returns:
            Dictionary mapping (pin_type1, pin_type2) to severity
        """
        # Start with all combinations as OK
        matrix: Dict[Tuple[str, str], int] = {}

        # Define all pin types
        pin_types = [
            "input",
            "output",
            "bidirectional",
            "tristate",
            "passive",
            "free",
            "unspecified",
            "power_input",
            "power_output",
            "open_collector",
            "open_emitter",
            "nc",
        ]

        # Default: everything is OK
        for pin1 in pin_types:
            for pin2 in pin_types:
                matrix[(pin1, pin2)] = PinSeverity.OK
                matrix[(pin2, pin1)] = PinSeverity.OK  # Ensure symmetry

        # ERROR conditions (serious electrical conflicts)
        error_rules = [
            ("output", "output"),  # Multiple outputs driving same net
            ("power_output", "power_output"),  # Multiple power supplies shorted
            ("output", "power_output"),  # Logic output to power rail
            ("nc", "input"),  # NC pin should not connect
            ("nc", "output"),
            ("nc", "bidirectional"),
            ("nc", "tristate"),
            ("nc", "power_input"),
            ("nc", "power_output"),
            ("nc", "open_collector"),
            ("nc", "open_emitter"),
        ]

        for pin1, pin2 in error_rules:
            matrix[(pin1, pin2)] = PinSeverity.ERROR
            matrix[(pin2, pin1)] = PinSeverity.ERROR

        # WARNING conditions (potential issues)
        warning_rules = [
            ("unspecified", "input"),
            ("unspecified", "output"),
            ("unspecified", "bidirectional"),
            ("unspecified", "tristate"),
            ("unspecified", "passive"),
            ("unspecified", "power_input"),
            ("unspecified", "power_output"),
            ("unspecified", "open_collector"),
            ("unspecified", "open_emitter"),
            ("unspecified", "unspecified"),
            ("tristate", "output"),  # Tri-state with output can conflict
            ("tristate", "tristate"),  # Multiple tri-states
        ]

        for pin1, pin2 in warning_rules:
            matrix[(pin1, pin2)] = PinSeverity.WARNING
            matrix[(pin2, pin1)] = PinSeverity.WARNING

        # Passive is OK with everything (except NC which is already ERROR)
        for pin_type in pin_types:
            if pin_type != "nc":
                matrix[("passive", pin_type)] = PinSeverity.OK
                matrix[(pin_type, "passive")] = PinSeverity.OK

        # Free/NIC is OK with everything
        for pin_type in pin_types:
            matrix[("free", pin_type)] = PinSeverity.OK
            matrix[(pin_type, "free")] = PinSeverity.OK

        return matrix

    def normalize_pin_type(self, pin_type: str) -> str:
        """Normalize pin type string.

        Handles case-insensitive matching and aliases.

        Args:
            pin_type: Pin type string

        Returns:
            Normalized pin type

        Raises:
            ValueError: If pin type is invalid
        """
        normalized = pin_type.lower().strip()

        if normalized in self.PIN_TYPE_ALIASES:
            return self.PIN_TYPE_ALIASES[normalized]

        raise ValueError(f"Unknown pin type: {pin_type}")

    def check_connection(self, pin1_type: str, pin2_type: str) -> int:
        """Check if connection between two pin types is OK, WARNING, or ERROR.

        Args:
            pin1_type: First pin type
            pin2_type: Second pin type

        Returns:
            PinSeverity.OK, PinSeverity.WARNING, or PinSeverity.ERROR

        Raises:
            ValueError: If pin type is invalid
        """
        # Normalize pin types
        pin1 = self.normalize_pin_type(pin1_type)
        pin2 = self.normalize_pin_type(pin2_type)

        # Look up in matrix
        key = (pin1, pin2)
        if key in self.matrix:
            return self.matrix[key]

        # Should not happen if matrix is complete
        raise ValueError(f"No rule for pin combination: {pin1} + {pin2}")

    def set_rule(self, pin1_type: str, pin2_type: str, severity: int) -> None:
        """Set custom rule for pin type combination.

        Args:
            pin1_type: First pin type
            pin2_type: Second pin type
            severity: PinSeverity.OK, WARNING, or ERROR
        """
        pin1 = self.normalize_pin_type(pin1_type)
        pin2 = self.normalize_pin_type(pin2_type)

        if severity not in [PinSeverity.OK, PinSeverity.WARNING, PinSeverity.ERROR]:
            raise ValueError(f"Invalid severity: {severity}")

        # Set both directions for symmetry
        self.matrix[(pin1, pin2)] = severity
        self.matrix[(pin2, pin1)] = severity

    @classmethod
    def from_dict(cls, custom_matrix: Dict[Tuple[str, str], int]) -> "PinConflictMatrix":
        """Create matrix from custom dictionary.

        Args:
            custom_matrix: Dictionary of custom rules

        Returns:
            PinConflictMatrix with custom rules applied
        """
        matrix = cls()

        for (pin1, pin2), severity in custom_matrix.items():
            matrix.set_rule(pin1, pin2, severity)

        return matrix
