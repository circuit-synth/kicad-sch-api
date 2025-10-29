"""Unit tests for exception hierarchy."""

import pytest
from kicad_sch_api.core.exceptions import (
    KiCadSchError,
    ValidationError,
    ReferenceError,
    LibraryError,
    GeometryError,
    NetError,
    ParseError,
    FormatError,
    CollectionError,
    ElementNotFoundError,
    DuplicateElementError,
    CollectionOperationError,
    FileOperationError,
    CLIError,
    SchematicStateError,
)
from kicad_sch_api.utils.validation import ValidationIssue, ValidationLevel


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy."""

    def test_base_exception_is_exception(self):
        """Test KiCadSchError inherits from Exception."""
        assert issubclass(KiCadSchError, Exception)

        error = KiCadSchError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_validation_error_inherits_from_base(self):
        """Test ValidationError inherits from KiCadSchError."""
        assert issubclass(ValidationError, KiCadSchError)
        assert issubclass(ValidationError, Exception)

    def test_specialized_validation_errors(self):
        """Test specialized validation errors inherit correctly."""
        assert issubclass(ReferenceError, ValidationError)
        assert issubclass(LibraryError, ValidationError)
        assert issubclass(GeometryError, ValidationError)
        assert issubclass(NetError, ValidationError)

    def test_collection_errors_inherit_from_base(self):
        """Test collection errors inherit from KiCadSchError."""
        assert issubclass(CollectionError, KiCadSchError)
        assert issubclass(ElementNotFoundError, CollectionError)
        assert issubclass(DuplicateElementError, CollectionError)
        assert issubclass(CollectionOperationError, CollectionError)

    def test_other_errors_inherit_from_base(self):
        """Test other errors inherit from KiCadSchError."""
        assert issubclass(ParseError, KiCadSchError)
        assert issubclass(FormatError, KiCadSchError)
        assert issubclass(FileOperationError, KiCadSchError)
        assert issubclass(CLIError, KiCadSchError)
        assert issubclass(SchematicStateError, KiCadSchError)


class TestValidationError:
    """Test ValidationError functionality."""

    def test_validation_error_basic(self):
        """Test basic ValidationError creation."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert error.issues == []

    def test_validation_error_with_issues_list(self):
        """Test ValidationError with issues list."""
        issue1 = ValidationIssue(
            category="test",
            message="Issue 1",
            level=ValidationLevel.ERROR
        )
        issue2 = ValidationIssue(
            category="test",
            message="Issue 2",
            level=ValidationLevel.WARNING
        )

        error = ValidationError("Validation failed", issues=[issue1, issue2])
        assert len(error.issues) == 2
        assert error.issues[0] == issue1
        assert error.issues[1] == issue2

    def test_validation_error_add_issue(self):
        """Test adding issues to ValidationError."""
        error = ValidationError("Validation failed")

        issue = ValidationIssue(
            category="test",
            message="New issue",
            level=ValidationLevel.ERROR
        )
        error.add_issue(issue)

        assert len(error.issues) == 1
        assert error.issues[0] == issue

    def test_validation_error_get_errors(self):
        """Test getting only error-level issues."""
        error = ValidationError("Validation failed")

        error.add_issue(ValidationIssue("test", "Error 1", ValidationLevel.ERROR))
        error.add_issue(ValidationIssue("test", "Warning 1", ValidationLevel.WARNING))
        error.add_issue(ValidationIssue("test", "Critical 1", ValidationLevel.CRITICAL))
        error.add_issue(ValidationIssue("test", "Info 1", ValidationLevel.INFO))

        errors = error.get_errors()
        assert len(errors) == 2  # ERROR and CRITICAL
        assert all(e.level in (ValidationLevel.ERROR, ValidationLevel.CRITICAL) for e in errors)

    def test_validation_error_get_warnings(self):
        """Test getting only warning-level issues."""
        error = ValidationError("Validation failed")

        error.add_issue(ValidationIssue("test", "Error 1", ValidationLevel.ERROR))
        error.add_issue(ValidationIssue("test", "Warning 1", ValidationLevel.WARNING))
        error.add_issue(ValidationIssue("test", "Warning 2", ValidationLevel.WARNING))

        warnings = error.get_warnings()
        assert len(warnings) == 2
        assert all(w.level == ValidationLevel.WARNING for w in warnings)

    def test_validation_error_with_field_and_value(self):
        """Test ValidationError with field and value context."""
        error = ValidationError("Invalid value", field="reference", value="R")
        assert error.field == "reference"
        assert error.value == "R"
        assert str(error) == "Invalid value"


class TestSpecializedValidationErrors:
    """Test specialized validation error classes."""

    def test_reference_error(self):
        """Test ReferenceError with context."""
        error = ReferenceError("Invalid reference", field="reference", value="R")
        assert isinstance(error, ValidationError)
        assert isinstance(error, KiCadSchError)
        assert error.field == "reference"
        assert error.value == "R"

    def test_library_error(self):
        """Test LibraryError."""
        error = LibraryError("Library not found", field="lib_id", value="Device:R")
        assert isinstance(error, ValidationError)
        assert error.field == "lib_id"
        assert error.value == "Device:R"

    def test_geometry_error(self):
        """Test GeometryError."""
        error = GeometryError("Invalid position", field="x", value=-1000)
        assert isinstance(error, ValidationError)
        assert error.field == "x"
        assert error.value == -1000

    def test_net_error(self):
        """Test NetError."""
        error = NetError("Net not found", field="net_name", value="VCC")
        assert isinstance(error, ValidationError)
        assert error.field == "net_name"
        assert error.value == "VCC"


class TestCollectionErrors:
    """Test collection-related exceptions."""

    def test_collection_error_basic(self):
        """Test basic CollectionError."""
        error = CollectionError("Collection operation failed")
        assert isinstance(error, KiCadSchError)
        assert str(error) == "Collection operation failed"

    def test_element_not_found_error(self):
        """Test ElementNotFoundError with context."""
        error = ElementNotFoundError(
            "Element not found",
            element_type="component",
            identifier="R1"
        )
        assert isinstance(error, CollectionError)
        assert error.element_type == "component"
        assert error.identifier == "R1"

    def test_element_not_found_error_minimal(self):
        """Test ElementNotFoundError without context."""
        error = ElementNotFoundError("Not found")
        assert error.element_type == ""
        assert error.identifier == ""

    def test_duplicate_element_error(self):
        """Test DuplicateElementError with context."""
        error = DuplicateElementError(
            "Duplicate element",
            element_type="component",
            identifier="R1"
        )
        assert isinstance(error, CollectionError)
        assert error.element_type == "component"
        assert error.identifier == "R1"

    def test_duplicate_element_error_minimal(self):
        """Test DuplicateElementError without context."""
        error = DuplicateElementError("Duplicate")
        assert error.element_type == ""
        assert error.identifier == ""

    def test_collection_operation_error(self):
        """Test CollectionOperationError."""
        error = CollectionOperationError("Operation failed")
        assert isinstance(error, CollectionError)


class TestOtherErrors:
    """Test other exception types."""

    def test_parse_error(self):
        """Test ParseError."""
        error = ParseError("Failed to parse S-expression")
        assert isinstance(error, KiCadSchError)
        assert str(error) == "Failed to parse S-expression"

    def test_format_error(self):
        """Test FormatError."""
        error = FormatError("Invalid file format")
        assert isinstance(error, KiCadSchError)
        assert str(error) == "Invalid file format"

    def test_file_operation_error(self):
        """Test FileOperationError."""
        error = FileOperationError("Failed to save file")
        assert isinstance(error, KiCadSchError)
        assert str(error) == "Failed to save file"

    def test_cli_error(self):
        """Test CLIError."""
        error = CLIError("KiCad CLI command failed")
        assert isinstance(error, KiCadSchError)
        assert str(error) == "KiCad CLI command failed"

    def test_schematic_state_error(self):
        """Test SchematicStateError."""
        error = SchematicStateError("Schematic must be saved before export")
        assert isinstance(error, KiCadSchError)
        assert str(error) == "Schematic must be saved before export"


class TestExceptionCatching:
    """Test exception catching patterns."""

    def test_catch_base_exception(self):
        """Test catching base exception catches all."""
        errors = [
            ValidationError("test"),
            ParseError("test"),
            CollectionError("test"),
            ElementNotFoundError("test"),
            CLIError("test"),
        ]

        for error in errors:
            try:
                raise error
            except KiCadSchError:
                pass  # Should catch all
            else:
                pytest.fail(f"Failed to catch {type(error).__name__} as KiCadSchError")

    def test_catch_validation_error_hierarchy(self):
        """Test catching ValidationError catches subclasses."""
        errors = [
            ReferenceError("test"),
            LibraryError("test"),
            GeometryError("test"),
            NetError("test"),
        ]

        for error in errors:
            try:
                raise error
            except ValidationError:
                pass  # Should catch all validation errors
            else:
                pytest.fail(f"Failed to catch {type(error).__name__} as ValidationError")

    def test_catch_collection_error_hierarchy(self):
        """Test catching CollectionError catches subclasses."""
        errors = [
            ElementNotFoundError("test"),
            DuplicateElementError("test"),
            CollectionOperationError("test"),
        ]

        for error in errors:
            try:
                raise error
            except CollectionError:
                pass  # Should catch all collection errors
            else:
                pytest.fail(f"Failed to catch {type(error).__name__} as CollectionError")

    def test_specific_exception_catching(self):
        """Test catching specific exceptions."""
        try:
            raise ElementNotFoundError("Component not found", "component", "R1")
        except ElementNotFoundError as e:
            assert e.element_type == "component"
            assert e.identifier == "R1"
        else:
            pytest.fail("Failed to catch ElementNotFoundError specifically")


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_validation_error_importable_from_utils(self):
        """Test ValidationError can be imported from utils.validation."""
        from kicad_sch_api.utils.validation import ValidationError as UtilsValidationError
        from kicad_sch_api.core.exceptions import ValidationError as CoreValidationError

        # Should be the same class
        assert UtilsValidationError is CoreValidationError

    def test_validation_issue_still_works(self):
        """Test ValidationIssue integration still works."""
        issue = ValidationIssue(
            category="test",
            message="Test issue",
            level=ValidationLevel.ERROR
        )

        error = ValidationError("Test", issues=[issue])
        assert len(error.issues) == 1
        assert error.issues[0] == issue
