"""
Label collection with specialized indexing and label-specific operations.

Extends the base IndexedCollection to provide label-specific features like
text indexing, position-based queries, and label type classification.
"""

import logging
import uuid as uuid_module
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.types import Point
from .base import IndexedCollection

logger = logging.getLogger(__name__)


class Label:
    """Label data structure."""

    def __init__(
        self,
        uuid: str,
        text: str,
        position: Point,
        rotation: float = 0.0,
        label_type: str = "label",
        effects: Optional[Dict[str, Any]] = None,
    ):
        self.uuid = uuid
        self.text = text
        self.position = position
        self.rotation = rotation
        self.label_type = label_type  # "label", "global_label", "hierarchical_label"
        self.effects = effects or {}

    def __repr__(self) -> str:
        return f"Label(text='{self.text}', pos={self.position}, type='{self.label_type}')"


class LabelCollection(IndexedCollection[Label]):
    """
    Collection class for efficient label management.

    Extends IndexedCollection with label-specific features:
    - Text indexing for finding labels by text content
    - Position indexing for spatial queries
    - Type classification (local, global, hierarchical)
    - Net name management
    - Connectivity analysis support
    """

    def __init__(self, labels: Optional[List[Label]] = None):
        """
        Initialize label collection.

        Args:
            labels: Initial list of labels
        """
        self._text_index: Dict[str, List[Label]] = {}
        self._position_index: Dict[Tuple[float, float], List[Label]] = {}
        self._type_index: Dict[str, List[Label]] = {}

        super().__init__(labels)

    # Abstract method implementations
    def _get_item_uuid(self, item: Label) -> str:
        """Extract UUID from label."""
        return item.uuid

    def _create_item(self, **kwargs) -> Label:
        """Create a new label with given parameters."""
        # This will be called by add() methods
        raise NotImplementedError("Use add() method instead")

    def _build_additional_indexes(self) -> None:
        """Build label-specific indexes."""
        # Clear existing indexes
        self._text_index.clear()
        self._position_index.clear()
        self._type_index.clear()

        # Rebuild indexes from current items
        for label in self._items:
            # Text index
            text_key = label.text.lower()  # Case-insensitive
            if text_key not in self._text_index:
                self._text_index[text_key] = []
            self._text_index[text_key].append(label)

            # Position index
            pos_key = (label.position.x, label.position.y)
            if pos_key not in self._position_index:
                self._position_index[pos_key] = []
            self._position_index[pos_key].append(label)

            # Type index
            if label.label_type not in self._type_index:
                self._type_index[label.label_type] = []
            self._type_index[label.label_type].append(label)

    # Label-specific methods
    def add(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        label_type: str = "label",
        rotation: float = 0.0,
        effects: Optional[Dict[str, Any]] = None,
        label_uuid: Optional[str] = None,
    ) -> Label:
        """
        Add a new label to the collection.

        Args:
            text: Label text content
            position: Label position
            label_type: Type of label ("label", "global_label", "hierarchical_label")
            rotation: Label rotation in degrees
            effects: Label effects (font, size, etc.)
            label_uuid: Specific UUID for label (auto-generated if None)

        Returns:
            Newly created Label

        Raises:
            ValueError: If invalid parameters provided
        """
        # Validate text
        if not text.strip():
            raise ValueError("Label text cannot be empty")

        # Convert tuple to Point if needed
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        # Validate label type
        valid_types = ["label", "global_label", "hierarchical_label"]
        if label_type not in valid_types:
            raise ValueError(f"Invalid label type: {label_type}. Must be one of {valid_types}")

        # Generate UUID if not provided
        if label_uuid is None:
            label_uuid = str(uuid_module.uuid4())

        # Create label
        label = Label(
            uuid=label_uuid,
            text=text,
            position=position,
            rotation=rotation,
            label_type=label_type,
            effects=effects or {},
        )

        # Add to collection using base class method
        return super().add(label)

    def get_labels_by_text(self, text: str, case_sensitive: bool = False) -> List[Label]:
        """
        Get all labels with specific text.

        Args:
            text: Text to search for
            case_sensitive: Whether search should be case sensitive

        Returns:
            List of matching labels
        """
        self._ensure_indexes_current()

        if case_sensitive:
            return [label for label in self._items if label.text == text]
        else:
            text_key = text.lower()
            return self._text_index.get(text_key, []).copy()

    def get_labels_at_position(
        self, position: Union[Point, Tuple[float, float]], tolerance: float = 0.0
    ) -> List[Label]:
        """
        Get all labels at a specific position.

        Args:
            position: Position to search at
            tolerance: Position tolerance for matching

        Returns:
            List of labels at the position
        """
        self._ensure_indexes_current()

        if isinstance(position, Point):
            pos_key = (position.x, position.y)
        else:
            pos_key = position

        if tolerance == 0.0:
            # Exact match
            return self._position_index.get(pos_key, []).copy()
        else:
            # Tolerance-based search
            matching_labels = []
            target_x, target_y = pos_key

            for label in self._items:
                dx = abs(label.position.x - target_x)
                dy = abs(label.position.y - target_y)
                distance = (dx**2 + dy**2) ** 0.5

                if distance <= tolerance:
                    matching_labels.append(label)

            return matching_labels

    def get_labels_by_type(self, label_type: str) -> List[Label]:
        """
        Get all labels of a specific type.

        Args:
            label_type: Type of labels to find

        Returns:
            List of labels of the specified type
        """
        self._ensure_indexes_current()
        return self._type_index.get(label_type, []).copy()

    def get_net_names(self) -> List[str]:
        """
        Get all unique net names from labels.

        Returns:
            List of unique net names
        """
        return list(set(label.text for label in self._items))

    def get_labels_for_net(self, net_name: str, case_sensitive: bool = False) -> List[Label]:
        """
        Get all labels for a specific net.

        Args:
            net_name: Net name to search for
            case_sensitive: Whether search should be case sensitive

        Returns:
            List of labels for the net
        """
        return self.get_labels_by_text(net_name, case_sensitive)

    def find_labels_in_region(
        self, min_x: float, min_y: float, max_x: float, max_y: float
    ) -> List[Label]:
        """
        Find all labels within a rectangular region.

        Args:
            min_x: Minimum X coordinate
            min_y: Minimum Y coordinate
            max_x: Maximum X coordinate
            max_y: Maximum Y coordinate

        Returns:
            List of labels in the region
        """
        matching_labels = []

        for label in self._items:
            if min_x <= label.position.x <= max_x and min_y <= label.position.y <= max_y:
                matching_labels.append(label)

        return matching_labels

    def update_label_text(self, label_uuid: str, new_text: str) -> bool:
        """
        Update the text of an existing label.

        Args:
            label_uuid: UUID of label to update
            new_text: New text content

        Returns:
            True if label was updated, False if not found

        Raises:
            ValueError: If new text is empty
        """
        if not new_text.strip():
            raise ValueError("Label text cannot be empty")

        label = self.get(label_uuid)
        if not label:
            return False

        # Update text
        label.text = new_text
        self._mark_modified()
        self._mark_indexes_dirty()

        logger.debug(f"Updated label {label_uuid} text to '{new_text}'")
        return True

    def update_label_position(
        self, label_uuid: str, new_position: Union[Point, Tuple[float, float]]
    ) -> bool:
        """
        Update the position of an existing label.

        Args:
            label_uuid: UUID of label to update
            new_position: New position

        Returns:
            True if label was updated, False if not found
        """
        label = self.get(label_uuid)
        if not label:
            return False

        # Convert tuple to Point if needed
        if isinstance(new_position, tuple):
            new_position = Point(new_position[0], new_position[1])

        # Update position
        label.position = new_position
        self._mark_modified()
        self._mark_indexes_dirty()

        logger.debug(f"Updated label {label_uuid} position to {new_position}")
        return True

    # Bulk operations
    def rename_net(self, old_name: str, new_name: str, case_sensitive: bool = False) -> int:
        """
        Rename all labels for a net.

        Args:
            old_name: Current net name
            new_name: New net name
            case_sensitive: Whether search should be case sensitive

        Returns:
            Number of labels renamed

        Raises:
            ValueError: If new name is empty
        """
        if not new_name.strip():
            raise ValueError("New net name cannot be empty")

        labels_to_rename = self.get_labels_by_text(old_name, case_sensitive)

        for label in labels_to_rename:
            label.text = new_name

        if labels_to_rename:
            self._mark_modified()
            self._mark_indexes_dirty()

        logger.info(f"Renamed {len(labels_to_rename)} labels from '{old_name}' to '{new_name}'")
        return len(labels_to_rename)

    def remove_labels_for_net(self, net_name: str, case_sensitive: bool = False) -> int:
        """
        Remove all labels for a specific net.

        Args:
            net_name: Net name to remove labels for
            case_sensitive: Whether search should be case sensitive

        Returns:
            Number of labels removed
        """
        labels_to_remove = self.get_labels_by_text(net_name, case_sensitive)

        for label in labels_to_remove:
            self.remove(label.uuid)

        logger.info(f"Removed {len(labels_to_remove)} labels for net '{net_name}'")
        return len(labels_to_remove)

    # Collection statistics
    def get_label_statistics(self) -> Dict[str, Any]:
        """
        Get label statistics for the collection.

        Returns:
            Dictionary with label statistics
        """
        stats = super().get_statistics()

        # Add label-specific statistics
        stats.update(
            {
                "unique_texts": len(self._text_index),
                "unique_positions": len(self._position_index),
                "label_types": {
                    label_type: len(labels) for label_type, labels in self._type_index.items()
                },
                "net_count": len(self.get_net_names()),
            }
        )

        return stats
