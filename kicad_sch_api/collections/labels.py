"""
Enhanced label management with IndexRegistry integration.

Provides LabelElement wrapper and LabelCollection using BaseCollection
infrastructure with text indexing and position-based queries.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.types import Label, Point
from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
from .base import BaseCollection, IndexSpec, ValidationLevel

logger = logging.getLogger(__name__)


class LabelElement:
    """
    Enhanced wrapper for schematic label elements.

    Provides intuitive access to label properties and operations
    while maintaining exact format preservation. All property
    modifications automatically notify the parent collection.
    """

    def __init__(self, label_data: Label, parent_collection: "LabelCollection"):
        """
        Initialize label element wrapper.

        Args:
            label_data: Underlying label data
            parent_collection: Parent collection for modification tracking
        """
        self._data = label_data
        self._collection = parent_collection
        self._validator = SchematicValidator()

    # Core properties with validation
    @property
    def uuid(self) -> str:
        """Label element UUID (read-only)."""
        return self._data.uuid

    @property
    def text(self) -> str:
        """Label text (net name)."""
        return self._data.text

    @text.setter
    def text(self, value: str):
        """
        Set label text with validation.

        Args:
            value: New label text

        Raises:
            ValidationError: If text is empty
        """
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Label text cannot be empty")

        old_text = self._data.text
        self._data.text = value.strip()
        self._collection._update_text_index(old_text, self)
        self._collection._mark_modified()
        logger.debug(f"Updated label text: '{old_text}' -> '{value}'")

    @property
    def position(self) -> Point:
        """Label position in schematic."""
        return self._data.position

    @position.setter
    def position(self, value: Union[Point, Tuple[float, float]]):
        """Set label position."""
        if isinstance(value, tuple):
            value = Point(value[0], value[1])
        elif not isinstance(value, Point):
            raise ValidationError(f"Position must be Point or tuple, got {type(value)}")

        self._data.position = value
        self._collection._mark_modified()

    @property
    def rotation(self) -> float:
        """Label rotation in degrees."""
        return self._data.rotation

    @rotation.setter
    def rotation(self, value: float):
        """Set label rotation."""
        self._data.rotation = float(value)
        self._collection._mark_modified()

    @property
    def size(self) -> float:
        """Label text size."""
        return self._data.size

    @size.setter
    def size(self, value: float):
        """
        Set label size with validation.

        Args:
            value: New text size

        Raises:
            ValidationError: If size is not positive
        """
        if value <= 0:
            raise ValidationError(f"Label size must be positive, got {value}")

        self._data.size = float(value)
        self._collection._mark_modified()

    # Utility methods
    def move(self, x: float, y: float):
        """Move label to absolute position."""
        self.position = Point(x, y)

    def translate(self, dx: float, dy: float):
        """Translate label by offset."""
        current = self.position
        self.position = Point(current.x + dx, current.y + dy)

    def rotate_by(self, angle: float):
        """Rotate label by angle (cumulative)."""
        self.rotation = (self.rotation + angle) % 360

    def validate(self) -> List[ValidationIssue]:
        """
        Validate this label element.

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        # Validate text is not empty
        if not self.text or not self.text.strip():
            issues.append(
                ValidationIssue(category="label", message="Label text is empty", level="error")
            )

        # Validate size is positive
        if self.size <= 0:
            issues.append(
                ValidationIssue(
                    category="label",
                    message=f"Label size must be positive, got {self.size}",
                    level="error",
                )
            )

        return issues

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert label to dictionary representation.

        Returns:
            Dictionary with label data
        """
        return {
            "text": self.text,
            "position": {"x": self.position.x, "y": self.position.y},
            "rotation": self.rotation,
            "size": self.size,
        }

    def __str__(self) -> str:
        """String representation for display."""
        return f"<Label '{self.text}' @ {self.position}>"

    def __repr__(self) -> str:
        """Detailed representation for debugging."""
        return f"LabelElement(text='{self.text}', pos={self.position}, rotation={self.rotation})"


class LabelCollection(BaseCollection[LabelElement]):
    """
    Label collection with text indexing and position queries.

    Inherits from BaseCollection for UUID indexing and adds label-specific
    functionality including text-based searches and filtering.

    Features:
    - Fast UUID lookup via IndexRegistry
    - Text-based label indexing
    - Position-based queries
    - Lazy index rebuilding
    - Batch mode support
    """

    def __init__(
        self,
        labels: Optional[List[Label]] = None,
        validation_level: ValidationLevel = ValidationLevel.NORMAL,
    ):
        """
        Initialize label collection.

        Args:
            labels: Initial list of label data
            validation_level: Validation level for operations
        """
        super().__init__(validation_level=validation_level)

        # Manual text index (non-unique - multiple labels can have same text)
        self._text_index: Dict[str, List[LabelElement]] = {}

        # Add initial labels
        if labels:
            with self.batch_mode():
                for label_data in labels:
                    label_element = LabelElement(label_data, self)
                    super().add(label_element)
                    self._add_to_text_index(label_element)

        logger.debug(f"LabelCollection initialized with {len(self)} labels")

    # BaseCollection abstract method implementations
    def _get_item_uuid(self, item: LabelElement) -> str:
        """Extract UUID from label element."""
        return item.uuid

    def _create_item(self, **kwargs) -> LabelElement:
        """Create a new label (not typically used directly)."""
        raise NotImplementedError("Use add() method to create labels")

    def _get_index_specs(self) -> List[IndexSpec]:
        """Get index specifications for label collection."""
        return [
            IndexSpec(
                name="uuid",
                key_func=lambda l: l.uuid,
                unique=True,
                description="UUID index for fast lookups",
            ),
        ]

    # Label-specific add method
    def add(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        rotation: float = 0.0,
        size: float = 1.27,
        justify_h: str = "left",
        justify_v: str = "bottom",
        uuid: Optional[str] = None,
    ) -> LabelElement:
        """
        Add a label to the collection.

        Args:
            text: Label text (net name)
            position: Label position
            rotation: Label rotation in degrees
            size: Text size
            justify_h: Horizontal justification ("left", "right", "center")
            justify_v: Vertical justification ("top", "bottom", "center")
            uuid: Optional UUID (auto-generated if not provided)

        Returns:
            LabelElement wrapper for the created label

        Raises:
            ValueError: If UUID already exists or text is empty
        """
        # Validate text
        if not text or not text.strip():
            raise ValueError("Label text cannot be empty")

        # Generate UUID if not provided
        if uuid is None:
            uuid = str(uuid_module.uuid4())
        else:
            # Check for duplicate
            self._ensure_indexes_current()
            if self._index_registry.has_key("uuid", uuid):
                raise ValueError(f"Label with UUID '{uuid}' already exists")

        # Convert position
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Create label data
        label_data = Label(
            uuid=uuid,
            text=text.strip(),
            position=position,
            rotation=rotation,
            size=size,
            justify_h=justify_h,
            justify_v=justify_v,
        )

        # Create label element wrapper
        label_element = LabelElement(label_data, self)

        # Add to collection
        super().add(label_element)

        # Add to text index
        self._add_to_text_index(label_element)

        logger.debug(f"Added label '{text}' at {position}, UUID={uuid}")
        return label_element

    # Remove operation (override to update text index)
    def remove(self, uuid: str) -> bool:
        """
        Remove label by UUID.

        Args:
            uuid: Label UUID to remove

        Returns:
            True if label was removed, False if not found
        """
        # Get label before removing
        label = self.get(uuid)
        if not label:
            return False

        # Remove from text index
        self._remove_from_text_index(label)

        # Remove from base collection
        result = super().remove(uuid)

        if result:
            logger.info(f"Removed label '{label.text}'")

        return result

    # Text-based queries
    def get_by_text(self, text: str) -> List[LabelElement]:
        """
        Find all labels with specific text.

        Args:
            text: Text to search for

        Returns:
            List of labels with matching text
        """
        return self._text_index.get(text, [])

    def filter_by_text_pattern(self, pattern: str) -> List[LabelElement]:
        """
        Find labels with text containing a pattern.

        Args:
            pattern: Text pattern to search for (case-insensitive)

        Returns:
            List of labels with matching text
        """
        pattern_lower = pattern.lower()
        matching = []

        for label in self._items:
            if pattern_lower in label.text.lower():
                matching.append(label)

        return matching

    # Position-based queries
    def get_at_position(
        self, position: Union[Point, Tuple[float, float]], tolerance: float = 0.01
    ) -> Optional[LabelElement]:
        """
        Find label at or near a specific position.

        Args:
            position: Position to search
            tolerance: Distance tolerance for matching

        Returns:
            Label if found, None otherwise
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        for label in self._items:
            if label.position.distance_to(position) <= tolerance:
                return label

        return None

    def get_near_point(
        self, point: Union[Point, Tuple[float, float]], radius: float
    ) -> List[LabelElement]:
        """
        Find all labels within radius of a point.

        Args:
            point: Center point
            radius: Search radius

        Returns:
            List of labels within radius
        """
        if isinstance(point, tuple):
            point = Point(point[0], point[1])

        matching = []
        for label in self._items:
            if label.position.distance_to(point) <= radius:
                matching.append(label)

        return matching

    # Validation
    def validate_all(self) -> List[ValidationIssue]:
        """
        Validate all labels in collection.

        Returns:
            List of validation issues found
        """
        all_issues = []

        for label in self._items:
            issues = label.validate()
            all_issues.extend(issues)

        return all_issues

    # Statistics
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get label collection statistics.

        Returns:
            Dictionary with label statistics
        """
        if not self._items:
            base_stats = super().get_statistics()
            base_stats.update(
                {
                    "total_labels": 0,
                    "unique_texts": 0,
                    "avg_size": 0,
                }
            )
            return base_stats

        unique_texts = len(self._text_index)
        avg_size = sum(l.size for l in self._items) / len(self._items)

        base_stats = super().get_statistics()
        base_stats.update(
            {
                "total_labels": len(self._items),
                "unique_texts": unique_texts,
                "avg_size": avg_size,
                "text_distribution": {
                    text: len(labels) for text, labels in self._text_index.items()
                },
            }
        )

        return base_stats

    # Internal helper methods
    def _add_to_text_index(self, label: LabelElement):
        """Add label to text index."""
        text = label.text
        if text not in self._text_index:
            self._text_index[text] = []
        self._text_index[text].append(label)

    def _remove_from_text_index(self, label: LabelElement):
        """Remove label from text index."""
        text = label.text
        if text in self._text_index:
            self._text_index[text].remove(label)
            if not self._text_index[text]:
                del self._text_index[text]

    def _update_text_index(self, old_text: str, label: LabelElement):
        """Update text index when label text changes."""
        # Remove from old text
        if old_text in self._text_index:
            self._text_index[old_text].remove(label)
            if not self._text_index[old_text]:
                del self._text_index[old_text]

        # Add to new text
        new_text = label.text
        if new_text not in self._text_index:
            self._text_index[new_text] = []
        self._text_index[new_text].append(label)

    # Compatibility methods
    @property
    def modified(self) -> bool:
        """Check if collection has been modified (compatibility)."""
        return self.is_modified

    def mark_saved(self) -> None:
        """Mark collection as saved (reset modified flag)."""
        self.mark_clean()
