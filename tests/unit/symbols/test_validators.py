"""
Unit tests for symbol validation.

Tests the SymbolValidator functionality for comprehensive symbol
validation and error reporting.
"""

import pytest
from unittest.mock import Mock

from kicad_sch_api.symbols.validators import SymbolValidator
from kicad_sch_api.symbols.cache import ISymbolCache
from kicad_sch_api.library.cache import SymbolDefinition
from kicad_sch_api.core.types import Point, SchematicPin, PinType
from kicad_sch_api.utils.validation import ValidationIssue


class MockCache(ISymbolCache):
    """Mock cache for testing validator."""

    def __init__(self):
        self.symbols = {}

    def get_symbol(self, lib_id: str):
        return self.symbols.get(lib_id)

    def has_symbol(self, lib_id: str) -> bool:
        return lib_id in self.symbols

    def add_library_path(self, library_path) -> bool:
        return True

    def get_library_symbols(self, library_name: str):
        return []

    def clear_cache(self) -> None:
        self.symbols.clear()

    def get_cache_statistics(self):
        return {}


class TestSymbolValidator:
    """Test cases for SymbolValidator."""

    def test_validator_initialization(self):
        """Test validator initializes correctly."""
        validator = SymbolValidator()

        assert validator._cache is None
        assert len(validator._validation_rules) > 0

    def test_validator_initialization_with_cache(self):
        """Test validator initialization with cache."""
        cache = MockCache()
        validator = SymbolValidator(cache)

        assert validator._cache is cache

    def test_validate_lib_id_valid(self):
        """Test validating valid lib_id."""
        validator = SymbolValidator()

        assert validator.validate_lib_id("Device:R") is True
        assert validator.validate_lib_id("MyLib:MySymbol") is True

    def test_validate_lib_id_invalid(self):
        """Test validating invalid lib_id."""
        validator = SymbolValidator()

        assert validator.validate_lib_id("NoColon") is False
        assert validator.validate_lib_id("") is False
        assert validator.validate_lib_id(None) is False
        assert validator.validate_lib_id("Too:Many:Colons") is False
        assert validator.validate_lib_id(":EmptyLibrary") is False
        assert validator.validate_lib_id("EmptySymbol:") is False

    def test_validate_symbol_basic(self):
        """Test basic symbol validation."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:R",
            name="R",
            library="Device",
            reference_prefix="R",
            description="Resistor",
            pins=[
                SchematicPin(
                    number="1",
                    name="Pin1",
                    position=Point(0, 0),
                    pin_type=PinType.PASSIVE
                ),
                SchematicPin(
                    number="2",
                    name="Pin2",
                    position=Point(1, 0),
                    pin_type=PinType.PASSIVE
                )
            ]
        )

        issues = validator.validate_symbol(symbol)

        # Should have minimal issues for a well-formed symbol
        error_issues = [i for i in issues if i.level.value == "error"]
        assert len(error_issues) == 0

    def test_validate_symbol_missing_required_fields(self):
        """Test validation with missing required fields."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Test:Empty",  # Valid format
            name="",    # Missing
            library="", # Missing
            reference_prefix="",  # Missing
        )

        issues = validator.validate_symbol(symbol)

        error_issues = [i for i in issues if i.level.value == "error"]
        assert len(error_issues) >= 1  # name is required (library gets auto-filled from lib_id)

    def test_validate_symbol_duplicate_pins(self):
        """Test validation with duplicate pin numbers."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:BadSymbol",
            name="BadSymbol",
            library="Device",
            reference_prefix="U",
            pins=[
                SchematicPin(
                    number="1",
                    name="Pin1",
                    position=Point(0, 0),
                    pin_type=PinType.INPUT
                ),
                SchematicPin(
                    number="1",  # Duplicate number
                    name="Pin1Dup",
                    position=Point(1, 0),
                    pin_type=PinType.OUTPUT
                )
            ]
        )

        issues = validator.validate_symbol(symbol)

        error_issues = [i for i in issues if i.level.value == "error"]
        duplicate_issues = [i for i in error_issues if "Duplicate pin" in i.message]
        assert len(duplicate_issues) >= 1

    def test_validate_symbol_pins_same_position(self):
        """Test validation with pins at same position."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:BadSymbol",
            name="BadSymbol",
            library="Device",
            reference_prefix="U",
            pins=[
                SchematicPin(
                    number="1",
                    name="Pin1",
                    position=Point(0, 0),
                    pin_type=PinType.INPUT
                ),
                SchematicPin(
                    number="2",
                    name="Pin2",
                    position=Point(0, 0),  # Same position
                    pin_type=PinType.OUTPUT
                )
            ]
        )

        issues = validator.validate_symbol(symbol)

        warning_issues = [i for i in issues if i.level.value == "warning"]
        position_issues = [i for i in warning_issues if "same position" in i.message]
        assert len(position_issues) >= 1

    def test_validate_symbol_no_pins(self):
        """Test validation with no pins."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:NoPins",
            name="NoPins",
            library="Device",
            reference_prefix="U",
            pins=[]
        )

        issues = validator.validate_symbol(symbol)

        warning_issues = [i for i in issues if i.level.value == "warning"]
        no_pins_issues = [i for i in warning_issues if "no pins" in i.message]
        assert len(no_pins_issues) >= 1

    def test_validate_symbol_invalid_units(self):
        """Test validation with invalid unit count."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:BadUnits",
            name="BadUnits",
            library="Device",
            reference_prefix="U",
            units=0  # Invalid
        )

        issues = validator.validate_symbol(symbol)

        error_issues = [i for i in issues if i.level.value == "error"]
        unit_issues = [i for i in error_issues if "Invalid unit count" in i.message]
        assert len(unit_issues) >= 1

    def test_validate_inheritance_chain_no_cache(self):
        """Test inheritance validation without cache."""
        validator = SymbolValidator()  # No cache

        symbol = SymbolDefinition(
            lib_id="Device:Child",
            name="Child",
            library="Device",
            reference_prefix="U",
            extends="Parent"
        )

        issues = validator.validate_inheritance_chain(symbol)

        warning_issues = [i for i in issues if i.level.value == "warning"]
        cache_issues = [i for i in warning_issues if "without cache" in i.message]
        assert len(cache_issues) == 1

    def test_validate_inheritance_chain_no_inheritance(self):
        """Test inheritance validation for symbol without inheritance."""
        cache = MockCache()
        validator = SymbolValidator(cache)

        symbol = SymbolDefinition(
            lib_id="Device:Simple",
            name="Simple",
            library="Device",
            reference_prefix="U",
            extends=None
        )

        issues = validator.validate_inheritance_chain(symbol)

        assert len(issues) == 0

    def test_validate_inheritance_chain_missing_parent(self):
        """Test inheritance validation with missing parent."""
        cache = MockCache()
        validator = SymbolValidator(cache)

        symbol = SymbolDefinition(
            lib_id="Device:Child",
            name="Child",
            library="Device",
            reference_prefix="U",
            extends="NonExistent"
        )
        cache.symbols["Device:Child"] = symbol  # Add symbol to cache

        issues = validator.validate_inheritance_chain(symbol)

        error_issues = [i for i in issues if i.level.value == "error"]
        parent_issues = [i for i in error_issues if "Parent symbol not found" in i.message]
        assert len(parent_issues) >= 1

    def test_validate_inheritance_chain_circular(self):
        """Test inheritance validation with circular inheritance."""
        cache = MockCache()
        validator = SymbolValidator(cache)

        # Create circular inheritance
        symbol_a = SymbolDefinition(
            lib_id="Device:A",
            name="A",
            library="Device",
            reference_prefix="U",
            extends="B"
        )
        cache.symbols["Device:A"] = symbol_a

        symbol_b = SymbolDefinition(
            lib_id="Device:B",
            name="B",
            library="Device",
            reference_prefix="U",
            extends="A"
        )
        cache.symbols["Device:B"] = symbol_b

        issues = validator.validate_inheritance_chain(symbol_a)

        error_issues = [i for i in issues if i.level.value == "error"]
        circular_issues = [i for i in error_issues if "Circular inheritance" in i.message]
        assert len(circular_issues) >= 1

    def test_validate_symbol_integrity(self):
        """Test complete symbol integrity validation."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:CompleteSymbol",
            name="CompleteSymbol",
            library="Device",
            reference_prefix="U",
            pins=[
                SchematicPin(
                    number="1",
                    name="Input",
                    position=Point(0, 0),
                    pin_type=PinType.INPUT
                )
            ],
            graphic_elements=[
                {"type": "rectangle", "points": [(0, 0), (1, 1)]}
            ],
            units=1,
            unit_names={1: "Main"}
        )

        issues = validator.validate_symbol_integrity(symbol)

        # Should have minimal issues for complete symbol
        error_issues = [i for i in issues if i.level.value == "error"]
        assert len(error_issues) == 0

    def test_validate_reference_prefix_invalid_chars(self):
        """Test reference prefix validation with invalid characters."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:BadPrefix",
            name="BadPrefix",
            library="Device",
            reference_prefix="R-1"  # Invalid character
        )

        issues = validator.validate_symbol(symbol)

        warning_issues = [i for i in issues if i.level.value == "warning"]
        prefix_issues = [i for i in warning_issues if "invalid characters" in i.message]
        assert len(prefix_issues) >= 1

    def test_validate_reference_prefix_generic_ic(self):
        """Test reference prefix validation for generic IC."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:GenericIC",
            name="GenericIC",
            library="Device",
            reference_prefix="U",
            description=""  # No description
        )

        issues = validator.validate_symbol(symbol)

        info_issues = [i for i in issues if i.level.value == "info"]
        generic_issues = [i for i in info_issues if "Generic IC prefix" in i.message]
        assert len(generic_issues) >= 1

    def test_validate_extends_format_empty(self):
        """Test validation of empty extends directive."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:BadExtends",
            name="BadExtends",
            library="Device",
            reference_prefix="U",
            extends=""  # Empty extends
        )

        issues = validator.validate_symbol(symbol)

        error_issues = [i for i in issues if i.level.value == "error"]
        extends_issues = [i for i in error_issues if "Empty extends" in i.message]
        assert len(extends_issues) >= 1

    def test_validate_extends_format_self_reference(self):
        """Test validation of self-referencing extends."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:SelfRef",
            name="SelfRef",
            library="Device",
            reference_prefix="U",
            extends="SelfRef"  # Self reference
        )

        issues = validator.validate_symbol(symbol)

        error_issues = [i for i in issues if i.level.value == "error"]
        self_ref_issues = [i for i in error_issues if "cannot extend itself" in i.message]
        assert len(self_ref_issues) >= 1

    def test_validate_pins_missing_details(self):
        """Test validation of pins with missing details."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:IncompletePins",
            name="IncompletePins",
            library="Device",
            reference_prefix="U",
            pins=[
                SchematicPin(
                    number="",  # Missing number
                    name="",    # Missing name
                    position=Point(0, 0),
                    pin_type=None  # Missing type
                )
            ]
        )

        issues = validator.validate_symbol(symbol)

        error_issues = [i for i in issues if i.level.value == "error"]
        warning_issues = [i for i in issues if i.level.value == "warning"]

        # Should have error for missing number
        number_issues = [i for i in error_issues if "missing number" in i.message]
        assert len(number_issues) >= 1

        # Should have warnings for missing name and type
        name_issues = [i for i in warning_issues if "missing name" in i.message]
        type_issues = [i for i in warning_issues if "missing pin type" in i.message]
        assert len(name_issues) >= 1
        assert len(type_issues) >= 1

    def test_validate_multi_unit_symbol(self):
        """Test validation of multi-unit symbol."""
        validator = SymbolValidator()

        symbol = SymbolDefinition(
            lib_id="Device:MultiUnit",
            name="MultiUnit",
            library="Device",
            reference_prefix="U",
            units=3,
            pins=[
                SchematicPin(
                    number="1",
                    name="Pin1",
                    position=Point(0, 0),
                    pin_type=PinType.INPUT
                ),
                SchematicPin(
                    number="2",
                    name="Pin2",
                    position=Point(1, 0),
                    pin_type=PinType.OUTPUT
                )
                # Unit 3 has no pins
            ],
            unit_names={1: "Unit A", 2: "Unit B"}  # Unit 3 missing name
        )

        issues = validator.validate_symbol(symbol)

        warning_issues = [i for i in issues if i.level.value == "warning"]
        empty_unit_issues = [i for i in warning_issues if "has no pins" in i.message]
        assert len(empty_unit_issues) >= 1

    def test_get_validation_summary(self):
        """Test getting validation summary."""
        validator = SymbolValidator()

        issues = [
            ValidationIssue(category="test", level="error", message="Error 1", context={}),
            ValidationIssue(category="test", level="error", message="Error 2", context={}),
            ValidationIssue(category="test", level="warning", message="Warning 1", context={}),
            ValidationIssue(category="test", level="info", message="Info 1", context={}),
        ]

        summary = validator.get_validation_summary(issues)

        assert summary["total_issues"] == 4
        assert summary["error_count"] == 2
        assert summary["warning_count"] == 1
        assert summary["info_count"] == 1
        assert summary["severity"] == "error"

    def test_get_validation_summary_warnings_only(self):
        """Test validation summary with only warnings."""
        validator = SymbolValidator()

        issues = [
            ValidationIssue(category="test", level="warning", message="Warning 1", context={}),
            ValidationIssue(category="test", level="info", message="Info 1", context={}),
        ]

        summary = validator.get_validation_summary(issues)

        assert summary["total_issues"] == 2
        assert summary["error_count"] == 0
        assert summary["warning_count"] == 1
        assert summary["info_count"] == 1
        assert summary["severity"] == "warning"

    def test_validation_rule_failure_handling(self):
        """Test handling of validation rule failures."""
        validator = SymbolValidator()

        # Mock a validation rule that raises an exception
        def failing_rule(symbol):
            raise ValueError("Rule failed")

        validator._validation_rules["failing_rule"] = failing_rule

        symbol = SymbolDefinition(
            lib_id="Device:Test",
            name="Test",
            library="Device",
            reference_prefix="U"
        )

        issues = validator.validate_symbol(symbol)

        error_issues = [i for i in issues if i.level.value == "error"]
        rule_failure_issues = [i for i in error_issues if "Rule failed" in i.message]
        assert len(rule_failure_issues) >= 1