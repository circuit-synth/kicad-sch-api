"""
Exception hierarchy for kicad-sch-api.

Provides a structured exception hierarchy for better error handling and debugging.
All exceptions inherit from the base KiCadSchError class.
"""

from typing import TYPE_CHECKING, Any, List, Optional

# Import validation types for type hints
# ValidationLevel is imported at runtime in methods that need it
if TYPE_CHECKING:
    from ..utils.validation import ValidationIssue


class KiCadSchError(Exception):
    """Base exception for all kicad-sch-api errors."""

    pass


class ValidationError(KiCadSchError):
    """
    Raised when validation fails.

    Supports rich error context with field/value information and can collect
    multiple validation issues.
    """

    def __init__(
        self,
        message: str,
        issues: Optional[List["ValidationIssue"]] = None,
        field: str = "",
        value: Any = None,
    ):
        """
        Initialize validation error with context.

        Args:
            message: Error message describing the validation failure
            issues: List of validation issues (for collecting multiple errors)
            field: The field name that failed validation
            value: The invalid value that was provided
        """
        self.issues = issues or []
        self.field = field
        self.value = value
        super().__init__(message)

    def add_issue(self, issue: "ValidationIssue") -> None:
        """Add a validation issue to this error."""
        self.issues.append(issue)

    def get_errors(self) -> List["ValidationIssue"]:
        """Get only error-level issues."""
        # Import here to avoid circular dependency
        from ..utils.validation import ValidationLevel

        return [
            issue
            for issue in self.issues
            if hasattr(issue, "level")
            and issue.level in (ValidationLevel.ERROR, ValidationLevel.CRITICAL)
        ]

    def get_warnings(self) -> List["ValidationIssue"]:
        """Get only warning-level issues."""
        # Import here to avoid circular dependency
        from ..utils.validation import ValidationLevel

        return [
            issue
            for issue in self.issues
            if hasattr(issue, "level") and issue.level == ValidationLevel.WARNING
        ]


class ReferenceError(ValidationError):
    """Raised when a component reference is invalid."""

    pass


class LibraryError(ValidationError):
    """Raised when a library or symbol reference is invalid."""

    pass


class GeometryError(ValidationError):
    """Raised when geometry validation fails (positions, shapes, dimensions)."""

    pass


class NetError(ValidationError):
    """Raised when a net specification or operation is invalid."""

    pass


class ParseError(KiCadSchError):
    """Raised when parsing a schematic file fails."""

    pass


class FormatError(KiCadSchError):
    """Raised when formatting a schematic file fails."""

    pass


class CollectionError(KiCadSchError):
    """Raised when a collection operation fails."""

    pass


class ElementNotFoundError(CollectionError):
    """Raised when an element is not found in a collection."""

    def __init__(self, message: str, element_type: str = "", identifier: str = ""):
        """
        Initialize element not found error.

        Args:
            message: Error message
            element_type: Type of element (e.g., 'component', 'wire', 'junction')
            identifier: The identifier used to search (e.g., 'R1', UUID)
        """
        self.element_type = element_type
        self.identifier = identifier
        super().__init__(message)


class DuplicateElementError(CollectionError):
    """Raised when attempting to add a duplicate element."""

    def __init__(self, message: str, element_type: str = "", identifier: str = ""):
        """
        Initialize duplicate element error.

        Args:
            message: Error message
            element_type: Type of element (e.g., 'component', 'wire', 'junction')
            identifier: The duplicate identifier (e.g., 'R1', UUID)
        """
        self.element_type = element_type
        self.identifier = identifier
        super().__init__(message)


class CollectionOperationError(CollectionError):
    """Raised when a collection operation fails for reasons other than not found/duplicate."""

    pass


class FileOperationError(KiCadSchError):
    """Raised when a file I/O operation fails."""

    pass


class CLIError(KiCadSchError):
    """Raised when KiCad CLI execution fails."""

    pass


class SchematicStateError(KiCadSchError):
    """
    Raised when an operation requires specific schematic state.

    Examples: schematic must be saved before export, etc.
    """

    pass
