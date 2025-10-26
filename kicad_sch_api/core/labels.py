"""
Label element management for KiCAD schematics.

This module provides collection classes for managing label elements,
featuring fast lookup, bulk operations, and validation.
"""

import logging
import uuid
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
from .types import Point, Label

logger = logging.getLogger(__name__)


class LabelElement:
    """
    Enhanced wrapper for schematic label elements with modern API.

    Provides intuitive access to label properties and operations
    while maintaining exact format preservation.
    """

    def __init__(self, label_data: Label, parent_collection: "LabelCollection"):
        """
        Initialize label element wrapper.

        Args:
            label_data: Underlying label data
            parent_collection: Parent collection for updates
        """
        self._data = label_data
        self._collection = parent_collection
        self._validator = SchematicValidator()

    # Core properties with validation
    @property
    def uuid(self) -> str:
        """Label element UUID."""
        return self._data.uuid

    @property
    def text(self) -> str:
        """Label text (net name)."""
        return self._data.text

    @text.setter
    def text(self, value: str):
        """Set label text with validation."""
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Label text cannot be empty")
        old_text = self._data.text
        self._data.text = value.strip()
        self._collection._update_text_index(old_text, self)
        self._collection._mark_modified()

    @property
    def position(self) -> Point:
        """Label position."""
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
        """Set label size with validation."""
        if value <= 0:
            raise ValidationError(f"Label size must be positive, got {value}")
        self._data.size = float(value)
        self._collection._mark_modified()

    def validate(self) -> List[ValidationIssue]:
        """Validate this label element."""
        return self._validator.validate_label(self._data.__dict__)

    def to_dict(self) -> Dict[str, Any]:
        """Convert label element to dictionary representation."""
        return {
            "uuid": self.uuid,
            "text": self.text,
            "position": {"x": self.position.x, "y": self.position.y},
            "rotation": self.rotation,
            "size": self.size,
        }

    def __str__(self) -> str:
        """String representation."""
        return f"<Label '{self.text}' @ {self.position}>"


class LabelCollection:
    """
    Collection class for efficient label element management.

    Provides fast lookup, filtering, and bulk operations for schematic label elements.
    """

    def __init__(self, labels: List[Label] = None):
        """
        Initialize label collection.

        Args:
            labels: Initial list of label data
        """
        self._labels: List[LabelElement] = []
        self._uuid_index: Dict[str, LabelElement] = {}
        self._text_index: Dict[str, List[LabelElement]] = {}
        self._modified = False

        # Add initial labels
        if labels:
            for label_data in labels:
                self._add_to_indexes(LabelElement(label_data, self))

        logger.debug(f"LabelCollection initialized with {len(self._labels)} labels")

    def add(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        rotation: float = 0.0,
        size: float = 1.27,
        label_uuid: Optional[str] = None,
    ) -> LabelElement:
        """
        Add a new label element to the schematic.

        Args:
            text: Label text (net name)
            position: Label position
            rotation: Label rotation in degrees
            size: Label text size
            label_uuid: Specific UUID for label (auto-generated if None)

        Returns:
            Newly created LabelElement

        Raises:
            ValidationError: If label data is invalid
        """
        # Validate inputs
        if not isinstance(text, str) or not text.strip():
            raise ValidationError("Label text cannot be empty")

        if isinstance(position, tuple):
            position = Point(position[0], position[1])
        elif not isinstance(position, Point):
            raise ValidationError(f"Position must be Point or tuple, got {type(position)}")

        if size <= 0:
            raise ValidationError(f"Label size must be positive, got {size}")

        # Generate UUID if not provided
        if not label_uuid:
            label_uuid = str(uuid.uuid4())

        # Check for duplicate UUID
        if label_uuid in self._uuid_index:
            raise ValidationError(f"Label UUID {label_uuid} already exists")

        # Create label data
        label_data = Label(
            uuid=label_uuid,
            position=position,
            text=text.strip(),
            rotation=rotation,
            size=size,
        )

        # Create wrapper and add to collection
        label_element = LabelElement(label_data, self)
        self._add_to_indexes(label_element)
        self._mark_modified()

        logger.debug(f"Added label: {label_element}")
        return label_element

    def get(self, label_uuid: str) -> Optional[LabelElement]:
        """Get label by UUID."""
        return self._uuid_index.get(label_uuid)

    def get_by_text(self, text: str) -> List[LabelElement]:
        """Get all labels with the given text."""
        return self._text_index.get(text, []).copy()

    def remove(self, label_uuid: str) -> bool:
        """
        Remove label by UUID.

        Args:
            label_uuid: UUID of label to remove

        Returns:
            True if label was removed, False if not found
        """
        label_element = self._uuid_index.get(label_uuid)
        if not label_element:
            return False

        # Remove from indexes
        self._remove_from_indexes(label_element)
        self._mark_modified()

        logger.debug(f"Removed label: {label_element}")
        return True

    def find_by_text(self, text: str, exact: bool = True) -> List[LabelElement]:
        """
        Find labels by text.

        Args:
            text: Text to search for
            exact: If True, exact match; if False, substring match

        Returns:
            List of matching label elements
        """
        if exact:
            return self._text_index.get(text, []).copy()
        else:
            matches = []
            for label_element in self._labels:
                if text.lower() in label_element.text.lower():
                    matches.append(label_element)
            return matches

    def filter(self, predicate: Callable[[LabelElement], bool]) -> List[LabelElement]:
        """
        Filter labels by predicate function.

        Args:
            predicate: Function that returns True for labels to include

        Returns:
            List of labels matching predicate
        """
        return [label for label in self._labels if predicate(label)]

    def bulk_update(self, criteria: Callable[[LabelElement], bool], updates: Dict[str, Any]):
        """
        Update multiple labels matching criteria.

        Args:
            criteria: Function to select labels to update
            updates: Dictionary of property updates
        """
        updated_count = 0
        for label_element in self._labels:
            if criteria(label_element):
                for prop, value in updates.items():
                    if hasattr(label_element, prop):
                        setattr(label_element, prop, value)
                        updated_count += 1

        if updated_count > 0:
            self._mark_modified()
            logger.debug(f"Bulk updated {updated_count} label properties")

    def clear(self):
        """Remove all labels from collection."""
        self._labels.clear()
        self._uuid_index.clear()
        self._text_index.clear()
        self._mark_modified()

    def _add_to_indexes(self, label_element: LabelElement):
        """Add label to internal indexes."""
        self._labels.append(label_element)
        self._uuid_index[label_element.uuid] = label_element

        # Add to text index
        text = label_element.text
        if text not in self._text_index:
            self._text_index[text] = []
        self._text_index[text].append(label_element)

    def _remove_from_indexes(self, label_element: LabelElement):
        """Remove label from internal indexes."""
        self._labels.remove(label_element)
        del self._uuid_index[label_element.uuid]

        # Remove from text index
        text = label_element.text
        if text in self._text_index:
            self._text_index[text].remove(label_element)
            if not self._text_index[text]:
                del self._text_index[text]

    def _update_text_index(self, old_text: str, label_element: LabelElement):
        """Update text index when label text changes."""
        # Remove from old text index
        if old_text in self._text_index:
            self._text_index[old_text].remove(label_element)
            if not self._text_index[old_text]:
                del self._text_index[old_text]

        # Add to new text index
        new_text = label_element.text
        if new_text not in self._text_index:
            self._text_index[new_text] = []
        self._text_index[new_text].append(label_element)

    def _mark_modified(self):
        """Mark collection as modified."""
        self._modified = True

    # Collection interface methods
    def __len__(self) -> int:
        """Return number of labels."""
        return len(self._labels)

    def __iter__(self) -> Iterator[LabelElement]:
        """Iterate over labels."""
        return iter(self._labels)

    def __getitem__(self, index: int) -> LabelElement:
        """Get label by index."""
        return self._labels[index]

    def __bool__(self) -> bool:
        """Return True if collection has labels."""
        return len(self._labels) > 0