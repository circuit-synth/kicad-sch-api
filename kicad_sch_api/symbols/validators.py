"""
Symbol validation for KiCAD symbol definitions.

Provides comprehensive validation for symbol definitions, inheritance chains,
and symbol data integrity.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

from ..library.cache import SymbolDefinition
from ..utils.validation import ValidationError, ValidationIssue
from .cache import ISymbolCache

logger = logging.getLogger(__name__)


class SymbolValidator:
    """
    Comprehensive validator for symbol definitions and inheritance.

    Provides detailed validation with specific error reporting for
    symbol issues that could affect schematic generation.
    """

    def __init__(self, cache: Optional[ISymbolCache] = None):
        """
        Initialize symbol validator.

        Args:
            cache: Optional symbol cache for inheritance validation
        """
        self._cache = cache
        self._validation_rules = self._initialize_validation_rules()

    def validate_symbol(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """
        Validate a symbol definition comprehensively.

        Args:
            symbol: Symbol to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Run all validation rules
        for rule_name, rule_func in self._validation_rules.items():
            try:
                rule_issues = rule_func(symbol)
                issues.extend(rule_issues)
            except Exception as e:
                issues.append(
                    ValidationIssue(
                        category="validation",
                        message=f"Validation rule '{rule_name}' failed: {e}",
                        level="error",
                        context={"symbol": symbol.lib_id, "rule": rule_name},
                    )
                )

        return issues

    def validate_lib_id(self, lib_id: str) -> bool:
        """
        Validate library ID format.

        Args:
            lib_id: Library identifier to validate

        Returns:
            True if lib_id format is valid
        """
        if not lib_id or not isinstance(lib_id, str):
            return False

        if ":" not in lib_id:
            return False

        parts = lib_id.split(":")
        if len(parts) != 2:
            return False

        library_name, symbol_name = parts
        return bool(library_name.strip() and symbol_name.strip())

    def validate_inheritance_chain(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """
        Validate symbol inheritance chain for cycles and missing parents.

        Args:
            symbol: Symbol to validate inheritance for

        Returns:
            List of inheritance-related validation issues
        """
        issues = []

        if not symbol.extends:
            return issues

        if not self._cache:
            issues.append(
                ValidationIssue(
                    category="inheritance",
                    message="Cannot validate inheritance without cache",
                    level="warning",
                    context={"symbol": symbol.lib_id},
                )
            )
            return issues

        # Check for inheritance chain issues
        visited = set()
        current_lib_id = symbol.lib_id

        while current_lib_id:
            if current_lib_id in visited:
                issues.append(
                    ValidationIssue(
                        category="inheritance",
                        message=f"Circular inheritance detected in chain starting from {symbol.lib_id}",
                        level="error",
                        context={"symbol": symbol.lib_id, "cycle_point": current_lib_id},
                    )
                )
                break

            visited.add(current_lib_id)
            current_symbol = self._cache.get_symbol(current_lib_id)

            if not current_symbol:
                issues.append(
                    ValidationIssue(
                        category="inheritance",
                        message=f"Missing symbol in inheritance chain: {current_lib_id}",
                        level="error",
                        context={"symbol": symbol.lib_id, "missing": current_lib_id},
                    )
                )
                break

            if not current_symbol.extends:
                break

            # Resolve parent lib_id
            parent_name = current_symbol.extends
            if ":" in parent_name:
                current_lib_id = parent_name
            else:
                current_lib_id = f"{current_symbol.library}:{parent_name}"

            # Check if parent exists
            if not self._cache.has_symbol(current_lib_id):
                issues.append(
                    ValidationIssue(
                        category="inheritance",
                        message=f"Parent symbol not found: {current_lib_id}",
                        level="error",
                        context={"symbol": symbol.lib_id, "parent": current_lib_id},
                    )
                )
                break

        return issues

    def validate_symbol_integrity(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """
        Validate symbol data integrity and consistency.

        Args:
            symbol: Symbol to validate

        Returns:
            List of integrity validation issues
        """
        issues = []

        # Validate pin integrity
        pin_issues = self._validate_pins(symbol)
        issues.extend(pin_issues)

        # Validate graphic elements
        graphics_issues = self._validate_graphics(symbol)
        issues.extend(graphics_issues)

        # Validate units
        units_issues = self._validate_units(symbol)
        issues.extend(units_issues)

        return issues

    def _initialize_validation_rules(self) -> Dict[str, callable]:
        """Initialize all validation rules."""
        return {
            "lib_id_format": self._validate_lib_id_format,
            "required_fields": self._validate_required_fields,
            "reference_prefix": self._validate_reference_prefix,
            "pin_consistency": self._validate_pin_consistency,
            "pin_details": self._validate_pins,
            "unit_consistency": self._validate_unit_consistency,
            "unit_details": self._validate_units,
            "extends_format": self._validate_extends_format,
        }

    def _validate_lib_id_format(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """Validate lib_id format."""
        issues = []

        if not self.validate_lib_id(symbol.lib_id):
            issues.append(
                ValidationIssue(
                    category="lib_id",
                    message=f"Invalid lib_id format: {symbol.lib_id}",
                    level="error",
                    context={"symbol": symbol.lib_id},
                )
            )

        return issues

    def _validate_required_fields(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """Validate required symbol fields."""
        issues = []

        if not symbol.name:
            issues.append(
                ValidationIssue(
                    category="required_fields",
                    message="Symbol name is required",
                    level="error",
                    context={"symbol": symbol.lib_id},
                )
            )

        if not symbol.library:
            issues.append(
                ValidationIssue(
                    category="required_fields",
                    message="Symbol library is required",
                    level="error",
                    context={"symbol": symbol.lib_id},
                )
            )

        if not symbol.reference_prefix:
            issues.append(
                ValidationIssue(
                    category="required_fields",
                    message="Symbol reference prefix is missing",
                    level="warning",
                    context={"symbol": symbol.lib_id},
                )
            )

        return issues

    def _validate_reference_prefix(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """Validate reference prefix format."""
        issues = []

        if symbol.reference_prefix:
            # Check for invalid characters
            invalid_chars = set(symbol.reference_prefix) - set(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
            )
            if invalid_chars:
                issues.append(
                    ValidationIssue(
                        category="reference_prefix",
                        message=f"Reference prefix contains invalid characters: {invalid_chars}",
                        level="warning",
                        context={"symbol": symbol.lib_id, "prefix": symbol.reference_prefix},
                    )
                )

            # Check for common patterns
            if symbol.reference_prefix.lower() in ["u", "ic"] and not symbol.description:
                issues.append(
                    ValidationIssue(
                        category="reference_prefix",
                        message="Generic IC prefix 'U' - consider adding description",
                        level="info",
                        context={"symbol": symbol.lib_id},
                    )
                )

        return issues

    def _validate_pin_consistency(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """Validate pin consistency and numbering."""
        issues = []

        if not symbol.pins:
            issues.append(
                ValidationIssue(
                    category="symbol",
                    level="warning",
                    message="Symbol has no pins defined",
                    context={"symbol": symbol.lib_id},
                )
            )
            return issues

        # Check for duplicate pin numbers
        pin_numbers = [pin.number for pin in symbol.pins]
        duplicates = set([num for num in pin_numbers if pin_numbers.count(num) > 1])

        if duplicates:
            issues.append(
                ValidationIssue(
                    category="symbol",
                    level="error",
                    message=f"Duplicate pin numbers found: {duplicates}",
                    context={"symbol": symbol.lib_id, "duplicates": list(duplicates)},
                )
            )

        # Check for pins with same position
        pin_positions = [(pin.position.x, pin.position.y) for pin in symbol.pins]
        for i, pos1 in enumerate(pin_positions):
            for j, pos2 in enumerate(pin_positions[i + 1 :], i + 1):
                if pos1 == pos2:
                    issues.append(
                        ValidationIssue(
                            category="symbol",
                            level="warning",
                            message=f"Pins at same position: {symbol.pins[i].number} and {symbol.pins[j].number}",
                            context={"symbol": symbol.lib_id, "position": pos1},
                        )
                    )

        return issues

    def _validate_unit_consistency(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """Validate unit consistency."""
        issues = []

        if symbol.units < 1:
            issues.append(
                ValidationIssue(
                    category="symbol",
                    level="error",
                    message=f"Invalid unit count: {symbol.units}",
                    context={"symbol": symbol.lib_id},
                )
            )

        # Check unit names consistency
        if symbol.unit_names:
            for unit_num in symbol.unit_names:
                if unit_num < 1 or unit_num > symbol.units:
                    issues.append(
                        ValidationIssue(
                            category="symbol",
                            level="warning",
                            message=f"Unit name defined for invalid unit number: {unit_num}",
                            context={"symbol": symbol.lib_id, "unit": unit_num},
                        )
                    )

        return issues

    def _validate_extends_format(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """Validate extends directive format."""
        issues = []

        if symbol.extends is not None:
            # Check extends format
            if not symbol.extends.strip():
                issues.append(
                    ValidationIssue(
                        category="symbol",
                        level="error",
                        message="Empty extends directive",
                        context={"symbol": symbol.lib_id},
                    )
                )

            # Check for self-reference
            if symbol.extends == symbol.name:
                issues.append(
                    ValidationIssue(
                        category="symbol",
                        level="error",
                        message="Symbol cannot extend itself",
                        context={"symbol": symbol.lib_id},
                    )
                )

        return issues

    def _validate_pins(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """Validate pin definitions."""
        issues = []

        for pin in symbol.pins:
            # Validate pin number
            if not pin.number:
                issues.append(
                    ValidationIssue(
                        category="symbol",
                        level="error",
                        message="Pin missing number",
                        context={"symbol": symbol.lib_id},
                    )
                )

            # Validate pin name
            if not pin.name:
                issues.append(
                    ValidationIssue(
                        category="symbol",
                        level="warning",
                        message=f"Pin {pin.number} missing name",
                        context={"symbol": symbol.lib_id, "pin": pin.number},
                    )
                )

            # Validate pin type
            if not hasattr(pin, "pin_type") or not pin.pin_type:
                issues.append(
                    ValidationIssue(
                        category="symbol",
                        level="warning",
                        message=f"Pin {pin.number} missing pin type",
                        context={"symbol": symbol.lib_id, "pin": pin.number},
                    )
                )

        return issues

    def _validate_graphics(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """Validate graphic elements."""
        issues = []

        if not symbol.graphic_elements:
            issues.append(
                ValidationIssue(
                    category="symbol",
                    level="info",
                    message="Symbol has no graphic elements",
                    context={"symbol": symbol.lib_id},
                )
            )

        # Could add more graphic validation here
        # - Check for overlapping elements
        # - Validate coordinate ranges
        # - Check fill/stroke consistency

        return issues

    def _validate_units(self, symbol: SymbolDefinition) -> List[ValidationIssue]:
        """Validate unit definitions."""
        issues = []

        # Check if pins are distributed across units correctly
        if symbol.units > 1:
            unit_pins = {}
            for pin in symbol.pins:
                unit = getattr(pin, "unit", 1)
                if unit not in unit_pins:
                    unit_pins[unit] = []
                unit_pins[unit].append(pin)

            # Check for empty units
            for unit_num in range(1, symbol.units + 1):
                if unit_num not in unit_pins:
                    issues.append(
                        ValidationIssue(
                            category="symbol",
                            level="warning",
                            message=f"Unit {unit_num} has no pins",
                            context={"symbol": symbol.lib_id, "unit": unit_num},
                        )
                    )

        return issues

    def get_validation_summary(self, issues: List[ValidationIssue]) -> Dict[str, Any]:
        """
        Get validation summary statistics.

        Args:
            issues: List of validation issues

        Returns:
            Summary dictionary with issue counts and severity
        """
        summary = {
            "total_issues": len(issues),
            "error_count": len([i for i in issues if i.level.value == "error"]),
            "warning_count": len([i for i in issues if i.level.value == "warning"]),
            "info_count": len([i for i in issues if i.level.value == "info"]),
            "severity": (
                "error"
                if any(i.level.value == "error" for i in issues)
                else "warning" if any(i.level.value == "warning" for i in issues) else "info"
            ),
        }

        return summary
