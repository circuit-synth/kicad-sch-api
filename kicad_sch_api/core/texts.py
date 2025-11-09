"""
Text element management for KiCAD schematics.

This module provides collection classes for managing text elements,
featuring fast lookup, bulk operations, and validation.
"""

import logging
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
from .collections import BaseCollection
from .types import Point, Text

logger = logging.getLogger(__name__)


class TextElement:
    """
    Enhanced wrapper for schematic text elements with modern API.

    Provides intuitive access to text properties and operations
    while maintaining exact format preservation.
    """

    def __init__(self, text_data: Text, parent_collection: "TextCollection"):
        """
        Initialize text element wrapper.

        Args:
            text_data: Underlying text data
            parent_collection: Parent collection for updates
        """
        self._data = text_data
        self._collection = parent_collection
        self._validator = SchematicValidator()

    # Core properties with validation
    @property
    def uuid(self) -> str:
        """Text element UUID."""
        return self._data.uuid

    @property
    def text(self) -> str:
        """Text content."""
        return self._data.text

    @text.setter
    def text(self, value: str):
        """Set text content with validation."""
        if not isinstance(value, str):
            raise ValidationError(f"Text content must be string, got {type(value)}")
        self._data.text = value
        self._collection._mark_modified()

    @property
    def position(self) -> Point:
        """Text position."""
        return self._data.position

    @position.setter
    def position(self, value: Union[Point, Tuple[float, float]]):
        """Set text position."""
        if isinstance(value, tuple):
            value = Point(value[0], value[1])
        elif not isinstance(value, Point):
            raise ValidationError(f"Position must be Point or tuple, got {type(value)}")
        self._data.position = value
        self._collection._mark_modified()

    @property
    def rotation(self) -> float:
        """Text rotation in degrees."""
        return self._data.rotation

    @rotation.setter
    def rotation(self, value: float):
        """Set text rotation."""
        self._data.rotation = float(value)
        self._collection._mark_modified()

    @property
    def size(self) -> float:
        """Text size."""
        return self._data.size

    @size.setter
    def size(self, value: float):
        """Set text size with validation."""
        if value <= 0:
            raise ValidationError(f"Text size must be positive, got {value}")
        self._data.size = float(value)
        self._collection._mark_modified()

    @property
    def exclude_from_sim(self) -> bool:
        """Whether text is excluded from simulation."""
        return self._data.exclude_from_sim

    @exclude_from_sim.setter
    def exclude_from_sim(self, value: bool):
        """Set exclude from simulation flag."""
        self._data.exclude_from_sim = bool(value)
        self._collection._mark_modified()

    @property
    def bold(self) -> bool:
        """Text bold flag."""
        return getattr(self._data, "bold", False)

    @bold.setter
    def bold(self, value: bool) -> None:
        """Set text bold flag."""
        self._data.bold = bool(value)
        self._collection._mark_modified()

    @property
    def italic(self) -> bool:
        """Text italic flag."""
        return getattr(self._data, "italic", False)

    @italic.setter
    def italic(self, value: bool) -> None:
        """Set text italic flag."""
        self._data.italic = bool(value)
        self._collection._mark_modified()

    @property
    def thickness(self) -> Optional[float]:
        """Text stroke thickness."""
        return getattr(self._data, "thickness", None)

    @thickness.setter
    def thickness(self, value: Optional[float]) -> None:
        """Set text stroke thickness."""
        if value is not None and value <= 0:
            raise ValidationError(f"Thickness must be positive, got {value}")
        self._data.thickness = float(value) if value is not None else None
        self._collection._mark_modified()

    @property
    def color(self) -> Optional[Tuple[int, int, int, float]]:
        """Text color (RGBA)."""
        return getattr(self._data, "color", None)

    @color.setter
    def color(self, value: Optional[Tuple[int, int, int, float]]) -> None:
        """Set text color."""
        if value is not None:
            if len(value) != 4:
                raise ValidationError(f"Color must be RGBA tuple (4 values), got {len(value)}")
            r, g, b, a = value
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0 <= a <= 1):
                raise ValidationError("Color values out of range: RGB 0-255, A 0-1")
            value = (int(r), int(g), int(b), float(a))
        self._data.color = value
        self._collection._mark_modified()

    @property
    def face(self) -> Optional[str]:
        """Font face name."""
        return getattr(self._data, "face", None)

    @face.setter
    def face(self, value: Optional[str]) -> None:
        """Set font face name."""
        self._data.face = str(value) if value is not None else None
        self._collection._mark_modified()

    def validate(self) -> List[ValidationIssue]:
        """Validate this text element."""
        return self._validator.validate_text(self._data.__dict__)

    def to_dict(self) -> Dict[str, Any]:
        """Convert text element to dictionary representation."""
        result = {
            "uuid": self.uuid,
            "text": self.text,
            "position": {"x": self.position.x, "y": self.position.y},
            "rotation": self.rotation,
            "size": self.size,
            "exclude_from_sim": self.exclude_from_sim,
        }

        # Include optional font effects if set
        if self.bold:
            result["bold"] = self.bold
        if self.italic:
            result["italic"] = self.italic
        if self.thickness is not None:
            result["thickness"] = self.thickness
        if self.color is not None:
            result["color"] = self.color
        if self.face is not None:
            result["face"] = self.face

        return result

    def __str__(self) -> str:
        """String representation."""
        return f"<Text '{self.text}' @ {self.position}>"


class TextCollection(BaseCollection[TextElement]):
    """
    Collection class for efficient text element management.

    Inherits from BaseCollection for standard operations and adds text-specific
    functionality including content-based indexing.

    Provides fast lookup, filtering, and bulk operations for schematic text elements.
    """

    def __init__(self, texts: List[Text] = None):
        """
        Initialize text collection.

        Args:
            texts: Initial list of text data
        """
        # Initialize base collection with empty list (we'll add elements below)
        super().__init__([], collection_name="texts")

        # Additional text-specific index
        self._content_index: Dict[str, List[TextElement]] = {}

        # Add initial texts
        if texts:
            for text_data in texts:
                self._add_to_indexes(TextElement(text_data, self))

    def add(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        rotation: float = 0.0,
        size: float = 1.27,
        exclude_from_sim: bool = False,
        text_uuid: Optional[str] = None,
        # Font effects (new parameters)
        bold: bool = False,
        italic: bool = False,
        thickness: Optional[float] = None,
        color: Optional[Tuple[int, int, int, float]] = None,
        face: Optional[str] = None,
    ) -> TextElement:
        """
        Add a new text element to the schematic.

        Args:
            text: Text content
            position: Text position
            rotation: Text rotation in degrees
            size: Text size
            exclude_from_sim: Whether to exclude from simulation
            text_uuid: Specific UUID for text (auto-generated if None)
            bold: Bold font flag
            italic: Italic font flag
            thickness: Stroke width (None = use default)
            color: RGBA color tuple (None = use default)
            face: Font face name (None = use default)

        Returns:
            Newly created TextElement

        Raises:
            ValidationError: If text data is invalid
        """
        # Validate inputs
        if not isinstance(text, str) or not text.strip():
            raise ValidationError("Text content cannot be empty")

        if isinstance(position, tuple):
            position = Point(position[0], position[1])
        elif not isinstance(position, Point):
            raise ValidationError(f"Position must be Point or tuple, got {type(position)}")

        if size <= 0:
            raise ValidationError(f"Text size must be positive, got {size}")

        # Validate color if provided
        if color is not None:
            if len(color) != 4:
                raise ValidationError(f"Color must be RGBA tuple (4 values), got {len(color)}")
            r, g, b, a = color
            if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255 and 0 <= a <= 1):
                raise ValidationError("Color values out of range: RGB 0-255, A 0-1")
            color = (int(r), int(g), int(b), float(a))

        # Validate thickness if provided
        if thickness is not None and thickness <= 0:
            raise ValidationError(f"Thickness must be positive, got {thickness}")

        # Generate UUID if not provided
        if not text_uuid:
            text_uuid = str(uuid.uuid4())

        # Check for duplicate UUID
        if text_uuid in self._uuid_index:
            raise ValidationError(f"Text UUID {text_uuid} already exists")

        # Create text data with all properties
        text_data = Text(
            uuid=text_uuid,
            position=position,
            text=text,
            rotation=rotation,
            size=size,
            exclude_from_sim=exclude_from_sim,
            bold=bold,
            italic=italic,
            thickness=thickness,
            color=color,
            face=face,
        )

        # Create wrapper and add to collection
        text_element = TextElement(text_data, self)
        self._add_to_indexes(text_element)

        logger.debug(f"Added text: {text_element}")
        return text_element

    def remove(self, text_uuid: str) -> bool:
        """
        Remove text by UUID.

        Args:
            text_uuid: UUID of text to remove

        Returns:
            True if text was removed, False if not found
        """
        text_element = self.get(text_uuid)
        if not text_element:
            return False

        # Remove from content index
        content = text_element.text
        if content in self._content_index:
            self._content_index[content].remove(text_element)
            if not self._content_index[content]:
                del self._content_index[content]

        # Remove using base class method
        super().remove(text_uuid)

        logger.debug(f"Removed text: {text_element}")
        return True

    def find_by_content(self, content: str, exact: bool = True) -> List[TextElement]:
        """
        Find texts by content.

        Args:
            content: Content to search for
            exact: If True, exact match; if False, substring match

        Returns:
            List of matching text elements
        """
        if exact:
            return self._content_index.get(content, []).copy()
        else:
            matches = []
            for text_element in self._items:
                if content.lower() in text_element.text.lower():
                    matches.append(text_element)
            return matches

    def filter(self, predicate: Callable[[TextElement], bool]) -> List[TextElement]:
        """
        Filter texts by predicate function (delegates to base class find).

        Args:
            predicate: Function that returns True for texts to include

        Returns:
            List of texts matching predicate
        """
        return self.find(predicate)

    def bulk_update(self, criteria: Callable[[TextElement], bool], updates: Dict[str, Any]):
        """
        Update multiple texts matching criteria.

        Args:
            criteria: Function to select texts to update
            updates: Dictionary of property updates
        """
        updated_count = 0
        for text_element in self._items:
            if criteria(text_element):
                for prop, value in updates.items():
                    if hasattr(text_element, prop):
                        setattr(text_element, prop, value)
                        updated_count += 1

        if updated_count > 0:
            self._mark_modified()
            logger.debug(f"Bulk updated {updated_count} text properties")

    def clear(self):
        """Remove all texts from collection."""
        self._content_index.clear()
        super().clear()

    def _add_to_indexes(self, text_element: TextElement):
        """Add text to internal indexes (base + content index)."""
        self._add_item(text_element)

        # Add to content index
        content = text_element.text
        if content not in self._content_index:
            self._content_index[content] = []
        self._content_index[content].append(text_element)

    # Collection interface methods - __len__, __iter__, __getitem__ inherited from BaseCollection
    def __bool__(self) -> bool:
        """Return True if collection has texts."""
        return len(self._items) > 0
