"""
S-expression parser for KiCAD schematic files.

This module provides robust parsing and writing capabilities for KiCAD's S-expression format,
with exact format preservation and enhanced error handling.
"""

import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import sexpdata

from ..utils.validation import ValidationError, ValidationIssue
from .formatter import ExactFormatter
from .types import Junction, Label, Net, Point, SchematicSymbol, Wire

logger = logging.getLogger(__name__)


class SExpressionParser:
    """
    High-performance S-expression parser for KiCAD schematic files.

    Features:
    - Exact format preservation
    - Enhanced error handling with detailed validation
    - Optimized for large schematics
    - Support for KiCAD 9 format
    """

    def __init__(self, preserve_format: bool = True):
        """
        Initialize the parser.

        Args:
            preserve_format: If True, preserve exact formatting when writing
        """
        self.preserve_format = preserve_format
        self._formatter = ExactFormatter() if preserve_format else None
        self._validation_issues = []
        logger.info(f"S-expression parser initialized (format preservation: {preserve_format})")

    def parse_file(self, filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a KiCAD schematic file with comprehensive validation.

        Args:
            filepath: Path to the .kicad_sch file

        Returns:
            Parsed schematic data structure

        Raises:
            FileNotFoundError: If file doesn't exist
            ValidationError: If parsing fails or validation issues found
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Schematic file not found: {filepath}")

        logger.info(f"Parsing schematic file: {filepath}")

        try:
            # Read file content
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse S-expression
            sexp_data = self.parse_string(content)

            # Validate structure
            self._validate_schematic_structure(sexp_data, filepath)

            # Convert to internal format
            schematic_data = self._sexp_to_schematic_data(sexp_data)
            schematic_data["_original_content"] = content  # Store for format preservation
            schematic_data["_file_path"] = str(filepath)

            logger.info(
                f"Successfully parsed schematic with {len(schematic_data.get('components', []))} components"
            )
            return schematic_data

        except Exception as e:
            logger.error(f"Error parsing {filepath}: {e}")
            raise ValidationError(f"Failed to parse schematic: {e}") from e

    def parse_string(self, content: str) -> Any:
        """
        Parse S-expression content from string.

        Args:
            content: S-expression string content

        Returns:
            Parsed S-expression data structure

        Raises:
            ValidationError: If parsing fails
        """
        try:
            return sexpdata.loads(content)
        except Exception as e:
            raise ValidationError(f"Invalid S-expression format: {e}") from e

    def write_file(self, schematic_data: Dict[str, Any], filepath: Union[str, Path]):
        """
        Write schematic data to file with exact format preservation.

        Args:
            schematic_data: Schematic data structure
            filepath: Path to write to
        """
        filepath = Path(filepath)

        # Convert internal format to S-expression
        sexp_data = self._schematic_data_to_sexp(schematic_data)

        # Format content
        if self.preserve_format and "_original_content" in schematic_data:
            # Use format-preserving writer
            content = self._formatter.format_preserving_write(
                sexp_data, schematic_data["_original_content"]
            )
        else:
            # Standard S-expression formatting
            content = self.dumps(sexp_data)

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Schematic written to: {filepath}")

    def dumps(self, data: Any, pretty: bool = True) -> str:
        """
        Convert S-expression data to string.

        Args:
            data: S-expression data structure
            pretty: If True, format with proper indentation

        Returns:
            Formatted S-expression string
        """
        if pretty and self._formatter:
            return self._formatter.format(data)
        else:
            return sexpdata.dumps(data)

    def _validate_schematic_structure(self, sexp_data: Any, filepath: Path):
        """Validate the basic structure of a KiCAD schematic."""
        self._validation_issues.clear()

        if not isinstance(sexp_data, list) or len(sexp_data) == 0:
            self._validation_issues.append(
                ValidationIssue("structure", "Invalid schematic format: not a list", "error")
            )

        # Check for kicad_sch header
        if not (isinstance(sexp_data[0], sexpdata.Symbol) and str(sexp_data[0]) == "kicad_sch"):
            self._validation_issues.append(
                ValidationIssue("format", "Missing kicad_sch header", "error")
            )

        # Collect validation issues and raise if any errors found
        errors = [issue for issue in self._validation_issues if issue.level == "error"]
        if errors:
            error_messages = [f"{issue.category}: {issue.message}" for issue in errors]
            raise ValidationError(f"Validation failed: {'; '.join(error_messages)}")

    def _sexp_to_schematic_data(self, sexp_data: List[Any]) -> Dict[str, Any]:
        """Convert S-expression data to internal schematic format."""
        schematic_data = {
            "version": None,
            "generator": None,
            "generator_version": None,
            "uuid": None,
            "paper": None,
            "title_block": {},
            "components": [],
            "wires": [],
            "junctions": [],
            "labels": [],
            "hierarchical_labels": [],
            "no_connects": [],
            "texts": [],
            "text_boxes": [],
            "sheets": [],
            "polylines": [],
            "arcs": [],
            "circles": [],
            "beziers": [],
            "rectangles": [],
            "nets": [],
            "lib_symbols": {},
            "sheet_instances": [],
            "symbol_instances": [],
            "embedded_fonts": None,
        }

        # Process top-level elements
        for item in sexp_data[1:]:  # Skip kicad_sch header
            if not isinstance(item, list):
                continue

            if len(item) == 0:
                continue

            element_type = str(item[0]) if isinstance(item[0], sexpdata.Symbol) else None

            if element_type == "version":
                schematic_data["version"] = str(item[1]) if len(item) > 1 else None
            elif element_type == "generator":
                schematic_data["generator"] = item[1] if len(item) > 1 else None
            elif element_type == "generator_version":
                schematic_data["generator_version"] = item[1] if len(item) > 1 else None
            elif element_type == "paper":
                schematic_data["paper"] = item[1] if len(item) > 1 else None
            elif element_type == "uuid":
                schematic_data["uuid"] = item[1] if len(item) > 1 else None
            elif element_type == "title_block":
                schematic_data["title_block"] = self._parse_title_block(item)
            elif element_type == "symbol":
                component = self._parse_symbol(item)
                if component:
                    schematic_data["components"].append(component)
            elif element_type == "wire":
                wire = self._parse_wire(item)
                if wire:
                    schematic_data["wires"].append(wire)
            elif element_type == "junction":
                junction = self._parse_junction(item)
                if junction:
                    schematic_data["junctions"].append(junction)
            elif element_type == "label":
                label = self._parse_label(item)
                if label:
                    schematic_data["labels"].append(label)
            elif element_type == "hierarchical_label":
                hlabel = self._parse_hierarchical_label(item)
                if hlabel:
                    schematic_data["hierarchical_labels"].append(hlabel)
            elif element_type == "no_connect":
                no_connect = self._parse_no_connect(item)
                if no_connect:
                    schematic_data["no_connects"].append(no_connect)
            elif element_type == "text":
                text = self._parse_text(item)
                if text:
                    schematic_data["texts"].append(text)
            elif element_type == "text_box":
                text_box = self._parse_text_box(item)
                if text_box:
                    schematic_data["text_boxes"].append(text_box)
            elif element_type == "sheet":
                sheet = self._parse_sheet(item)
                if sheet:
                    schematic_data["sheets"].append(sheet)
            elif element_type == "polyline":
                polyline = self._parse_polyline(item)
                if polyline:
                    schematic_data["polylines"].append(polyline)
            elif element_type == "arc":
                arc = self._parse_arc(item)
                if arc:
                    schematic_data["arcs"].append(arc)
            elif element_type == "circle":
                circle = self._parse_circle(item)
                if circle:
                    schematic_data["circles"].append(circle)
            elif element_type == "bezier":
                bezier = self._parse_bezier(item)
                if bezier:
                    schematic_data["beziers"].append(bezier)
            elif element_type == "rectangle":
                rectangle = self._parse_rectangle(item)
                if rectangle:
                    schematic_data["rectangles"].append(rectangle)
            elif element_type == "lib_symbols":
                schematic_data["lib_symbols"] = self._parse_lib_symbols(item)
            elif element_type == "sheet_instances":
                schematic_data["sheet_instances"] = self._parse_sheet_instances(item)
            elif element_type == "symbol_instances":
                schematic_data["symbol_instances"] = self._parse_symbol_instances(item)
            elif element_type == "embedded_fonts":
                schematic_data["embedded_fonts"] = item[1] if len(item) > 1 else None

        return schematic_data

    def _schematic_data_to_sexp(self, schematic_data: Dict[str, Any]) -> List[Any]:
        """Convert internal schematic format to S-expression data."""
        sexp_data = [sexpdata.Symbol("kicad_sch")]

        # Add version and generator info
        if schematic_data.get("version"):
            sexp_data.append([sexpdata.Symbol("version"), int(schematic_data["version"])])
        if schematic_data.get("generator"):
            sexp_data.append([sexpdata.Symbol("generator"), schematic_data["generator"]])
        if schematic_data.get("generator_version"):
            sexp_data.append(
                [sexpdata.Symbol("generator_version"), schematic_data["generator_version"]]
            )
        if schematic_data.get("uuid"):
            sexp_data.append([sexpdata.Symbol("uuid"), schematic_data["uuid"]])
        if schematic_data.get("paper"):
            sexp_data.append([sexpdata.Symbol("paper"), schematic_data["paper"]])

        # Add title block only if it has non-default content
        title_block = schematic_data.get("title_block")
        if title_block and any(
            title_block.get(key) for key in ["title", "company", "revision", "date", "comments"]
        ):
            sexp_data.append(self._title_block_to_sexp(title_block))

        # Add lib_symbols (always include for KiCAD compatibility)
        lib_symbols = schematic_data.get("lib_symbols", {})
        sexp_data.append(self._lib_symbols_to_sexp(lib_symbols))

        # Add components
        for component in schematic_data.get("components", []):
            sexp_data.append(self._symbol_to_sexp(component, schematic_data.get("uuid")))

        # Add wires
        for wire in schematic_data.get("wires", []):
            sexp_data.append(self._wire_to_sexp(wire))

        # Add junctions
        for junction in schematic_data.get("junctions", []):
            sexp_data.append(self._junction_to_sexp(junction))

        # Add labels
        for label in schematic_data.get("labels", []):
            sexp_data.append(self._label_to_sexp(label))

        # Add hierarchical labels
        for hlabel in schematic_data.get("hierarchical_labels", []):
            sexp_data.append(self._hierarchical_label_to_sexp(hlabel))

        # Add no_connects
        for no_connect in schematic_data.get("no_connects", []):
            sexp_data.append(self._no_connect_to_sexp(no_connect))

        # Add graphical elements (in KiCad element order)
        # Beziers
        for bezier in schematic_data.get("beziers", []):
            sexp_data.append(self._bezier_to_sexp(bezier))

        # Rectangles (both from API and graphics)
        for rectangle in schematic_data.get("rectangles", []):
            sexp_data.append(self._rectangle_to_sexp(rectangle))
        for graphic in schematic_data.get("graphics", []):
            sexp_data.append(self._graphic_to_sexp(graphic))

        # Circles
        for circle in schematic_data.get("circles", []):
            sexp_data.append(self._circle_to_sexp(circle))

        # Arcs
        for arc in schematic_data.get("arcs", []):
            sexp_data.append(self._arc_to_sexp(arc))

        # Polylines
        for polyline in schematic_data.get("polylines", []):
            sexp_data.append(self._polyline_to_sexp(polyline))

        # Text elements
        for text in schematic_data.get("texts", []):
            sexp_data.append(self._text_to_sexp(text))

        # Text boxes
        for text_box in schematic_data.get("text_boxes", []):
            sexp_data.append(self._text_box_to_sexp(text_box))

        # Hierarchical sheets
        for sheet in schematic_data.get("sheets", []):
            sexp_data.append(self._sheet_to_sexp(sheet, schematic_data.get("uuid")))

        # Add sheet_instances (required by KiCAD)
        sheet_instances = schematic_data.get("sheet_instances", [])
        if sheet_instances:
            sexp_data.append(self._sheet_instances_to_sexp(sheet_instances))

        # Add symbol_instances (only if non-empty or for blank schematics)
        symbol_instances = schematic_data.get("symbol_instances", [])
        # Always include for blank schematics (no UUID, no embedded_fonts)
        is_blank_schematic = (
            not schematic_data.get("uuid") and schematic_data.get("embedded_fonts") is None
        )
        if symbol_instances or is_blank_schematic:
            sexp_data.append([sexpdata.Symbol("symbol_instances")])

        # Add embedded_fonts (required by KiCAD)
        if schematic_data.get("embedded_fonts") is not None:
            sexp_data.append([sexpdata.Symbol("embedded_fonts"), schematic_data["embedded_fonts"]])

        return sexp_data

    def _parse_title_block(self, item: List[Any]) -> Dict[str, Any]:
        """Parse title block information."""
        title_block = {}
        for sub_item in item[1:]:
            if isinstance(sub_item, list) and len(sub_item) >= 2:
                key = str(sub_item[0]) if isinstance(sub_item[0], sexpdata.Symbol) else None
                if key:
                    title_block[key] = sub_item[1] if len(sub_item) > 1 else None
        return title_block

    def _parse_symbol(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a symbol (component) definition."""
        try:
            symbol_data = {
                "lib_id": None,
                "position": Point(0, 0),
                "rotation": 0,
                "uuid": None,
                "reference": None,
                "value": None,
                "footprint": None,
                "properties": {},
                "pins": [],
                "in_bom": True,
                "on_board": True,
            }

            for sub_item in item[1:]:
                if not isinstance(sub_item, list) or len(sub_item) == 0:
                    continue

                element_type = (
                    str(sub_item[0]) if isinstance(sub_item[0], sexpdata.Symbol) else None
                )

                if element_type == "lib_id":
                    symbol_data["lib_id"] = sub_item[1] if len(sub_item) > 1 else None
                elif element_type == "at":
                    if len(sub_item) >= 3:
                        symbol_data["position"] = Point(float(sub_item[1]), float(sub_item[2]))
                        if len(sub_item) > 3:
                            symbol_data["rotation"] = float(sub_item[3])
                elif element_type == "uuid":
                    symbol_data["uuid"] = sub_item[1] if len(sub_item) > 1 else None
                elif element_type == "property":
                    prop_data = self._parse_property(sub_item)
                    if prop_data:
                        prop_name = prop_data.get("name")
                        if prop_name == "Reference":
                            symbol_data["reference"] = prop_data.get("value")
                        elif prop_name == "Value":
                            symbol_data["value"] = prop_data.get("value")
                        elif prop_name == "Footprint":
                            symbol_data["footprint"] = prop_data.get("value")
                        else:
                            # Unescape quotes in property values when loading
                            prop_value = prop_data.get("value")
                            if prop_value:
                                prop_value = str(prop_value).replace('\\"', '"')
                            symbol_data["properties"][prop_name] = prop_value
                elif element_type == "in_bom":
                    symbol_data["in_bom"] = sub_item[1] == "yes" if len(sub_item) > 1 else True
                elif element_type == "on_board":
                    symbol_data["on_board"] = sub_item[1] == "yes" if len(sub_item) > 1 else True

            return symbol_data

        except Exception as e:
            logger.warning(f"Error parsing symbol: {e}")
            return None

    def _parse_property(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a property definition."""
        if len(item) < 3:
            return None

        return {
            "name": item[1] if len(item) > 1 else None,
            "value": item[2] if len(item) > 2 else None,
        }

    def _parse_wire(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a wire definition."""
        wire_data = {
            "points": [],
            "stroke_width": 0.0,
            "stroke_type": "default",
            "uuid": None,
            "wire_type": "wire"  # Default to wire (vs bus)
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "pts":
                # Parse points: (pts (xy x1 y1) (xy x2 y2) ...)
                for pt in elem[1:]:
                    if isinstance(pt, list) and len(pt) >= 3:
                        if str(pt[0]) == "xy":
                            x, y = float(pt[1]), float(pt[2])
                            wire_data["points"].append({"x": x, "y": y})

            elif elem_type == "stroke":
                # Parse stroke: (stroke (width 0) (type default))
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list) and len(stroke_elem) >= 2:
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width":
                            wire_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type":
                            wire_data["stroke_type"] = str(stroke_elem[1])

            elif elem_type == "uuid":
                wire_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        # Only return wire if it has at least 2 points
        if len(wire_data["points"]) >= 2:
            return wire_data
        else:
            logger.warning(f"Wire has insufficient points: {len(wire_data['points'])}")
            return None

    def _parse_junction(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a junction definition."""
        junction_data = {
            "position": {"x": 0, "y": 0},
            "diameter": 0,
            "color": (0, 0, 0, 0),
            "uuid": None
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at":
                # Parse position: (at x y)
                if len(elem) >= 3:
                    junction_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}

            elif elem_type == "diameter":
                # Parse diameter: (diameter value)
                if len(elem) >= 2:
                    junction_data["diameter"] = float(elem[1])

            elif elem_type == "color":
                # Parse color: (color r g b a)
                if len(elem) >= 5:
                    junction_data["color"] = (int(elem[1]), int(elem[2]), int(elem[3]), int(elem[4]))

            elif elem_type == "uuid":
                junction_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return junction_data

    def _parse_label(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a label definition."""
        # Label format: (label "text" (at x y rotation) (effects ...) (uuid ...))
        if len(item) < 2:
            return None

        label_data = {
            "text": str(item[1]),  # Label text is second element
            "position": {"x": 0, "y": 0},
            "rotation": 0,
            "size": 1.27,
            "uuid": None
        }

        for elem in item[2:]:  # Skip label keyword and text
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at":
                # Parse position: (at x y rotation)
                if len(elem) >= 3:
                    label_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
                if len(elem) >= 4:
                    label_data["rotation"] = float(elem[3])

            elif elem_type == "effects":
                # Parse effects for font size: (effects (font (size x y)) ...)
                for effect_elem in elem[1:]:
                    if isinstance(effect_elem, list) and str(effect_elem[0]) == "font":
                        for font_elem in effect_elem[1:]:
                            if isinstance(font_elem, list) and str(font_elem[0]) == "size":
                                if len(font_elem) >= 2:
                                    label_data["size"] = float(font_elem[1])

            elif elem_type == "uuid":
                label_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return label_data

    def _parse_hierarchical_label(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a hierarchical label definition."""
        # Format: (hierarchical_label "text" (shape input) (at x y rotation) (effects ...) (uuid ...))
        if len(item) < 2:
            return None

        hlabel_data = {
            "text": str(item[1]),  # Hierarchical label text is second element
            "shape": "input",  # input/output/bidirectional/tri_state/passive
            "position": {"x": 0, "y": 0},
            "rotation": 0,
            "size": 1.27,
            "justify": "left",
            "uuid": None
        }

        for elem in item[2:]:  # Skip hierarchical_label keyword and text
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "shape":
                # Parse shape: (shape input)
                if len(elem) >= 2:
                    hlabel_data["shape"] = str(elem[1])

            elif elem_type == "at":
                # Parse position: (at x y rotation)
                if len(elem) >= 3:
                    hlabel_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
                if len(elem) >= 4:
                    hlabel_data["rotation"] = float(elem[3])

            elif elem_type == "effects":
                # Parse effects for font size and justification: (effects (font (size x y)) (justify left))
                for effect_elem in elem[1:]:
                    if isinstance(effect_elem, list):
                        effect_type = str(effect_elem[0]) if isinstance(effect_elem[0], sexpdata.Symbol) else None

                        if effect_type == "font":
                            # Parse font size
                            for font_elem in effect_elem[1:]:
                                if isinstance(font_elem, list) and str(font_elem[0]) == "size":
                                    if len(font_elem) >= 2:
                                        hlabel_data["size"] = float(font_elem[1])

                        elif effect_type == "justify":
                            # Parse justification (e.g., "left", "right")
                            if len(effect_elem) >= 2:
                                hlabel_data["justify"] = str(effect_elem[1])

            elif elem_type == "uuid":
                hlabel_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return hlabel_data

    def _parse_no_connect(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a no_connect symbol."""
        # Format: (no_connect (at x y) (uuid ...))
        no_connect_data = {
            "position": {"x": 0, "y": 0},
            "uuid": None
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at":
                if len(elem) >= 3:
                    no_connect_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "uuid":
                no_connect_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return no_connect_data

    def _parse_text(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a text element."""
        # Format: (text "text" (exclude_from_sim no) (at x y rotation) (effects ...) (uuid ...))
        if len(item) < 2:
            return None

        text_data = {
            "text": str(item[1]),
            "exclude_from_sim": False,
            "position": {"x": 0, "y": 0},
            "rotation": 0,
            "size": 1.27,
            "uuid": None
        }

        for elem in item[2:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "exclude_from_sim":
                if len(elem) >= 2:
                    text_data["exclude_from_sim"] = str(elem[1]) == "yes"
            elif elem_type == "at":
                if len(elem) >= 3:
                    text_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
                if len(elem) >= 4:
                    text_data["rotation"] = float(elem[3])
            elif elem_type == "effects":
                for effect_elem in elem[1:]:
                    if isinstance(effect_elem, list) and str(effect_elem[0]) == "font":
                        for font_elem in effect_elem[1:]:
                            if isinstance(font_elem, list) and str(font_elem[0]) == "size":
                                if len(font_elem) >= 2:
                                    text_data["size"] = float(font_elem[1])
            elif elem_type == "uuid":
                text_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return text_data

    def _parse_text_box(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a text_box element."""
        # Format: (text_box "text" (exclude_from_sim no) (at x y rotation) (size w h) (margins ...) (stroke ...) (fill ...) (effects ...) (uuid ...))
        if len(item) < 2:
            return None

        text_box_data = {
            "text": str(item[1]),
            "exclude_from_sim": False,
            "position": {"x": 0, "y": 0},
            "rotation": 0,
            "size": {"width": 0, "height": 0},
            "margins": (0.9525, 0.9525, 0.9525, 0.9525),
            "stroke_width": 0,
            "stroke_type": "solid",
            "fill_type": "none",
            "font_size": 1.27,
            "justify_horizontal": "left",
            "justify_vertical": "top",
            "uuid": None
        }

        for elem in item[2:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "exclude_from_sim":
                if len(elem) >= 2:
                    text_box_data["exclude_from_sim"] = str(elem[1]) == "yes"
            elif elem_type == "at":
                if len(elem) >= 3:
                    text_box_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
                if len(elem) >= 4:
                    text_box_data["rotation"] = float(elem[3])
            elif elem_type == "size":
                if len(elem) >= 3:
                    text_box_data["size"] = {"width": float(elem[1]), "height": float(elem[2])}
            elif elem_type == "margins":
                if len(elem) >= 5:
                    text_box_data["margins"] = (float(elem[1]), float(elem[2]), float(elem[3]), float(elem[4]))
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            text_box_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            text_box_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "type":
                        text_box_data["fill_type"] = str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
            elif elem_type == "effects":
                for effect_elem in elem[1:]:
                    if isinstance(effect_elem, list):
                        effect_type = str(effect_elem[0])
                        if effect_type == "font":
                            for font_elem in effect_elem[1:]:
                                if isinstance(font_elem, list) and str(font_elem[0]) == "size":
                                    if len(font_elem) >= 2:
                                        text_box_data["font_size"] = float(font_elem[1])
                        elif effect_type == "justify":
                            if len(effect_elem) >= 2:
                                text_box_data["justify_horizontal"] = str(effect_elem[1])
                            if len(effect_elem) >= 3:
                                text_box_data["justify_vertical"] = str(effect_elem[2])
            elif elem_type == "uuid":
                text_box_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return text_box_data

    def _parse_sheet(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a hierarchical sheet."""
        # Complex format with position, size, properties, pins, instances
        sheet_data = {
            "position": {"x": 0, "y": 0},
            "size": {"width": 0, "height": 0},
            "exclude_from_sim": False,
            "in_bom": True,
            "on_board": True,
            "dnp": False,
            "fields_autoplaced": True,
            "stroke_width": 0.1524,
            "stroke_type": "solid",
            "fill_color": (0, 0, 0, 0.0),
            "uuid": None,
            "name": "Sheet",
            "filename": "sheet.kicad_sch",
            "pins": [],
            "project_name": "",
            "page_number": "2"
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at":
                if len(elem) >= 3:
                    sheet_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "size":
                if len(elem) >= 3:
                    sheet_data["size"] = {"width": float(elem[1]), "height": float(elem[2])}
            elif elem_type == "exclude_from_sim":
                sheet_data["exclude_from_sim"] = str(elem[1]) == "yes" if len(elem) > 1 else False
            elif elem_type == "in_bom":
                sheet_data["in_bom"] = str(elem[1]) == "yes" if len(elem) > 1 else True
            elif elem_type == "on_board":
                sheet_data["on_board"] = str(elem[1]) == "yes" if len(elem) > 1 else True
            elif elem_type == "dnp":
                sheet_data["dnp"] = str(elem[1]) == "yes" if len(elem) > 1 else False
            elif elem_type == "fields_autoplaced":
                sheet_data["fields_autoplaced"] = str(elem[1]) == "yes" if len(elem) > 1 else True
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            sheet_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            sheet_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "color":
                        if len(fill_elem) >= 5:
                            sheet_data["fill_color"] = (int(fill_elem[1]), int(fill_elem[2]), int(fill_elem[3]), float(fill_elem[4]))
            elif elem_type == "uuid":
                sheet_data["uuid"] = str(elem[1]) if len(elem) > 1 else None
            elif elem_type == "property":
                if len(elem) >= 3:
                    prop_name = str(elem[1])
                    prop_value = str(elem[2])
                    if prop_name == "Sheetname":
                        sheet_data["name"] = prop_value
                    elif prop_name == "Sheetfile":
                        sheet_data["filename"] = prop_value
            elif elem_type == "pin":
                # Parse sheet pin - reuse existing _parse_sheet_pin helper
                pin_data = self._parse_sheet_pin_for_read(elem)
                if pin_data:
                    sheet_data["pins"].append(pin_data)
            elif elem_type == "instances":
                # Parse instances for project name and page number
                for inst_elem in elem[1:]:
                    if isinstance(inst_elem, list) and str(inst_elem[0]) == "project":
                        if len(inst_elem) >= 2:
                            sheet_data["project_name"] = str(inst_elem[1])
                        for path_elem in inst_elem[2:]:
                            if isinstance(path_elem, list) and str(path_elem[0]) == "path":
                                for page_elem in path_elem[1:]:
                                    if isinstance(page_elem, list) and str(page_elem[0]) == "page":
                                        sheet_data["page_number"] = str(page_elem[1]) if len(page_elem) > 1 else "2"

        return sheet_data

    def _parse_sheet_pin_for_read(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a sheet pin (for reading during sheet parsing)."""
        # Format: (pin "name" type (at x y rotation) (uuid ...) (effects ...))
        if len(item) < 3:
            return None

        pin_data = {
            "name": str(item[1]),
            "pin_type": str(item[2]) if len(item) > 2 else "input",
            "position": {"x": 0, "y": 0},
            "rotation": 0,
            "size": 1.27,
            "justify": "right",
            "uuid": None
        }

        for elem in item[3:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "at":
                if len(elem) >= 3:
                    pin_data["position"] = {"x": float(elem[1]), "y": float(elem[2])}
                if len(elem) >= 4:
                    pin_data["rotation"] = float(elem[3])
            elif elem_type == "uuid":
                pin_data["uuid"] = str(elem[1]) if len(elem) > 1 else None
            elif elem_type == "effects":
                for effect_elem in elem[1:]:
                    if isinstance(effect_elem, list):
                        effect_type = str(effect_elem[0])
                        if effect_type == "font":
                            for font_elem in effect_elem[1:]:
                                if isinstance(font_elem, list) and str(font_elem[0]) == "size":
                                    if len(font_elem) >= 2:
                                        pin_data["size"] = float(font_elem[1])
                        elif effect_type == "justify":
                            if len(effect_elem) >= 2:
                                pin_data["justify"] = str(effect_elem[1])

        return pin_data

    def _parse_polyline(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a polyline graphical element."""
        # Format: (polyline (pts (xy x1 y1) (xy x2 y2) ...) (stroke ...) (uuid ...))
        polyline_data = {
            "points": [],
            "stroke_width": 0,
            "stroke_type": "default",
            "uuid": None
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "pts":
                for pt in elem[1:]:
                    if isinstance(pt, list) and len(pt) >= 3 and str(pt[0]) == "xy":
                        polyline_data["points"].append({"x": float(pt[1]), "y": float(pt[2])})
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            polyline_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            polyline_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "uuid":
                polyline_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return polyline_data if polyline_data["points"] else None

    def _parse_arc(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse an arc graphical element."""
        # Format: (arc (start x y) (mid x y) (end x y) (stroke ...) (fill ...) (uuid ...))
        arc_data = {
            "start": {"x": 0, "y": 0},
            "mid": {"x": 0, "y": 0},
            "end": {"x": 0, "y": 0},
            "stroke_width": 0,
            "stroke_type": "default",
            "fill_type": "none",
            "uuid": None
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "start" and len(elem) >= 3:
                arc_data["start"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "mid" and len(elem) >= 3:
                arc_data["mid"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "end" and len(elem) >= 3:
                arc_data["end"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            arc_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            arc_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "type":
                        arc_data["fill_type"] = str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
            elif elem_type == "uuid":
                arc_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return arc_data

    def _parse_circle(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a circle graphical element."""
        # Format: (circle (center x y) (radius r) (stroke ...) (fill ...) (uuid ...))
        circle_data = {
            "center": {"x": 0, "y": 0},
            "radius": 0,
            "stroke_width": 0,
            "stroke_type": "default",
            "fill_type": "none",
            "uuid": None
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "center" and len(elem) >= 3:
                circle_data["center"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "radius" and len(elem) >= 2:
                circle_data["radius"] = float(elem[1])
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            circle_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            circle_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "type":
                        circle_data["fill_type"] = str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
            elif elem_type == "uuid":
                circle_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return circle_data

    def _parse_bezier(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a bezier curve graphical element."""
        # Format: (bezier (pts (xy x1 y1) (xy x2 y2) ...) (stroke ...) (fill ...) (uuid ...))
        bezier_data = {
            "points": [],
            "stroke_width": 0,
            "stroke_type": "default",
            "fill_type": "none",
            "uuid": None
        }

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0]) if isinstance(elem[0], sexpdata.Symbol) else None

            if elem_type == "pts":
                for pt in elem[1:]:
                    if isinstance(pt, list) and len(pt) >= 3 and str(pt[0]) == "xy":
                        bezier_data["points"].append({"x": float(pt[1]), "y": float(pt[2])})
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            bezier_data["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            bezier_data["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "type":
                        bezier_data["fill_type"] = str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
            elif elem_type == "uuid":
                bezier_data["uuid"] = str(elem[1]) if len(elem) > 1 else None

        return bezier_data if bezier_data["points"] else None

    def _parse_rectangle(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a rectangle graphical element."""
        rectangle = {}

        for elem in item[1:]:
            if not isinstance(elem, list):
                continue

            elem_type = str(elem[0])

            if elem_type == "start" and len(elem) >= 3:
                rectangle["start"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "end" and len(elem) >= 3:
                rectangle["end"] = {"x": float(elem[1]), "y": float(elem[2])}
            elif elem_type == "stroke":
                for stroke_elem in elem[1:]:
                    if isinstance(stroke_elem, list):
                        stroke_type = str(stroke_elem[0])
                        if stroke_type == "width" and len(stroke_elem) >= 2:
                            rectangle["stroke_width"] = float(stroke_elem[1])
                        elif stroke_type == "type" and len(stroke_elem) >= 2:
                            rectangle["stroke_type"] = str(stroke_elem[1])
            elif elem_type == "fill":
                for fill_elem in elem[1:]:
                    if isinstance(fill_elem, list) and str(fill_elem[0]) == "type":
                        rectangle["fill_type"] = str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
            elif elem_type == "uuid" and len(elem) >= 2:
                rectangle["uuid"] = str(elem[1])

        return rectangle if rectangle else None

    def _parse_lib_symbols(self, item: List[Any]) -> Dict[str, Any]:
        """Parse lib_symbols section."""
        # Implementation for lib_symbols parsing
        return {}

    # Conversion methods from internal format to S-expression
    def _title_block_to_sexp(self, title_block: Dict[str, Any]) -> List[Any]:
        """Convert title block to S-expression."""
        sexp = [sexpdata.Symbol("title_block")]

        # Add standard fields
        for key in ["title", "date", "rev", "company"]:
            if key in title_block and title_block[key]:
                sexp.append([sexpdata.Symbol(key), title_block[key]])

        # Add comments with special formatting
        comments = title_block.get("comments", {})
        if isinstance(comments, dict):
            for comment_num, comment_text in comments.items():
                sexp.append([sexpdata.Symbol("comment"), comment_num, comment_text])

        return sexp

    def _symbol_to_sexp(self, symbol_data: Dict[str, Any], schematic_uuid: str = None) -> List[Any]:
        """Convert symbol to S-expression."""
        sexp = [sexpdata.Symbol("symbol")]

        if symbol_data.get("lib_id"):
            sexp.append([sexpdata.Symbol("lib_id"), symbol_data["lib_id"]])

        # Add position and rotation (preserve original format)
        pos = symbol_data.get("position", Point(0, 0))
        rotation = symbol_data.get("rotation", 0)
        # Format numbers as integers if they are whole numbers
        x = int(pos.x) if pos.x == int(pos.x) else pos.x
        y = int(pos.y) if pos.y == int(pos.y) else pos.y
        r = int(rotation) if rotation == int(rotation) else rotation
        # Always include rotation for format consistency with KiCAD
        sexp.append([sexpdata.Symbol("at"), x, y, r])

        # Add unit (required by KiCAD)
        unit = symbol_data.get("unit", 1)
        sexp.append([sexpdata.Symbol("unit"), unit])

        # Add simulation and board settings (required by KiCAD)
        sexp.append([sexpdata.Symbol("exclude_from_sim"), "no"])
        sexp.append([sexpdata.Symbol("in_bom"), "yes" if symbol_data.get("in_bom", True) else "no"])
        sexp.append(
            [sexpdata.Symbol("on_board"), "yes" if symbol_data.get("on_board", True) else "no"]
        )
        sexp.append([sexpdata.Symbol("dnp"), "no"])
        sexp.append([sexpdata.Symbol("fields_autoplaced"), "yes"])

        if symbol_data.get("uuid"):
            sexp.append([sexpdata.Symbol("uuid"), symbol_data["uuid"]])

        # Add properties with proper positioning and effects
        lib_id = symbol_data.get("lib_id", "")
        is_power_symbol = "power:" in lib_id

        if symbol_data.get("reference"):
            # Power symbol references should be hidden by default
            ref_hide = is_power_symbol
            ref_prop = self._create_property_with_positioning(
                "Reference", symbol_data["reference"], pos, 0, "left", hide=ref_hide
            )
            sexp.append(ref_prop)

        if symbol_data.get("value"):
            # Power symbol values need different positioning
            if is_power_symbol:
                val_prop = self._create_power_symbol_value_property(
                    symbol_data["value"], pos, lib_id
                )
            else:
                val_prop = self._create_property_with_positioning(
                    "Value", symbol_data["value"], pos, 1, "left"
                )
            sexp.append(val_prop)

        footprint = symbol_data.get("footprint")
        if footprint is not None:  # Include empty strings but not None
            fp_prop = self._create_property_with_positioning(
                "Footprint", footprint, pos, 2, "left", hide=True
            )
            sexp.append(fp_prop)

        for prop_name, prop_value in symbol_data.get("properties", {}).items():
            escaped_value = str(prop_value).replace('"', '\\"')
            prop = self._create_property_with_positioning(
                prop_name, escaped_value, pos, 3, "left", hide=True
            )
            sexp.append(prop)

        # Add pin UUID assignments (required by KiCAD)
        for pin in symbol_data.get("pins", []):
            pin_uuid = str(uuid.uuid4())
            # Ensure pin number is a string for proper quoting
            pin_number = str(pin.number)
            sexp.append([sexpdata.Symbol("pin"), pin_number, [sexpdata.Symbol("uuid"), pin_uuid]])

        # Add instances section (required by KiCAD)
        from .config import config

        # Get project name from config or properties
        project_name = symbol_data.get("properties", {}).get("project_name")
        if not project_name:
            project_name = getattr(self, "project_name", config.defaults.project_name)

        # CRITICAL FIX: Use the FULL hierarchy_path from properties if available
        # For hierarchical schematics, this contains the complete path: /root_uuid/sheet_symbol_uuid/...
        # This ensures KiCad can properly annotate components in sub-sheets
        hierarchy_path = symbol_data.get("properties", {}).get("hierarchy_path")
        if hierarchy_path:
            # Use the full hierarchical path (includes root + all sheet symbols)
            instance_path = hierarchy_path
            logger.debug(f"🔧 Using FULL hierarchy_path: {instance_path} for component {symbol_data.get('reference', 'unknown')}")
        else:
            # Fallback: use root_uuid or schematic_uuid for flat designs
            root_uuid = symbol_data.get("properties", {}).get("root_uuid") or schematic_uuid or str(uuid.uuid4())
            instance_path = f"/{root_uuid}"
            logger.debug(f"🔧 Using root UUID path: {instance_path} for component {symbol_data.get('reference', 'unknown')}")

        logger.debug(f"🔧 Component properties keys: {list(symbol_data.get('properties', {}).keys())}")
        logger.debug(f"🔧 Using project name: '{project_name}'")

        sexp.append(
            [
                sexpdata.Symbol("instances"),
                [
                    sexpdata.Symbol("project"),
                    project_name,
                    [
                        sexpdata.Symbol("path"),
                        instance_path,
                        [sexpdata.Symbol("reference"), symbol_data.get("reference", "U?")],
                        [sexpdata.Symbol("unit"), symbol_data.get("unit", 1)],
                    ],
                ],
            ]
        )

        return sexp

    def _create_property_with_positioning(
        self,
        prop_name: str,
        prop_value: str,
        component_pos: Point,
        offset_index: int,
        justify: str = "left",
        hide: bool = False,
    ) -> List[Any]:
        """Create a property with proper positioning and effects like KiCAD."""
        from .config import config

        # Calculate property position using configuration
        prop_x, prop_y, rotation = config.get_property_position(
            prop_name, (component_pos.x, component_pos.y), offset_index
        )

        # Build effects section based on hide status
        effects = [
            sexpdata.Symbol("effects"),
            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
        ]

        # Only add justify for visible properties or Reference/Value
        if not hide or prop_name in ["Reference", "Value"]:
            effects.append([sexpdata.Symbol("justify"), sexpdata.Symbol(justify)])

        if hide:
            effects.append([sexpdata.Symbol("hide"), sexpdata.Symbol("yes")])

        prop_sexp = [
            sexpdata.Symbol("property"),
            prop_name,
            prop_value,
            [
                sexpdata.Symbol("at"),
                round(prop_x, 4) if prop_x != int(prop_x) else int(prop_x),
                round(prop_y, 4) if prop_y != int(prop_y) else int(prop_y),
                rotation,
            ],
            effects,
        ]

        return prop_sexp

    def _create_power_symbol_value_property(
        self, value: str, component_pos: Point, lib_id: str
    ) -> List[Any]:
        """Create Value property for power symbols with correct positioning."""
        # Power symbols have different value positioning based on type
        if "GND" in lib_id:
            # GND value goes below the symbol
            prop_x = component_pos.x
            prop_y = component_pos.y + 5.08  # Below GND symbol
        elif "+3.3V" in lib_id or "VDD" in lib_id:
            # Positive voltage values go below the symbol
            prop_x = component_pos.x
            prop_y = component_pos.y - 5.08  # Above symbol (negative offset)
        else:
            # Default power symbol positioning
            prop_x = component_pos.x
            prop_y = component_pos.y + 3.556

        prop_sexp = [
            sexpdata.Symbol("property"),
            "Value",
            value,
            [
                sexpdata.Symbol("at"),
                round(prop_x, 4) if prop_x != int(prop_x) else int(prop_x),
                round(prop_y, 4) if prop_y != int(prop_y) else int(prop_y),
                0,
            ],
            [
                sexpdata.Symbol("effects"),
                [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
            ],
        ]

        return prop_sexp

    def _wire_to_sexp(self, wire_data: Dict[str, Any]) -> List[Any]:
        """Convert wire to S-expression."""
        sexp = [sexpdata.Symbol("wire")]

        # Add points (pts section)
        points = wire_data.get("points", [])
        if len(points) >= 2:
            pts_sexp = [sexpdata.Symbol("pts")]
            for point in points:
                if isinstance(point, dict):
                    x, y = point["x"], point["y"]
                elif isinstance(point, (list, tuple)) and len(point) >= 2:
                    x, y = point[0], point[1]
                else:
                    # Assume it's a Point object
                    x, y = point.x, point.y

                # Format coordinates properly (avoid unnecessary .0 for integers)
                if isinstance(x, float) and x.is_integer():
                    x = int(x)
                if isinstance(y, float) and y.is_integer():
                    y = int(y)

                pts_sexp.append([sexpdata.Symbol("xy"), x, y])
            sexp.append(pts_sexp)

        # Add stroke information
        stroke_width = wire_data.get("stroke_width", 0)
        stroke_type = wire_data.get("stroke_type", "default")
        stroke_sexp = [sexpdata.Symbol("stroke")]

        # Format stroke width (use int for 0, preserve float for others)
        if isinstance(stroke_width, float) and stroke_width == 0.0:
            stroke_width = 0

        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add UUID
        if "uuid" in wire_data:
            sexp.append([sexpdata.Symbol("uuid"), wire_data["uuid"]])

        return sexp

    def _junction_to_sexp(self, junction_data: Dict[str, Any]) -> List[Any]:
        """Convert junction to S-expression."""
        sexp = [sexpdata.Symbol("junction")]

        # Add position
        pos = junction_data["position"]
        if isinstance(pos, dict):
            x, y = pos["x"], pos["y"]
        elif isinstance(pos, (list, tuple)) and len(pos) >= 2:
            x, y = pos[0], pos[1]
        else:
            # Assume it's a Point object
            x, y = pos.x, pos.y

        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)

        sexp.append([sexpdata.Symbol("at"), x, y])

        # Add diameter
        diameter = junction_data.get("diameter", 0)
        sexp.append([sexpdata.Symbol("diameter"), diameter])

        # Add color (RGBA)
        color = junction_data.get("color", (0, 0, 0, 0))
        if isinstance(color, (list, tuple)) and len(color) >= 4:
            sexp.append([sexpdata.Symbol("color"), color[0], color[1], color[2], color[3]])
        else:
            sexp.append([sexpdata.Symbol("color"), 0, 0, 0, 0])

        # Add UUID
        if "uuid" in junction_data:
            sexp.append([sexpdata.Symbol("uuid"), junction_data["uuid"]])

        return sexp

    def _label_to_sexp(self, label_data: Dict[str, Any]) -> List[Any]:
        """Convert local label to S-expression."""
        sexp = [sexpdata.Symbol("label"), label_data["text"]]

        # Add position
        pos = label_data["position"]
        x, y = pos["x"], pos["y"]
        rotation = label_data.get("rotation", 0)

        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)

        sexp.append([sexpdata.Symbol("at"), x, y, rotation])

        # Add effects (font properties)
        size = label_data.get("size", 1.27)
        effects = [sexpdata.Symbol("effects")]
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), size, size]]
        effects.append(font)
        effects.append(
            [sexpdata.Symbol("justify"), sexpdata.Symbol("left"), sexpdata.Symbol("bottom")]
        )
        sexp.append(effects)

        # Add UUID
        if "uuid" in label_data:
            sexp.append([sexpdata.Symbol("uuid"), label_data["uuid"]])

        return sexp

    def _hierarchical_label_to_sexp(self, hlabel_data: Dict[str, Any]) -> List[Any]:
        """Convert hierarchical label to S-expression."""
        sexp = [sexpdata.Symbol("hierarchical_label"), hlabel_data["text"]]

        # Add shape
        shape = hlabel_data.get("shape", "input")
        sexp.append([sexpdata.Symbol("shape"), sexpdata.Symbol(shape)])

        # Add position
        pos = hlabel_data["position"]
        x, y = pos["x"], pos["y"]
        rotation = hlabel_data.get("rotation", 0)
        sexp.append([sexpdata.Symbol("at"), x, y, rotation])

        # Add effects (font properties)
        size = hlabel_data.get("size", 1.27)
        effects = [sexpdata.Symbol("effects")]
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), size, size]]
        effects.append(font)

        # Use justification from data if provided, otherwise default to "left"
        justify = hlabel_data.get("justify", "left")
        effects.append([sexpdata.Symbol("justify"), sexpdata.Symbol(justify)])
        sexp.append(effects)

        # Add UUID
        if "uuid" in hlabel_data:
            sexp.append([sexpdata.Symbol("uuid"), hlabel_data["uuid"]])

        return sexp

    def _no_connect_to_sexp(self, no_connect_data: Dict[str, Any]) -> List[Any]:
        """Convert no_connect to S-expression."""
        sexp = [sexpdata.Symbol("no_connect")]

        # Add position
        pos = no_connect_data["position"]
        x, y = pos["x"], pos["y"]

        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)

        sexp.append([sexpdata.Symbol("at"), x, y])

        # Add UUID
        if "uuid" in no_connect_data:
            sexp.append([sexpdata.Symbol("uuid"), no_connect_data["uuid"]])

        return sexp

    def _polyline_to_sexp(self, polyline_data: Dict[str, Any]) -> List[Any]:
        """Convert polyline to S-expression."""
        sexp = [sexpdata.Symbol("polyline")]

        # Add points
        points = polyline_data.get("points", [])
        if points:
            pts_sexp = [sexpdata.Symbol("pts")]
            for point in points:
                x, y = point["x"], point["y"]
                # Format coordinates properly
                if isinstance(x, float) and x.is_integer():
                    x = int(x)
                if isinstance(y, float) and y.is_integer():
                    y = int(y)
                pts_sexp.append([sexpdata.Symbol("xy"), x, y])
            sexp.append(pts_sexp)

        # Add stroke
        stroke_width = polyline_data.get("stroke_width", 0)
        stroke_type = polyline_data.get("stroke_type", "default")
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add UUID
        if "uuid" in polyline_data:
            sexp.append([sexpdata.Symbol("uuid"), polyline_data["uuid"]])

        return sexp

    def _arc_to_sexp(self, arc_data: Dict[str, Any]) -> List[Any]:
        """Convert arc to S-expression."""
        sexp = [sexpdata.Symbol("arc")]

        # Add start, mid, end points
        for point_name in ["start", "mid", "end"]:
            point = arc_data.get(point_name, {"x": 0, "y": 0})
            x, y = point["x"], point["y"]
            # Format coordinates properly
            if isinstance(x, float) and x.is_integer():
                x = int(x)
            if isinstance(y, float) and y.is_integer():
                y = int(y)
            sexp.append([sexpdata.Symbol(point_name), x, y])

        # Add stroke
        stroke_width = arc_data.get("stroke_width", 0)
        stroke_type = arc_data.get("stroke_type", "default")
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add fill
        fill_type = arc_data.get("fill_type", "none")
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)])
        sexp.append(fill_sexp)

        # Add UUID
        if "uuid" in arc_data:
            sexp.append([sexpdata.Symbol("uuid"), arc_data["uuid"]])

        return sexp

    def _circle_to_sexp(self, circle_data: Dict[str, Any]) -> List[Any]:
        """Convert circle to S-expression."""
        sexp = [sexpdata.Symbol("circle")]

        # Add center
        center = circle_data.get("center", {"x": 0, "y": 0})
        x, y = center["x"], center["y"]
        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)
        sexp.append([sexpdata.Symbol("center"), x, y])

        # Add radius
        radius = circle_data.get("radius", 0)
        sexp.append([sexpdata.Symbol("radius"), radius])

        # Add stroke
        stroke_width = circle_data.get("stroke_width", 0)
        stroke_type = circle_data.get("stroke_type", "default")
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add fill
        fill_type = circle_data.get("fill_type", "none")
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)])
        sexp.append(fill_sexp)

        # Add UUID
        if "uuid" in circle_data:
            sexp.append([sexpdata.Symbol("uuid"), circle_data["uuid"]])

        return sexp

    def _bezier_to_sexp(self, bezier_data: Dict[str, Any]) -> List[Any]:
        """Convert bezier curve to S-expression."""
        sexp = [sexpdata.Symbol("bezier")]

        # Add points
        points = bezier_data.get("points", [])
        if points:
            pts_sexp = [sexpdata.Symbol("pts")]
            for point in points:
                x, y = point["x"], point["y"]
                # Format coordinates properly
                if isinstance(x, float) and x.is_integer():
                    x = int(x)
                if isinstance(y, float) and y.is_integer():
                    y = int(y)
                pts_sexp.append([sexpdata.Symbol("xy"), x, y])
            sexp.append(pts_sexp)

        # Add stroke
        stroke_width = bezier_data.get("stroke_width", 0)
        stroke_type = bezier_data.get("stroke_type", "default")
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add fill
        fill_type = bezier_data.get("fill_type", "none")
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)])
        sexp.append(fill_sexp)

        # Add UUID
        if "uuid" in bezier_data:
            sexp.append([sexpdata.Symbol("uuid"), bezier_data["uuid"]])

        return sexp

    def _sheet_to_sexp(self, sheet_data: Dict[str, Any], schematic_uuid: str) -> List[Any]:
        """Convert hierarchical sheet to S-expression."""
        sexp = [sexpdata.Symbol("sheet")]

        # Add position
        pos = sheet_data["position"]
        x, y = pos["x"], pos["y"]
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)
        sexp.append([sexpdata.Symbol("at"), x, y])

        # Add size
        size = sheet_data["size"]
        w, h = size["width"], size["height"]
        sexp.append([sexpdata.Symbol("size"), w, h])

        # Add basic properties
        sexp.append(
            [
                sexpdata.Symbol("exclude_from_sim"),
                sexpdata.Symbol("yes" if sheet_data.get("exclude_from_sim", False) else "no"),
            ]
        )
        sexp.append(
            [
                sexpdata.Symbol("in_bom"),
                sexpdata.Symbol("yes" if sheet_data.get("in_bom", True) else "no"),
            ]
        )
        sexp.append(
            [
                sexpdata.Symbol("on_board"),
                sexpdata.Symbol("yes" if sheet_data.get("on_board", True) else "no"),
            ]
        )
        sexp.append(
            [
                sexpdata.Symbol("dnp"),
                sexpdata.Symbol("yes" if sheet_data.get("dnp", False) else "no"),
            ]
        )
        sexp.append(
            [
                sexpdata.Symbol("fields_autoplaced"),
                sexpdata.Symbol("yes" if sheet_data.get("fields_autoplaced", True) else "no"),
            ]
        )

        # Add stroke
        stroke_width = sheet_data.get("stroke_width", 0.1524)
        stroke_type = sheet_data.get("stroke_type", "solid")
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add fill
        fill_color = sheet_data.get("fill_color", (0, 0, 0, 0.0))
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append(
            [sexpdata.Symbol("color"), fill_color[0], fill_color[1], fill_color[2], fill_color[3]]
        )
        sexp.append(fill_sexp)

        # Add UUID
        if "uuid" in sheet_data:
            sexp.append([sexpdata.Symbol("uuid"), sheet_data["uuid"]])

        # Add sheet properties (name and filename)
        name = sheet_data.get("name", "Sheet")
        filename = sheet_data.get("filename", "sheet.kicad_sch")

        # Sheetname property
        from .config import config

        name_prop = [sexpdata.Symbol("property"), "Sheetname", name]
        name_prop.append(
            [sexpdata.Symbol("at"), x, round(y + config.sheet.name_offset_y, 4), 0]
        )  # Above sheet
        name_prop.append(
            [
                sexpdata.Symbol("effects"),
                [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                [sexpdata.Symbol("justify"), sexpdata.Symbol("left"), sexpdata.Symbol("bottom")],
            ]
        )
        sexp.append(name_prop)

        # Sheetfile property
        file_prop = [sexpdata.Symbol("property"), "Sheetfile", filename]
        file_prop.append(
            [sexpdata.Symbol("at"), x, round(y + h + config.sheet.file_offset_y, 4), 0]
        )  # Below sheet
        file_prop.append(
            [
                sexpdata.Symbol("effects"),
                [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                [sexpdata.Symbol("justify"), sexpdata.Symbol("left"), sexpdata.Symbol("top")],
            ]
        )
        sexp.append(file_prop)

        # Add sheet pins if any
        for pin in sheet_data.get("pins", []):
            pin_sexp = self._sheet_pin_to_sexp(pin)
            sexp.append(pin_sexp)

        # Add instances
        if schematic_uuid:
            instances_sexp = [sexpdata.Symbol("instances")]
            project_name = sheet_data.get("project_name", "")
            page_number = sheet_data.get("page_number", "2")
            project_sexp = [sexpdata.Symbol("project"), project_name]
            path_sexp = [sexpdata.Symbol("path"), f"/{schematic_uuid}"]
            path_sexp.append([sexpdata.Symbol("page"), page_number])
            project_sexp.append(path_sexp)
            instances_sexp.append(project_sexp)
            sexp.append(instances_sexp)

        return sexp

    def _sheet_pin_to_sexp(self, pin_data: Dict[str, Any]) -> List[Any]:
        """Convert sheet pin to S-expression."""
        pin_sexp = [
            sexpdata.Symbol("pin"),
            pin_data["name"],
            sexpdata.Symbol(pin_data.get("pin_type", "input")),
        ]

        # Add position
        pos = pin_data["position"]
        x, y = pos["x"], pos["y"]
        rotation = pin_data.get("rotation", 0)
        pin_sexp.append([sexpdata.Symbol("at"), x, y, rotation])

        # Add UUID
        if "uuid" in pin_data:
            pin_sexp.append([sexpdata.Symbol("uuid"), pin_data["uuid"]])

        # Add effects
        size = pin_data.get("size", 1.27)
        effects = [sexpdata.Symbol("effects")]
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), size, size]]
        effects.append(font)
        justify = pin_data.get("justify", "right")
        effects.append([sexpdata.Symbol("justify"), sexpdata.Symbol(justify)])
        pin_sexp.append(effects)

        return pin_sexp

    def _text_to_sexp(self, text_data: Dict[str, Any]) -> List[Any]:
        """Convert text element to S-expression."""
        sexp = [sexpdata.Symbol("text"), text_data["text"]]

        # Add exclude_from_sim
        exclude_sim = text_data.get("exclude_from_sim", False)
        sexp.append(
            [sexpdata.Symbol("exclude_from_sim"), sexpdata.Symbol("yes" if exclude_sim else "no")]
        )

        # Add position
        pos = text_data["position"]
        x, y = pos["x"], pos["y"]
        rotation = text_data.get("rotation", 0)

        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)

        sexp.append([sexpdata.Symbol("at"), x, y, rotation])

        # Add effects (font properties)
        size = text_data.get("size", 1.27)
        effects = [sexpdata.Symbol("effects")]
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), size, size]]
        effects.append(font)
        sexp.append(effects)

        # Add UUID
        if "uuid" in text_data:
            sexp.append([sexpdata.Symbol("uuid"), text_data["uuid"]])

        return sexp

    def _text_box_to_sexp(self, text_box_data: Dict[str, Any]) -> List[Any]:
        """Convert text box element to S-expression."""
        sexp = [sexpdata.Symbol("text_box"), text_box_data["text"]]

        # Add exclude_from_sim
        exclude_sim = text_box_data.get("exclude_from_sim", False)
        sexp.append(
            [sexpdata.Symbol("exclude_from_sim"), sexpdata.Symbol("yes" if exclude_sim else "no")]
        )

        # Add position
        pos = text_box_data["position"]
        x, y = pos["x"], pos["y"]
        rotation = text_box_data.get("rotation", 0)

        # Format coordinates properly
        if isinstance(x, float) and x.is_integer():
            x = int(x)
        if isinstance(y, float) and y.is_integer():
            y = int(y)

        sexp.append([sexpdata.Symbol("at"), x, y, rotation])

        # Add size
        size = text_box_data["size"]
        w, h = size["width"], size["height"]
        sexp.append([sexpdata.Symbol("size"), w, h])

        # Add margins
        margins = text_box_data.get("margins", (0.9525, 0.9525, 0.9525, 0.9525))
        sexp.append([sexpdata.Symbol("margins"), margins[0], margins[1], margins[2], margins[3]])

        # Add stroke
        stroke_width = text_box_data.get("stroke_width", 0)
        stroke_type = text_box_data.get("stroke_type", "solid")
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add fill
        fill_type = text_box_data.get("fill_type", "none")
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)])
        sexp.append(fill_sexp)

        # Add effects (font properties and justification)
        font_size = text_box_data.get("font_size", 1.27)
        justify_h = text_box_data.get("justify_horizontal", "left")
        justify_v = text_box_data.get("justify_vertical", "top")

        effects = [sexpdata.Symbol("effects")]
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), font_size, font_size]]
        effects.append(font)
        effects.append(
            [sexpdata.Symbol("justify"), sexpdata.Symbol(justify_h), sexpdata.Symbol(justify_v)]
        )
        sexp.append(effects)

        # Add UUID
        if "uuid" in text_box_data:
            sexp.append([sexpdata.Symbol("uuid"), text_box_data["uuid"]])

        return sexp

    def _rectangle_to_sexp(self, rectangle_data: Dict[str, Any]) -> List[Any]:
        """Convert rectangle element to S-expression."""
        sexp = [sexpdata.Symbol("rectangle")]

        # Add start point
        start = rectangle_data["start"]
        start_x, start_y = start["x"], start["y"]
        sexp.append([sexpdata.Symbol("start"), start_x, start_y])

        # Add end point
        end = rectangle_data["end"]
        end_x, end_y = end["x"], end["y"]
        sexp.append([sexpdata.Symbol("end"), end_x, end_y])

        # Add stroke
        stroke_width = rectangle_data.get("stroke_width", 0)
        stroke_type = rectangle_data.get("stroke_type", "default")
        stroke_sexp = [sexpdata.Symbol("stroke")]
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])
        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(stroke_type)])
        sexp.append(stroke_sexp)

        # Add fill
        fill_type = rectangle_data.get("fill_type", "none")
        fill_sexp = [sexpdata.Symbol("fill")]
        fill_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)])
        sexp.append(fill_sexp)

        # Add UUID
        if "uuid" in rectangle_data:
            sexp.append([sexpdata.Symbol("uuid"), rectangle_data["uuid"]])

        return sexp

    def _lib_symbols_to_sexp(self, lib_symbols: Dict[str, Any]) -> List[Any]:
        """Convert lib_symbols to S-expression."""
        sexp = [sexpdata.Symbol("lib_symbols")]

        # Add each symbol definition
        for symbol_name, symbol_def in lib_symbols.items():
            if isinstance(symbol_def, list):
                # Raw S-expression data from parsed library file - use directly
                sexp.append(symbol_def)
            elif isinstance(symbol_def, dict):
                # Dictionary format - convert to S-expression
                symbol_sexp = self._create_basic_symbol_definition(symbol_name)
                sexp.append(symbol_sexp)

        return sexp

    def _create_basic_symbol_definition(self, lib_id: str) -> List[Any]:
        """Create a basic symbol definition for KiCAD compatibility."""
        symbol_sexp = [sexpdata.Symbol("symbol"), lib_id]

        # Add basic symbol properties
        symbol_sexp.extend(
            [
                [sexpdata.Symbol("pin_numbers"), [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")]],
                [sexpdata.Symbol("pin_names"), [sexpdata.Symbol("offset"), 0]],
                [sexpdata.Symbol("exclude_from_sim"), sexpdata.Symbol("no")],
                [sexpdata.Symbol("in_bom"), sexpdata.Symbol("yes")],
                [sexpdata.Symbol("on_board"), sexpdata.Symbol("yes")],
            ]
        )

        # Add basic properties for the symbol
        if "R" in lib_id:  # Resistor
            symbol_sexp.extend(
                [
                    [
                        sexpdata.Symbol("property"),
                        "Reference",
                        "R",
                        [sexpdata.Symbol("at"), 2.032, 0, 90],
                        [
                            sexpdata.Symbol("effects"),
                            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                        ],
                    ],
                    [
                        sexpdata.Symbol("property"),
                        "Value",
                        "R",
                        [sexpdata.Symbol("at"), 0, 0, 90],
                        [
                            sexpdata.Symbol("effects"),
                            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                        ],
                    ],
                    [
                        sexpdata.Symbol("property"),
                        "Footprint",
                        "",
                        [sexpdata.Symbol("at"), -1.778, 0, 90],
                        [
                            sexpdata.Symbol("effects"),
                            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                            [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")],
                        ],
                    ],
                    [
                        sexpdata.Symbol("property"),
                        "Datasheet",
                        "~",
                        [sexpdata.Symbol("at"), 0, 0, 0],
                        [
                            sexpdata.Symbol("effects"),
                            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                            [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")],
                        ],
                    ],
                ]
            )

        elif "C" in lib_id:  # Capacitor
            symbol_sexp.extend(
                [
                    [
                        sexpdata.Symbol("property"),
                        "Reference",
                        "C",
                        [sexpdata.Symbol("at"), 0.635, 2.54, 0],
                        [
                            sexpdata.Symbol("effects"),
                            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                        ],
                    ],
                    [
                        sexpdata.Symbol("property"),
                        "Value",
                        "C",
                        [sexpdata.Symbol("at"), 0.635, -2.54, 0],
                        [
                            sexpdata.Symbol("effects"),
                            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                        ],
                    ],
                    [
                        sexpdata.Symbol("property"),
                        "Footprint",
                        "",
                        [sexpdata.Symbol("at"), 0, -1.27, 0],
                        [
                            sexpdata.Symbol("effects"),
                            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                            [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")],
                        ],
                    ],
                    [
                        sexpdata.Symbol("property"),
                        "Datasheet",
                        "~",
                        [sexpdata.Symbol("at"), 0, 0, 0],
                        [
                            sexpdata.Symbol("effects"),
                            [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]],
                            [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")],
                        ],
                    ],
                ]
            )

        # Add basic graphics and pins (minimal for now)
        symbol_sexp.append([sexpdata.Symbol("embedded_fonts"), sexpdata.Symbol("no")])

        return symbol_sexp

    def _parse_sheet_instances(self, item: List[Any]) -> List[Dict[str, Any]]:
        """Parse sheet_instances section."""
        sheet_instances = []
        for sheet_item in item[1:]:  # Skip 'sheet_instances' header
            if isinstance(sheet_item, list) and len(sheet_item) > 0:
                sheet_data = {"path": "/", "page": "1"}
                for element in sheet_item[1:]:  # Skip element header
                    if isinstance(element, list) and len(element) >= 2:
                        key = (
                            str(element[0])
                            if isinstance(element[0], sexpdata.Symbol)
                            else str(element[0])
                        )
                        if key == "path":
                            sheet_data["path"] = element[1]
                        elif key == "page":
                            sheet_data["page"] = element[1]
                sheet_instances.append(sheet_data)
        return sheet_instances

    def _parse_symbol_instances(self, item: List[Any]) -> List[Any]:
        """Parse symbol_instances section."""
        # For now, just return the raw structure minus the header
        return item[1:] if len(item) > 1 else []

    def _sheet_instances_to_sexp(self, sheet_instances: List[Dict[str, Any]]) -> List[Any]:
        """Convert sheet_instances to S-expression."""
        sexp = [sexpdata.Symbol("sheet_instances")]
        for sheet in sheet_instances:
            # Create: (path "/" (page "1"))
            sheet_sexp = [
                sexpdata.Symbol("path"),
                sheet.get("path", "/"),
                [sexpdata.Symbol("page"), str(sheet.get("page", "1"))],
            ]
            sexp.append(sheet_sexp)
        return sexp

    def _graphic_to_sexp(self, graphic_data: Dict[str, Any]) -> List[Any]:
        """Convert graphics (rectangles, etc.) to S-expression."""
        # For now, we only support rectangles - this is the main graphics element we create
        sexp = [sexpdata.Symbol("rectangle")]

        # Add start position
        start = graphic_data.get("start", {})
        start_x = start.get("x", 0)
        start_y = start.get("y", 0)

        # Format coordinates properly (avoid unnecessary .0 for integers)
        if isinstance(start_x, float) and start_x.is_integer():
            start_x = int(start_x)
        if isinstance(start_y, float) and start_y.is_integer():
            start_y = int(start_y)

        sexp.append([sexpdata.Symbol("start"), start_x, start_y])

        # Add end position
        end = graphic_data.get("end", {})
        end_x = end.get("x", 0)
        end_y = end.get("y", 0)

        # Format coordinates properly (avoid unnecessary .0 for integers)
        if isinstance(end_x, float) and end_x.is_integer():
            end_x = int(end_x)
        if isinstance(end_y, float) and end_y.is_integer():
            end_y = int(end_y)

        sexp.append([sexpdata.Symbol("end"), end_x, end_y])

        # Add stroke information (KiCAD format: width, type, and optionally color)
        stroke = graphic_data.get("stroke", {})
        stroke_sexp = [sexpdata.Symbol("stroke")]

        # Stroke width - default to 0 to match KiCAD behavior
        stroke_width = stroke.get("width", 0)
        if isinstance(stroke_width, float) and stroke_width == 0.0:
            stroke_width = 0
        stroke_sexp.append([sexpdata.Symbol("width"), stroke_width])

        # Stroke type - normalize to KiCAD format and validate
        stroke_type = stroke.get("type", "default")

        # KiCAD only supports these exact stroke types
        valid_kicad_types = {"solid", "dash", "dash_dot", "dash_dot_dot", "dot", "default"}

        # Map common variations to KiCAD format
        stroke_type_map = {
            "dashdot": "dash_dot",
            "dash-dot": "dash_dot",
            "dashdotdot": "dash_dot_dot",
            "dash-dot-dot": "dash_dot_dot",
            "solid": "solid",
            "dash": "dash",
            "dot": "dot",
            "default": "default",
        }

        # Normalize and validate
        normalized_stroke_type = stroke_type_map.get(stroke_type.lower(), stroke_type)
        if normalized_stroke_type not in valid_kicad_types:
            normalized_stroke_type = "default"  # Fallback to default for invalid types

        stroke_sexp.append([sexpdata.Symbol("type"), sexpdata.Symbol(normalized_stroke_type)])

        # Stroke color (if specified) - KiCAD format uses RGB 0-255 values plus alpha
        stroke_color = stroke.get("color")
        if stroke_color:
            if isinstance(stroke_color, str):
                # Convert string color names to RGB 0-255 values
                color_rgb = self._color_to_rgb255(stroke_color)
                stroke_sexp.append([sexpdata.Symbol("color")] + color_rgb + [1])  # Add alpha=1
            elif isinstance(stroke_color, (list, tuple)) and len(stroke_color) >= 3:
                # Use provided RGB values directly
                stroke_sexp.append([sexpdata.Symbol("color")] + list(stroke_color))

        sexp.append(stroke_sexp)

        # Add fill information
        fill = graphic_data.get("fill", {"type": "none"})
        fill_type = fill.get("type", "none")
        fill_sexp = [sexpdata.Symbol("fill"), [sexpdata.Symbol("type"), sexpdata.Symbol(fill_type)]]
        sexp.append(fill_sexp)

        # Add UUID (no quotes around UUID in KiCAD format)
        if "uuid" in graphic_data:
            uuid_str = graphic_data["uuid"]
            # Remove quotes and convert to Symbol to match KiCAD format
            uuid_clean = uuid_str.replace('"', "")
            sexp.append([sexpdata.Symbol("uuid"), sexpdata.Symbol(uuid_clean)])

        return sexp

    def _color_to_rgba(self, color_name: str) -> List[float]:
        """Convert color name to RGBA values (0.0-1.0) for KiCAD compatibility."""
        # Basic color mapping for common colors (0.0-1.0 range)
        color_map = {
            "red": [1.0, 0.0, 0.0, 1.0],
            "blue": [0.0, 0.0, 1.0, 1.0],
            "green": [0.0, 1.0, 0.0, 1.0],
            "yellow": [1.0, 1.0, 0.0, 1.0],
            "magenta": [1.0, 0.0, 1.0, 1.0],
            "cyan": [0.0, 1.0, 1.0, 1.0],
            "black": [0.0, 0.0, 0.0, 1.0],
            "white": [1.0, 1.0, 1.0, 1.0],
            "gray": [0.5, 0.5, 0.5, 1.0],
            "grey": [0.5, 0.5, 0.5, 1.0],
            "orange": [1.0, 0.5, 0.0, 1.0],
            "purple": [0.5, 0.0, 0.5, 1.0],
        }

        # Return RGBA values, default to black if color not found
        return color_map.get(color_name.lower(), [0.0, 0.0, 0.0, 1.0])

    def _color_to_rgb255(self, color_name: str) -> List[int]:
        """Convert color name to RGB values (0-255) for KiCAD rectangle graphics."""
        # Basic color mapping for common colors (0-255 range)
        color_map = {
            "red": [255, 0, 0],
            "blue": [0, 0, 255],
            "green": [0, 255, 0],
            "yellow": [255, 255, 0],
            "magenta": [255, 0, 255],
            "cyan": [0, 255, 255],
            "black": [0, 0, 0],
            "white": [255, 255, 255],
            "gray": [128, 128, 128],
            "grey": [128, 128, 128],
            "orange": [255, 128, 0],
            "purple": [128, 0, 128],
        }

        # Return RGB values, default to black if color not found
        return color_map.get(color_name.lower(), [0, 0, 0])

    def get_validation_issues(self) -> List[ValidationIssue]:
        """Get list of validation issues from last parse operation."""
        return self._validation_issues.copy()
