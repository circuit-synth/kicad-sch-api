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

from ..parsers.elements.graphics_parser import GraphicsParser
from ..parsers.elements.label_parser import LabelParser
from ..parsers.elements.library_parser import LibraryParser
from ..parsers.elements.metadata_parser import MetadataParser
from ..parsers.elements.sheet_parser import SheetParser
from ..parsers.elements.symbol_parser import SymbolParser
from ..parsers.elements.text_parser import TextParser
from ..parsers.elements.wire_parser import WireParser
from ..parsers.utils import color_to_rgb255, color_to_rgba
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
        self._graphics_parser = GraphicsParser()
        self._wire_parser = WireParser()
        self._label_parser = LabelParser()
        self._text_parser = TextParser()
        self._sheet_parser = SheetParser()
        self._library_parser = LibraryParser()
        self._symbol_parser = SymbolParser()
        self._metadata_parser = MetadataParser()
        self._project_name = None
        logger.info(f"S-expression parser initialized (format preservation: {preserve_format})")

    @property
    def project_name(self):
        """Get project name."""
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        """Set project name on parser and propagate to sub-parsers."""
        self._project_name = value
        # Propagate to symbol parser which needs it for instances
        if hasattr(self, "_symbol_parser"):
            self._symbol_parser.project_name = value

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
            "images": [],
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
            elif element_type == "image":
                image = self._parse_image(item)
                if image:
                    schematic_data["images"].append(image)
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

        # Images
        for image in schematic_data.get("images", []):
            sexp_data.append(self._image_to_sexp(image))

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
        return self._metadata_parser._parse_title_block(item)

    def _parse_symbol(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a symbol (component) definition."""
        return self._symbol_parser._parse_symbol(item)

    def _parse_property(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a property definition."""
        return self._symbol_parser._parse_property(item)

    def _parse_wire(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a wire definition."""
        return self._wire_parser._parse_wire(item)

    def _parse_junction(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a junction definition."""
        return self._wire_parser._parse_junction(item)

    def _parse_label(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a label definition."""
        return self._label_parser._parse_label(item)

    def _parse_hierarchical_label(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a hierarchical label definition."""
        return self._label_parser._parse_hierarchical_label(item)

    def _parse_no_connect(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a no_connect symbol."""
        return self._wire_parser._parse_no_connect(item)

    def _parse_text(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a text element."""
        return self._text_parser._parse_text(item)

    def _parse_text_box(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a text_box element."""
        return self._text_parser._parse_text_box(item)

    def _parse_sheet(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a hierarchical sheet."""
        return self._sheet_parser._parse_sheet(item)

    def _parse_sheet_pin_for_read(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a sheet pin (for reading during sheet parsing)."""
        return self._sheet_parser._parse_sheet_pin_for_read(item)

    def _parse_polyline(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a polyline graphical element."""
        return self._graphics_parser._parse_polyline(item)

    def _parse_arc(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse an arc graphical element."""
        return self._graphics_parser._parse_arc(item)

    def _parse_circle(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a circle graphical element."""
        return self._graphics_parser._parse_circle(item)

    def _parse_bezier(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a bezier curve graphical element."""
        return self._graphics_parser._parse_bezier(item)

    def _parse_rectangle(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a rectangle graphical element."""
        return self._graphics_parser._parse_rectangle(item)

    def _parse_image(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse an image element."""
        return self._graphics_parser._parse_image(item)

    def _parse_lib_symbols(self, item: List[Any]) -> Dict[str, Any]:
        """Parse lib_symbols section."""
        return self._library_parser._parse_lib_symbols(item)

    def _title_block_to_sexp(self, title_block: Dict[str, Any]) -> List[Any]:
        """Convert title block to S-expression."""
        return self._metadata_parser._title_block_to_sexp(title_block)

    def _symbol_to_sexp(self, symbol_data: Dict[str, Any], schematic_uuid: str = None) -> List[Any]:
        """Convert symbol to S-expression."""
        return self._symbol_parser._symbol_to_sexp(symbol_data, schematic_uuid)

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
        return self._wire_parser._wire_to_sexp(wire_data)

    def _junction_to_sexp(self, junction_data: Dict[str, Any]) -> List[Any]:
        """Convert junction to S-expression."""
        return self._wire_parser._junction_to_sexp(junction_data)

    def _label_to_sexp(self, label_data: Dict[str, Any]) -> List[Any]:
        """Convert local label to S-expression."""
        return self._label_parser._label_to_sexp(label_data)

    def _hierarchical_label_to_sexp(self, hlabel_data: Dict[str, Any]) -> List[Any]:
        """Convert hierarchical label to S-expression."""
        return self._label_parser._hierarchical_label_to_sexp(hlabel_data)

    def _no_connect_to_sexp(self, no_connect_data: Dict[str, Any]) -> List[Any]:
        """Convert no_connect to S-expression."""
        return self._wire_parser._no_connect_to_sexp(no_connect_data)

    def _polyline_to_sexp(self, polyline_data: Dict[str, Any]) -> List[Any]:
        """Convert polyline to S-expression."""
        return self._graphics_parser._polyline_to_sexp(polyline_data)

    def _arc_to_sexp(self, arc_data: Dict[str, Any]) -> List[Any]:
        """Convert arc to S-expression."""
        return self._graphics_parser._arc_to_sexp(arc_data)

    def _circle_to_sexp(self, circle_data: Dict[str, Any]) -> List[Any]:
        """Convert circle to S-expression."""
        return self._graphics_parser._circle_to_sexp(circle_data)

    def _bezier_to_sexp(self, bezier_data: Dict[str, Any]) -> List[Any]:
        """Convert bezier curve to S-expression."""
        return self._graphics_parser._bezier_to_sexp(bezier_data)

    def _sheet_to_sexp(self, sheet_data: Dict[str, Any], schematic_uuid: str) -> List[Any]:
        """Convert hierarchical sheet to S-expression."""
        return self._sheet_parser._sheet_to_sexp(sheet_data, schematic_uuid)

    def _sheet_pin_to_sexp(self, pin_data: Dict[str, Any]) -> List[Any]:
        """Convert sheet pin to S-expression."""
        return self._sheet_parser._sheet_pin_to_sexp(pin_data)

    def _text_to_sexp(self, text_data: Dict[str, Any]) -> List[Any]:
        """Convert text element to S-expression."""
        return self._text_parser._text_to_sexp(text_data)

    def _text_box_to_sexp(self, text_box_data: Dict[str, Any]) -> List[Any]:
        """Convert text box element to S-expression."""
        return self._text_parser._text_box_to_sexp(text_box_data)

    def _rectangle_to_sexp(self, rectangle_data: Dict[str, Any]) -> List[Any]:
        """Convert rectangle element to S-expression."""
        return self._graphics_parser._rectangle_to_sexp(rectangle_data)

    def _image_to_sexp(self, image_data: Dict[str, Any]) -> List[Any]:
        """Convert image element to S-expression."""
        return self._graphics_parser._image_to_sexp(image_data)

    def _lib_symbols_to_sexp(self, lib_symbols: Dict[str, Any]) -> List[Any]:
        """Convert lib_symbols to S-expression."""
        return self._library_parser._lib_symbols_to_sexp(lib_symbols)

    def _create_basic_symbol_definition(self, lib_id: str) -> List[Any]:
        """Create a basic symbol definition for KiCAD compatibility."""
        return self._library_parser._create_basic_symbol_definition(lib_id)

    def _parse_sheet_instances(self, item: List[Any]) -> List[Dict[str, Any]]:
        """Parse sheet_instances section."""
        return self._sheet_parser._parse_sheet_instances(item)

    def _parse_symbol_instances(self, item: List[Any]) -> List[Any]:
        """Parse symbol_instances section."""
        return self._metadata_parser._parse_symbol_instances(item)

    def _sheet_instances_to_sexp(self, sheet_instances: List[Dict[str, Any]]) -> List[Any]:
        """Convert sheet_instances to S-expression."""
        return self._sheet_parser._sheet_instances_to_sexp(sheet_instances)

    def _graphic_to_sexp(self, graphic_data: Dict[str, Any]) -> List[Any]:
        """Convert graphics (rectangles, etc.) to S-expression."""
        return self._graphics_parser._graphic_to_sexp(graphic_data)

    def _color_to_rgba(self, color_name: str) -> List[float]:
        """Convert color name to RGBA values (0.0-1.0) for KiCAD compatibility."""
        return color_to_rgba(color_name)

    def _color_to_rgb255(self, color_name: str) -> List[int]:
        """Convert color name to RGB values (0-255) for KiCAD rectangle graphics."""
        return color_to_rgb255(color_name)

    def get_validation_issues(self) -> List[ValidationIssue]:
        """Get list of validation issues from last parse operation."""
        return self._validation_issues.copy()
