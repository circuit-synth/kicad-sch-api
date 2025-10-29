"""
Text Element Manager for KiCAD schematic text operations.

Handles all text-related elements including labels, hierarchical labels,
global labels, text annotations, and text boxes while managing positioning
and validation.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from ..types import Point
from .base import BaseManager

logger = logging.getLogger(__name__)


class TextElementManager(BaseManager):
    """
    Manages text elements and labeling in KiCAD schematics.

    Responsible for:
    - Label creation and management (normal, hierarchical, global)
    - Text annotation placement
    - Text box management
    - Text effect and styling
    - Position validation and adjustment
    """

    def __init__(self, schematic_data: Dict[str, Any]):
        """
        Initialize TextElementManager.

        Args:
            schematic_data: Reference to schematic data
        """
        super().__init__(schematic_data)

    def add_label(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        effects: Optional[Dict[str, Any]] = None,
        uuid_str: Optional[str] = None,
        rotation: float = 0,
        size: Optional[float] = None,
    ) -> str:
        """
        Add a text label to the schematic.

        Args:
            text: Label text content
            position: Label position
            effects: Text effects (size, font, etc.)
            uuid_str: Optional UUID, generated if not provided
            rotation: Label rotation in degrees (default 0)
            size: Text size override (default from effects)

        Returns:
            UUID of created label
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if effects is None:
            effects = self._get_default_text_effects()

        # Override size if provided
        if size is not None:
            effects = dict(effects)  # Make a copy
            if "font" not in effects:
                effects["font"] = {}
            effects["font"]["size"] = [size, size]

        label_data = {
            "uuid": uuid_str,
            "text": text,
            "at": [position.x, position.y, rotation],  # KiCAD format: [x, y, rotation]
            "effects": effects,
        }

        # Add to schematic data
        if "label" not in self._data:
            self._data["label"] = []
        self._data["label"].append(label_data)

        logger.debug(f"Added label '{text}' at {position}")
        return uuid_str

    def add_hierarchical_label(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        shape: str = "input",
        effects: Optional[Dict[str, Any]] = None,
        uuid_str: Optional[str] = None,
    ) -> str:
        """
        Add a hierarchical label (for sheet connections).

        Args:
            text: Label text
            position: Label position
            shape: Shape type (input, output, bidirectional, tri_state, passive)
            effects: Text effects
            uuid_str: Optional UUID

        Returns:
            UUID of created hierarchical label
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if effects is None:
            effects = self._get_default_text_effects()

        valid_shapes = ["input", "output", "bidirectional", "tri_state", "passive"]
        if shape not in valid_shapes:
            logger.warning(f"Invalid hierarchical label shape: {shape}. Using 'input'")
            shape = "input"

        label_data = {
            "uuid": uuid_str,
            "text": text,
            "shape": shape,
            "at": [position.x, position.y, 0],
            "effects": effects,
        }

        # Add to schematic data
        if "hierarchical_label" not in self._data:
            self._data["hierarchical_label"] = []
        self._data["hierarchical_label"].append(label_data)

        logger.debug(f"Added hierarchical label '{text}' ({shape}) at {position}")
        return uuid_str

    def add_global_label(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        shape: str = "input",
        effects: Optional[Dict[str, Any]] = None,
        uuid_str: Optional[str] = None,
    ) -> str:
        """
        Add a global label (for project-wide connections).

        Args:
            text: Label text
            position: Label position
            shape: Shape type
            effects: Text effects
            uuid_str: Optional UUID

        Returns:
            UUID of created global label
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if effects is None:
            effects = self._get_default_text_effects()

        valid_shapes = ["input", "output", "bidirectional", "tri_state", "passive"]
        if shape not in valid_shapes:
            logger.warning(f"Invalid global label shape: {shape}. Using 'input'")
            shape = "input"

        label_data = {
            "uuid": uuid_str,
            "text": text,
            "shape": shape,
            "at": [position.x, position.y, 0],
            "effects": effects,
        }

        # Add to schematic data
        if "global_label" not in self._data:
            self._data["global_label"] = []
        self._data["global_label"].append(label_data)

        logger.debug(f"Added global label '{text}' ({shape}) at {position}")
        return uuid_str

    def add_text(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        effects: Optional[Dict[str, Any]] = None,
        uuid_str: Optional[str] = None,
    ) -> str:
        """
        Add free text annotation.

        Args:
            text: Text content
            position: Text position
            effects: Text effects
            uuid_str: Optional UUID

        Returns:
            UUID of created text
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if effects is None:
            effects = self._get_default_text_effects()

        text_data = {
            "uuid": uuid_str,
            "text": text,
            "at": [position.x, position.y, 0],
            "effects": effects,
        }

        # Add to schematic data
        if "text" not in self._data:
            self._data["text"] = []
        self._data["text"].append(text_data)

        logger.debug(f"Added text '{text}' at {position}")
        return uuid_str

    def add_text_box(
        self,
        text: str,
        position: Union[Point, Tuple[float, float]],
        size: Union[Point, Tuple[float, float]],
        rotation: float = 0.0,
        font_size: float = 1.27,
        margins: Optional[Tuple[float, float, float, float]] = None,
        stroke_width: Optional[float] = None,
        stroke_type: str = "solid",
        fill_type: str = "none",
        justify_horizontal: str = "left",
        justify_vertical: str = "top",
        exclude_from_sim: bool = False,
        effects: Optional[Dict[str, Any]] = None,
        stroke: Optional[Dict[str, Any]] = None,
        uuid_str: Optional[str] = None,
    ) -> str:
        """
        Add a text box with border.

        Args:
            text: Text content
            position: Top-left position
            size: Box size (width, height)
            rotation: Text rotation in degrees
            font_size: Text font size
            margins: Box margins (top, bottom, left, right)
            stroke_width: Border stroke width
            stroke_type: Border stroke type (solid, dash, etc.)
            fill_type: Fill type (none, outline, background)
            justify_horizontal: Horizontal justification
            justify_vertical: Vertical justification
            exclude_from_sim: Whether to exclude from simulation
            effects: Text effects (legacy, overrides font_size and justify if provided)
            stroke: Border stroke settings (legacy, overrides stroke_width/type if provided)
            uuid_str: Optional UUID

        Returns:
            UUID of created text box
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])
        if isinstance(size, tuple):
            size = Point(size[0], size[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if margins is None:
            margins = (0.9525, 0.9525, 0.9525, 0.9525)

        if stroke_width is None:
            stroke_width = 0

        # Build text_box_data matching parser format
        text_box_data = {
            "uuid": uuid_str,
            "text": text,
            "exclude_from_sim": exclude_from_sim,
            "position": {"x": position.x, "y": position.y},
            "rotation": rotation,
            "size": {"width": size.x, "height": size.y},
            "margins": margins,
            "stroke_width": stroke_width,
            "stroke_type": stroke_type,
            "fill_type": fill_type,
            "font_size": font_size,
            "justify_horizontal": justify_horizontal,
            "justify_vertical": justify_vertical,
        }

        # Add to schematic data (note: plural "text_boxes")
        if "text_boxes" not in self._data:
            self._data["text_boxes"] = []
        self._data["text_boxes"].append(text_box_data)

        logger.debug(f"Added text box '{text}' at {position}, size {size}")
        return uuid_str

    def remove_label(self, uuid_str: str) -> bool:
        """
        Remove a label by UUID.

        Args:
            uuid_str: UUID of label to remove

        Returns:
            True if label was removed, False if not found
        """
        return self._remove_text_element_by_uuid("label", uuid_str)

    def remove_hierarchical_label(self, uuid_str: str) -> bool:
        """
        Remove a hierarchical label by UUID.

        Args:
            uuid_str: UUID of label to remove

        Returns:
            True if label was removed, False if not found
        """
        return self._remove_text_element_by_uuid("hierarchical_label", uuid_str)

    def remove_global_label(self, uuid_str: str) -> bool:
        """
        Remove a global label by UUID.

        Args:
            uuid_str: UUID of label to remove

        Returns:
            True if label was removed, False if not found
        """
        return self._remove_text_element_by_uuid("global_label", uuid_str)

    def remove_text(self, uuid_str: str) -> bool:
        """
        Remove a text element by UUID.

        Args:
            uuid_str: UUID of text to remove

        Returns:
            True if text was removed, False if not found
        """
        return self._remove_text_element_by_uuid("text", uuid_str)

    def remove_text_box(self, uuid_str: str) -> bool:
        """
        Remove a text box by UUID.

        Args:
            uuid_str: UUID of text box to remove

        Returns:
            True if text box was removed, False if not found
        """
        return self._remove_text_element_by_uuid("text_boxes", uuid_str)

    def get_labels_at_position(
        self, position: Union[Point, Tuple[float, float]], tolerance: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Get all labels near a position.

        Args:
            position: Search position
            tolerance: Position tolerance

        Returns:
            List of matching label data
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        matches = []
        for label_type in ["label", "hierarchical_label", "global_label"]:
            labels = self._data.get(label_type, [])
            for label in labels:
                label_pos = Point(label["at"][0], label["at"][1])
                if label_pos.distance_to(position) <= tolerance:
                    matches.append(
                        {
                            "type": label_type,
                            "data": label,
                            "uuid": label.get("uuid"),
                            "text": label.get("text"),
                            "position": label_pos,
                        }
                    )

        return matches

    def update_text_effects(self, uuid_str: str, effects: Dict[str, Any]) -> bool:
        """
        Update text effects for any text element.

        Args:
            uuid_str: UUID of text element
            effects: New text effects

        Returns:
            True if updated, False if not found
        """
        for text_type in ["label", "hierarchical_label", "global_label", "text", "text_boxes"]:
            elements = self._data.get(text_type, [])
            for element in elements:
                if element.get("uuid") == uuid_str:
                    element["effects"] = effects
                    logger.debug(f"Updated text effects for {text_type} {uuid_str}")
                    return True

        logger.warning(f"Text element not found for UUID: {uuid_str}")
        return False

    def list_all_text_elements(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all text elements in the schematic.

        Returns:
            Dictionary with text element types and their data
        """
        result = {}
        for text_type in ["label", "hierarchical_label", "global_label", "text", "text_boxes"]:
            elements = self._data.get(text_type, [])
            result[text_type] = [
                {
                    "uuid": elem.get("uuid"),
                    "text": elem.get("text"),
                    "position": (
                        Point(elem["at"][0], elem["at"][1])
                        if "at" in elem
                        else (
                            Point(elem["position"]["x"], elem["position"]["y"])
                            if "position" in elem
                            else None
                        )
                    ),
                    "data": elem,
                }
                for elem in elements
            ]

        return result

    def get_text_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about text elements.

        Returns:
            Dictionary with text element statistics
        """
        stats = {}
        total_elements = 0

        for text_type in ["label", "hierarchical_label", "global_label", "text", "text_boxes"]:
            count = len(self._data.get(text_type, []))
            stats[text_type] = count
            total_elements += count

        stats["total_text_elements"] = total_elements
        return stats

    def _remove_text_element_by_uuid(self, element_type: str, uuid_str: str) -> bool:
        """Remove text element by UUID from specified type."""
        elements = self._data.get(element_type, [])
        for i, element in enumerate(elements):
            if element.get("uuid") == uuid_str:
                del elements[i]
                logger.debug(f"Removed {element_type}: {uuid_str}")
                return True
        return False

    def _get_default_text_effects(self) -> Dict[str, Any]:
        """Get default text effects configuration."""
        return {"font": {"size": [1.27, 1.27], "thickness": 0.254}, "justify": ["left"]}

    def validate_text_positions(self) -> List[str]:
        """
        Validate text element positions for overlaps and readability.

        Returns:
            List of validation warnings
        """
        warnings = []
        all_elements = []

        # Collect all text elements with positions
        for text_type in ["label", "hierarchical_label", "global_label", "text", "text_boxes"]:
            elements = self._data.get(text_type, [])
            for element in elements:
                if "at" in element:
                    position = Point(element["at"][0], element["at"][1])
                elif "position" in element:
                    position = Point(element["position"]["x"], element["position"]["y"])
                else:
                    continue
                all_elements.append(
                    {
                        "type": text_type,
                        "position": position,
                        "text": element.get("text", ""),
                        "uuid": element.get("uuid"),
                    }
                )

        # Check for overlapping elements
        overlap_threshold = 2.0  # Minimum distance
        for i, elem1 in enumerate(all_elements):
            for elem2 in all_elements[i + 1 :]:
                distance = elem1["position"].distance_to(elem2["position"])
                if distance < overlap_threshold:
                    warnings.append(
                        f"Text elements '{elem1['text']}' and '{elem2['text']}' "
                        f"are very close ({distance:.2f} units apart)"
                    )

        return warnings
