"""
Main Electrical Rules Checker orchestrator.

Coordinates all validators and produces comprehensive ERC results.
"""

import time
from typing import TYPE_CHECKING, List, Optional

from kicad_sch_api.validation.erc_models import ERCConfig, ERCResult, ERCViolation
from kicad_sch_api.validation.validators import (
    BaseValidator,
    ComponentValidator,
    ConnectivityValidator,
    PinTypeValidator,
    PowerValidator,
)

if TYPE_CHECKING:
    from kicad_sch_api.core.schematic import Schematic


class ElectricalRulesChecker:
    """Main ERC orchestrator.

    Coordinates all validation checks and produces comprehensive results.

    Example:
        >>> import kicad_sch_api as ksa
        >>> from kicad_sch_api.validation import ElectricalRulesChecker
        >>>
        >>> sch = ksa.load_schematic("circuit.kicad_sch")
        >>> erc = ElectricalRulesChecker(sch)
        >>> result = erc.run_all_checks()
        >>>
        >>> if result.has_errors():
        ...     for error in result.errors:
        ...         print(f"ERROR: {error.message}")
    """

    def __init__(self, schematic: "Schematic", config: Optional[ERCConfig] = None) -> None:
        """Initialize ERC checker.

        Args:
            schematic: Schematic to validate
            config: Optional custom configuration
        """
        self.schematic = schematic
        self.config = config or ERCConfig()
        self.validators: List[BaseValidator] = []

        # Register default validators
        self._register_default_validators()

    def _register_default_validators(self) -> None:
        """Register default validators."""
        self.validators = [
            PinTypeValidator(self.schematic),
            ConnectivityValidator(self.schematic),
            ComponentValidator(self.schematic),
            PowerValidator(self.schematic),
        ]

    def add_validator(self, validator: BaseValidator) -> None:
        """Add custom validator.

        Args:
            validator: Custom validator to add
        """
        self.validators.append(validator)

    def run_all_checks(self) -> ERCResult:
        """Run all ERC checks.

        Returns:
            Complete ERC result with all violations
        """
        start_time = time.time()

        all_violations: List[ERCViolation] = []

        # Run each validator
        for validator in self.validators:
            violations = validator.validate()
            all_violations.extend(violations)

        # Apply configuration (severity overrides, suppression)
        all_violations = self._apply_config(all_violations)

        # Categorize by severity
        errors = [v for v in all_violations if v.severity == "error"]
        warnings = [v for v in all_violations if v.severity == "warning"]
        info = [v for v in all_violations if v.severity == "info"]

        # Calculate statistics
        total_checks = len(all_violations) + 100  # Placeholder
        passed_checks = total_checks - len(all_violations)

        duration_ms = (time.time() - start_time) * 1000

        return ERCResult(
            errors=errors,
            warnings=warnings,
            info=info,
            total_checks=total_checks,
            passed_checks=passed_checks,
            duration_ms=duration_ms,
        )

    def run_check(self, check_type: str) -> List[ERCViolation]:
        """Run specific check type.

        Args:
            check_type: Type of check ("pin_types", "connectivity", "components", "power")

        Returns:
            List of violations from that check

        Raises:
            ValueError: If check type is invalid
        """
        validator_map = {
            "pin_types": PinTypeValidator,
            "connectivity": ConnectivityValidator,
            "components": ComponentValidator,
            "power": PowerValidator,
        }

        if check_type not in validator_map:
            raise ValueError(f"Unknown check type: {check_type}")

        validator = validator_map[check_type](self.schematic)
        violations = validator.validate()

        return self._apply_config(violations)

    def _apply_config(self, violations: List[ERCViolation]) -> List[ERCViolation]:
        """Apply configuration to violations.

        Applies severity overrides and filters suppressed warnings.

        Args:
            violations: Raw violations

        Returns:
            Filtered and adjusted violations
        """
        result: List[ERCViolation] = []

        for violation in violations:
            # Check if suppressed
            is_suppressed = False
            for component_ref in violation.component_refs:
                if self.config.is_suppressed(violation.error_code, component_ref):
                    is_suppressed = True
                    break

            if is_suppressed:
                continue

            # Apply severity override
            if violation.violation_type in self.config.severity_overrides:
                violation.severity = self.config.severity_overrides[violation.violation_type]

            result.append(violation)

        return result
