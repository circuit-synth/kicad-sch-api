"""Test exception import patterns work correctly."""


def test_all_import_paths_work():
    """Test exceptions can be imported from multiple valid paths."""
    # Core location (canonical)
    # Package level (convenience)
    from kicad_sch_api import ValidationError as PkgVE
    from kicad_sch_api.core.exceptions import ValidationError as CoreVE

    # Utils location (backward compatibility)
    from kicad_sch_api.utils.validation import ValidationError as UtilsVE

    # All should be the same class
    assert CoreVE is UtilsVE, "utils.validation should re-export core.exceptions.ValidationError"
    assert UtilsVE is PkgVE, "package level should export core.exceptions.ValidationError"
    assert CoreVE is PkgVE, "all imports should reference same ValidationError class"


def test_core_exports_all_exceptions():
    """Test all exceptions are exported from core module."""
    from kicad_sch_api.core import exceptions as exc

    # Should be able to access all exception classes
    assert hasattr(exc, "KiCadSchError")
    assert hasattr(exc, "ValidationError")
    assert hasattr(exc, "ReferenceError")
    assert hasattr(exc, "LibraryError")
    assert hasattr(exc, "GeometryError")
    assert hasattr(exc, "NetError")
    assert hasattr(exc, "ParseError")
    assert hasattr(exc, "FormatError")
    assert hasattr(exc, "CollectionError")
    assert hasattr(exc, "ElementNotFoundError")
    assert hasattr(exc, "DuplicateElementError")
    assert hasattr(exc, "CollectionOperationError")
    assert hasattr(exc, "FileOperationError")
    assert hasattr(exc, "CLIError")
    assert hasattr(exc, "SchematicStateError")


def test_core_init_exports():
    """Test exceptions can be imported from core package."""
    from kicad_sch_api.core import (
        DuplicateElementError,
        ElementNotFoundError,
        KiCadSchError,
        ValidationError,
    )

    # Should all be importable
    assert KiCadSchError is not None
    assert ValidationError is not None
    assert ElementNotFoundError is not None
    assert DuplicateElementError is not None


def test_package_level_common_exceptions():
    """Test commonly-used exceptions are exported at package level."""
    from kicad_sch_api import (
        DuplicateElementError,
        ElementNotFoundError,
        KiCadSchError,
        ValidationError,
    )

    # Should all be importable
    assert KiCadSchError is not None
    assert ValidationError is not None
    assert ElementNotFoundError is not None
    assert DuplicateElementError is not None


def test_exception_attributes_work():
    """Test both old and new exception patterns work."""
    from kicad_sch_api import ValidationError

    # Old pattern (should still work)
    error1 = ValidationError("test error")
    assert error1.issues == []

    # New pattern with field/value
    error2 = ValidationError("test", field="x", value=100)
    assert error2.field == "x"
    assert error2.value == 100

    # Backward compat: old code doesn't access new attributes
    error3 = ValidationError("test")
    assert hasattr(error3, "field")
    assert hasattr(error3, "value")
    assert error3.field == ""
    assert error3.value is None


def test_validation_issue_integration():
    """Test ValidationIssue still works with new ValidationError."""
    from kicad_sch_api import ValidationError, ValidationIssue
    from kicad_sch_api.utils.validation import ValidationLevel

    issue1 = ValidationIssue(category="test", message="Issue 1", level=ValidationLevel.ERROR)
    issue2 = ValidationIssue(category="test", message="Issue 2", level=ValidationLevel.WARNING)

    error = ValidationError("Validation failed", issues=[issue1, issue2])
    assert len(error.issues) == 2
    assert error.issues[0] == issue1
    assert error.issues[1] == issue2

    # Test get_errors and get_warnings
    errors = error.get_errors()
    warnings = error.get_warnings()
    assert len(errors) == 1
    assert len(warnings) == 1


def test_specialized_exceptions_importable():
    """Test specialized exceptions can be imported from core.exceptions."""
    from kicad_sch_api.core.exceptions import (
        CLIError,
        CollectionOperationError,
        FileOperationError,
        FormatError,
        GeometryError,
        LibraryError,
        NetError,
        ParseError,
        ReferenceError,
        SchematicStateError,
    )

    # All should be importable
    assert ReferenceError is not None
    assert LibraryError is not None
    assert GeometryError is not None
    assert NetError is not None
    assert ParseError is not None
    assert FormatError is not None
    assert CollectionOperationError is not None
    assert FileOperationError is not None
    assert CLIError is not None
    assert SchematicStateError is not None


def test_element_not_found_error_usage():
    """Test ElementNotFoundError works as expected."""
    from kicad_sch_api import ElementNotFoundError

    error = ElementNotFoundError("Component not found", element_type="component", identifier="R1")

    assert str(error) == "Component not found"
    assert error.element_type == "component"
    assert error.identifier == "R1"

    # Test it can be caught properly
    try:
        raise error
    except ElementNotFoundError as e:
        assert e.element_type == "component"
        assert e.identifier == "R1"
    else:
        assert False, "Should have caught ElementNotFoundError"


def test_duplicate_element_error_usage():
    """Test DuplicateElementError works as expected."""
    from kicad_sch_api import DuplicateElementError

    error = DuplicateElementError(
        "Component already exists", element_type="component", identifier="R1"
    )

    assert str(error) == "Component already exists"
    assert error.element_type == "component"
    assert error.identifier == "R1"

    # Test it can be caught properly
    try:
        raise error
    except DuplicateElementError as e:
        assert e.element_type == "component"
        assert e.identifier == "R1"
    else:
        assert False, "Should have caught DuplicateElementError"


def test_inheritance_chain():
    """Test exception inheritance works correctly."""
    from kicad_sch_api import (
        ElementNotFoundError,
        KiCadSchError,
        ValidationError,
    )
    from kicad_sch_api.core.exceptions import (
        CollectionError,
        ReferenceError,
    )

    # Test inheritance relationships
    assert issubclass(ValidationError, KiCadSchError)
    assert issubclass(ReferenceError, ValidationError)
    assert issubclass(CollectionError, KiCadSchError)
    assert issubclass(ElementNotFoundError, CollectionError)

    # Test catching base exception
    try:
        raise ValidationError("test")
    except KiCadSchError:
        pass  # Should catch
    else:
        assert False, "Should have caught as KiCadSchError"
