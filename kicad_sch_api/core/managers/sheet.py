"""
Sheet Manager for KiCAD hierarchical sheet operations.

Handles hierarchical sheet management, sheet pin connections, and
multi-sheet project coordination while maintaining sheet instance tracking.
"""

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..types import Point
from .base import BaseManager

logger = logging.getLogger(__name__)


class SheetManager(BaseManager):
    """
    Manages hierarchical sheets and multi-sheet project coordination.

    Responsible for:
    - Sheet creation and management
    - Sheet pin connections
    - Sheet instance tracking
    - Hierarchical navigation
    - Sheet file references
    """

    def __init__(self, schematic_data: Dict[str, Any]):
        """
        Initialize SheetManager.

        Args:
            schematic_data: Reference to schematic data
        """
        super().__init__(schematic_data)

    def add_sheet(
        self,
        name: str,
        filename: str,
        position: Union[Point, Tuple[float, float]],
        size: Union[Point, Tuple[float, float]],
        uuid_str: Optional[str] = None,
        sheet_pins: Optional[List[Dict[str, Any]]] = None,
        stroke_width: Optional[float] = None,
        stroke_type: str = "solid",
        project_name: Optional[str] = None,
        page_number: Optional[str] = None,
    ) -> str:
        """
        Add a hierarchical sheet to the schematic.

        Args:
            name: Sheet name/title
            filename: Referenced schematic filename
            position: Sheet position (top-left corner)
            size: Sheet size (width, height)
            uuid_str: Optional UUID
            sheet_pins: Optional list of sheet pins
            stroke_width: Border stroke width
            stroke_type: Border stroke type (solid, dashed, etc.)
            project_name: Project name for this sheet
            page_number: Page number for this sheet

        Returns:
            UUID of created sheet
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])
        if isinstance(size, tuple):
            size = Point(size[0], size[1])

        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        if sheet_pins is None:
            sheet_pins = []

        # Validate filename
        if not filename.endswith(".kicad_sch"):
            filename = f"{filename}.kicad_sch"

        sheet_data = {
            "uuid": uuid_str,
            "position": {"x": position.x, "y": position.y},
            "size": {"width": size.x, "height": size.y},
            "stroke_width": stroke_width if stroke_width is not None else 0.1524,
            "stroke_type": stroke_type,
            "fill_color": (0, 0, 0, 0.0),
            "name": name,
            "filename": filename,
            "exclude_from_sim": False,
            "in_bom": True,
            "on_board": True,
            "dnp": False,
            "fields_autoplaced": True,
            "pins": [],
            "project_name": project_name,
            "page_number": page_number if page_number else "2",
            "instances": [
                {"project": project_name, "path": f"/{uuid_str}", "reference": name, "unit": 1}
            ],
        }

        # Add sheet pins if provided (though usually added separately)
        if sheet_pins:
            sheet_data["pins"] = sheet_pins

        # Add to schematic data
        if "sheets" not in self._data:
            self._data["sheets"] = []
        self._data["sheets"].append(sheet_data)

        logger.debug(f"Added sheet '{name}' ({filename}) at {position}")
        return uuid_str

    def add_sheet_pin(
        self,
        sheet_uuid: str,
        name: str,
        pin_type: str,
        edge: str,
        position_along_edge: float,
        uuid_str: Optional[str] = None,
    ) -> Optional[str]:
        """
        Add a pin to an existing sheet using edge-based positioning.

        Args:
            sheet_uuid: UUID of target sheet
            name: Pin name
            pin_type: Pin type (input, output, bidirectional, tri_state, passive)
            edge: Edge to place pin on ("right", "bottom", "left", "top")
            position_along_edge: Distance along edge from reference corner (mm)
            uuid_str: Optional pin UUID

        Returns:
            UUID of created pin, or None if sheet not found

        Edge positioning (clockwise from right):
            - "right": rotation=0°, justify="right", position from top edge
            - "bottom": rotation=270°, justify="left", position from left edge
            - "left": rotation=180°, justify="left", position from bottom edge
            - "top": rotation=90°, justify="right", position from left edge
        """
        if uuid_str is None:
            uuid_str = str(uuid.uuid4())

        valid_pin_types = ["input", "output", "bidirectional", "tri_state", "passive"]
        if pin_type not in valid_pin_types:
            logger.warning(f"Invalid sheet pin type: {pin_type}. Using 'input'")
            pin_type = "input"

        valid_edges = ["right", "bottom", "left", "top"]
        if edge not in valid_edges:
            logger.error(f"Invalid edge: {edge}. Must be one of {valid_edges}")
            return None

        # Find the sheet
        sheets = self._data.get("sheets", [])
        for sheet in sheets:
            if sheet.get("uuid") == sheet_uuid:
                # Get sheet bounds
                sheet_x = sheet["position"]["x"]
                sheet_y = sheet["position"]["y"]
                sheet_width = sheet["size"]["width"]
                sheet_height = sheet["size"]["height"]

                # Calculate position, rotation, and justification based on edge
                # Clockwise: right (0°) → bottom (270°) → left (180°) → top (90°)
                if edge == "right":
                    x = sheet_x + sheet_width
                    y = sheet_y + position_along_edge
                    rotation = 0
                    justify = "right"
                elif edge == "bottom":
                    x = sheet_x + position_along_edge
                    y = sheet_y + sheet_height
                    rotation = 270
                    justify = "left"
                elif edge == "left":
                    x = sheet_x
                    y = sheet_y + sheet_height - position_along_edge
                    rotation = 180
                    justify = "left"
                elif edge == "top":
                    x = sheet_x + position_along_edge
                    y = sheet_y
                    rotation = 90
                    justify = "right"

                pin_data = {
                    "uuid": uuid_str,
                    "name": name,
                    "pin_type": pin_type,
                    "position": {"x": x, "y": y},
                    "rotation": rotation,
                    "size": 1.27,
                    "justify": justify,
                }

                # Add to sheet's pins array (already initialized in add_sheet)
                sheet["pins"].append(pin_data)

                logger.debug(
                    f"Added pin '{name}' to sheet {sheet_uuid} on {edge} edge at ({x}, {y})"
                )
                return uuid_str

        logger.warning(f"Sheet not found: {sheet_uuid}")
        return None

    def remove_sheet(self, sheet_uuid: str) -> bool:
        """
        Remove a sheet by UUID.

        Args:
            sheet_uuid: UUID of sheet to remove

        Returns:
            True if sheet was removed, False if not found
        """
        sheets = self._data.get("sheets", [])
        for i, sheet in enumerate(sheets):
            if sheet.get("uuid") == sheet_uuid:
                # Also remove from sheet instances
                self._remove_sheet_from_instances(sheet_uuid)
                del sheets[i]
                logger.debug(f"Removed sheet: {sheet_uuid}")
                return True

        logger.warning(f"Sheet not found for removal: {sheet_uuid}")
        return False

    def remove_sheet_pin(self, sheet_uuid: str, pin_uuid: str) -> bool:
        """
        Remove a pin from a sheet.

        Args:
            sheet_uuid: UUID of parent sheet
            pin_uuid: UUID of pin to remove

        Returns:
            True if pin was removed, False if not found
        """
        sheets = self._data.get("sheets", [])
        for sheet in sheets:
            if sheet.get("uuid") == sheet_uuid:
                pins = sheet.get("pins", [])
                for i, pin in enumerate(pins):
                    if pin.get("uuid") == pin_uuid:
                        del pins[i]
                        logger.debug(f"Removed pin {pin_uuid} from sheet {sheet_uuid}")
                        return True

        logger.warning(f"Sheet pin not found: {pin_uuid} in sheet {sheet_uuid}")
        return False

    def get_sheet_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find sheet by name.

        Args:
            name: Sheet name to find

        Returns:
            Sheet data or None if not found
        """
        sheets = self._data.get("sheets", [])
        for sheet in sheets:
            if sheet.get("name") == name:
                return sheet
        return None

    def get_sheet_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Find sheet by filename.

        Args:
            filename: Filename to find

        Returns:
            Sheet data or None if not found
        """
        # Normalize filename
        if not filename.endswith(".kicad_sch"):
            filename = f"{filename}.kicad_sch"

        sheets = self._data.get("sheets", [])
        for sheet in sheets:
            if sheet.get("filename") == filename:
                return sheet
        return None

    def list_sheet_pins(self, sheet_uuid: str) -> List[Dict[str, Any]]:
        """
        Get all pins for a sheet.

        Args:
            sheet_uuid: UUID of sheet

        Returns:
            List of pin data
        """
        sheets = self._data.get("sheets", [])
        for sheet in sheets:
            if sheet.get("uuid") == sheet_uuid:
                pins = sheet.get("pins", [])
                return [
                    {
                        "uuid": pin.get("uuid"),
                        "name": pin.get("name"),
                        "pin_type": pin.get("pin_type"),
                        "position": (
                            Point(pin["position"]["x"], pin["position"]["y"])
                            if "position" in pin
                            else None
                        ),
                        "data": pin,
                    }
                    for pin in pins
                ]
        return []

    def update_sheet_size(self, sheet_uuid: str, size: Union[Point, Tuple[float, float]]) -> bool:
        """
        Update sheet size.

        Args:
            sheet_uuid: UUID of sheet
            size: New size (width, height)

        Returns:
            True if updated, False if not found
        """
        if isinstance(size, tuple):
            size = Point(size[0], size[1])

        sheets = self._data.get("sheets", [])
        for sheet in sheets:
            if sheet.get("uuid") == sheet_uuid:
                sheet["size"] = {"width": size.x, "height": size.y}
                logger.debug(f"Updated sheet size: {sheet_uuid}")
                return True

        logger.warning(f"Sheet not found for size update: {sheet_uuid}")
        return False

    def update_sheet_position(
        self, sheet_uuid: str, position: Union[Point, Tuple[float, float]]
    ) -> bool:
        """
        Update sheet position.

        Args:
            sheet_uuid: UUID of sheet
            position: New position

        Returns:
            True if updated, False if not found
        """
        if isinstance(position, tuple):
            position = Point(position[0], position[1])

        sheets = self._data.get("sheets", [])
        for sheet in sheets:
            if sheet.get("uuid") == sheet_uuid:
                sheet["position"] = {"x": position.x, "y": position.y}
                logger.debug(f"Updated sheet position: {sheet_uuid}")
                return True

        logger.warning(f"Sheet not found for position update: {sheet_uuid}")
        return False

    def get_sheet_hierarchy(self) -> Dict[str, Any]:
        """
        Get hierarchical structure of all sheets.

        Returns:
            Dictionary representing sheet hierarchy
        """
        sheets = self._data.get("sheets", [])

        hierarchy = {"root": {"uuid": self._data.get("uuid"), "name": "Root Sheet", "children": []}}

        # Build sheet tree
        for sheet in sheets:
            sheet_info = {
                "uuid": sheet.get("uuid"),
                "name": sheet.get("name"),
                "filename": sheet.get("filename"),
                "pin_count": len(sheet.get("pins", [])),
                "position": (
                    Point(sheet["position"]["x"], sheet["position"]["y"])
                    if "position" in sheet
                    else None
                ),
                "size": (
                    Point(sheet["size"]["width"], sheet["size"]["height"])
                    if "size" in sheet
                    else None
                ),
            }
            hierarchy["root"]["children"].append(sheet_info)

        return hierarchy

    def validate_sheet_references(self) -> List[str]:
        """
        Validate sheet file references and connections.

        Returns:
            List of validation warnings
        """
        warnings = []
        sheets = self._data.get("sheets", [])

        for sheet in sheets:
            sheet_name = sheet.get("name", "Unknown")
            filename = sheet.get("filename")

            # Check filename format
            if filename and not filename.endswith(".kicad_sch"):
                warnings.append(f"Sheet '{sheet_name}' has invalid filename: {filename}")

            # Check for duplicate filenames
            filename_count = sum(1 for s in sheets if s.get("filename") == filename)
            if filename_count > 1:
                warnings.append(f"Duplicate sheet filename: {filename}")

            # Check sheet pins
            pins = sheet.get("pins", [])
            pin_names = [pin.get("name") for pin in pins]
            duplicate_pins = set([name for name in pin_names if pin_names.count(name) > 1])
            if duplicate_pins:
                warnings.append(f"Sheet '{sheet_name}' has duplicate pin names: {duplicate_pins}")

        return warnings

    def get_sheet_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about sheets in the schematic.

        Returns:
            Dictionary with sheet statistics
        """
        sheets = self._data.get("sheets", [])

        total_pins = sum(len(sheet.get("pins", [])) for sheet in sheets)
        sheet_instances = self._data.get("sheet_instances", [])

        return {
            "total_sheets": len(sheets),
            "total_sheet_pins": total_pins,
            "average_pins_per_sheet": total_pins / len(sheets) if sheets else 0,
            "sheet_instances": len(sheet_instances),
            "filenames": [sheet.get("filename") for sheet in sheets if sheet.get("filename")],
        }

    def _remove_sheet_from_instances(self, sheet_uuid: str) -> None:
        """Remove sheet from sheet instances tracking."""
        sheet_instances = self._data.get("sheet_instances", [])
        for i, instance in enumerate(sheet_instances):
            if instance.get("uuid") == sheet_uuid:
                del sheet_instances[i]
                break

    def add_sheet_instance(self, sheet_uuid: str, project: str, path: str, reference: str) -> None:
        """
        Add sheet instance tracking.

        Args:
            sheet_uuid: UUID of sheet
            project: Project identifier
            path: Hierarchical path
            reference: Sheet reference
        """
        if "sheet_instances" not in self._data:
            self._data["sheet_instances"] = []

        instance_data = {
            "uuid": sheet_uuid,
            "project": project,
            "path": path,
            "reference": reference,
        }

        self._data["sheet_instances"].append(instance_data)
        logger.debug(f"Added sheet instance: {reference} at {path}")
