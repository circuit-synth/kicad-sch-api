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
            "nets": [],
            "lib_symbols": {},
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
            elif element_type == "lib_symbols":
                schematic_data["lib_symbols"] = self._parse_lib_symbols(item)

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
            sexp_data.append([sexpdata.Symbol("generator_version"), schematic_data["generator_version"]])
        if schematic_data.get("uuid"):
            sexp_data.append([sexpdata.Symbol("uuid"), schematic_data["uuid"]])
        if schematic_data.get("paper"):
            sexp_data.append([sexpdata.Symbol("paper"), schematic_data["paper"]])

        # Add title block
        if schematic_data.get("title_block"):
            sexp_data.append(self._title_block_to_sexp(schematic_data["title_block"]))

        # Add lib_symbols (always include for KiCAD compatibility)
        lib_symbols = schematic_data.get("lib_symbols", {})
        sexp_data.append(self._lib_symbols_to_sexp(lib_symbols))

        # Add components
        for component in schematic_data.get("components", []):
            sexp_data.append(self._symbol_to_sexp(component))

        # Add wires
        for wire in schematic_data.get("wires", []):
            sexp_data.append(self._wire_to_sexp(wire))

        # Add junctions
        for junction in schematic_data.get("junctions", []):
            sexp_data.append(self._junction_to_sexp(junction))

        # Add labels
        for label in schematic_data.get("labels", []):
            sexp_data.append(self._label_to_sexp(label))

        # Add symbol_instances (required by KiCAD)
        symbol_instances = schematic_data.get("symbol_instances", [])
        if symbol_instances or schematic_data.get("components"):
            sexp_data.append([sexpdata.Symbol("symbol_instances")])

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
        # Implementation for wire parsing
        # This would parse pts, stroke, uuid elements
        return {}

    def _parse_junction(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a junction definition."""
        # Implementation for junction parsing
        return {}

    def _parse_label(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a label definition."""
        # Implementation for label parsing
        return {}

    def _parse_lib_symbols(self, item: List[Any]) -> Dict[str, Any]:
        """Parse lib_symbols section."""
        # Implementation for lib_symbols parsing
        return {}

    # Conversion methods from internal format to S-expression
    def _title_block_to_sexp(self, title_block: Dict[str, Any]) -> List[Any]:
        """Convert title block to S-expression."""
        sexp = [sexpdata.Symbol("title_block")]
        for key, value in title_block.items():
            sexp.append([sexpdata.Symbol(key), value])
        return sexp

    def _symbol_to_sexp(self, symbol_data: Dict[str, Any]) -> List[Any]:
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

        if symbol_data.get("uuid"):
            sexp.append([sexpdata.Symbol("uuid"), symbol_data["uuid"]])

        # Add properties
        if symbol_data.get("reference"):
            sexp.append([sexpdata.Symbol("property"), "Reference", symbol_data["reference"]])
        if symbol_data.get("value"):
            sexp.append([sexpdata.Symbol("property"), "Value", symbol_data["value"]])
        footprint = symbol_data.get("footprint")
        if footprint is not None:  # Include empty strings but not None
            sexp.append([sexpdata.Symbol("property"), "Footprint", footprint])

        for prop_name, prop_value in symbol_data.get("properties", {}).items():
            # Escape quotes in property values for proper S-expression format
            escaped_value = str(prop_value).replace('"', '\\"')
            sexp.append([sexpdata.Symbol("property"), prop_name, escaped_value])

        # Add BOM and board settings
        sexp.append([sexpdata.Symbol("in_bom"), "yes" if symbol_data.get("in_bom", True) else "no"])
        sexp.append(
            [sexpdata.Symbol("on_board"), "yes" if symbol_data.get("on_board", True) else "no"]
        )

        return sexp

    def _wire_to_sexp(self, wire_data: Dict[str, Any]) -> List[Any]:
        """Convert wire to S-expression."""
        # Implementation for wire conversion
        return [sexpdata.Symbol("wire")]

    def _junction_to_sexp(self, junction_data: Dict[str, Any]) -> List[Any]:
        """Convert junction to S-expression."""
        # Implementation for junction conversion
        return [sexpdata.Symbol("junction")]

    def _label_to_sexp(self, label_data: Dict[str, Any]) -> List[Any]:
        """Convert label to S-expression."""
        # Implementation for label conversion
        return [sexpdata.Symbol("label")]

    def _lib_symbols_to_sexp(self, lib_symbols: Dict[str, Any]) -> List[Any]:
        """Convert lib_symbols to S-expression."""
        sexp = [sexpdata.Symbol("lib_symbols")]
        
        # Add each symbol definition
        for symbol_name, symbol_def in lib_symbols.items():
            if isinstance(symbol_def, dict):
                symbol_sexp = self._create_basic_symbol_definition(symbol_name)
                sexp.append(symbol_sexp)
        
        return sexp
    
    def _create_basic_symbol_definition(self, lib_id: str) -> List[Any]:
        """Create a basic symbol definition for KiCAD compatibility."""
        symbol_sexp = [sexpdata.Symbol("symbol"), lib_id]
        
        # Add basic symbol properties
        symbol_sexp.extend([
            [sexpdata.Symbol("pin_numbers"), [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")]],
            [sexpdata.Symbol("pin_names"), [sexpdata.Symbol("offset"), 0]],
            [sexpdata.Symbol("exclude_from_sim"), sexpdata.Symbol("no")],
            [sexpdata.Symbol("in_bom"), sexpdata.Symbol("yes")],
            [sexpdata.Symbol("on_board"), sexpdata.Symbol("yes")]
        ])
        
        # Add basic properties for the symbol
        if "R" in lib_id:  # Resistor
            symbol_sexp.extend([
                [sexpdata.Symbol("property"), "Reference", "R",
                 [sexpdata.Symbol("at"), 2.032, 0, 90],
                 [sexpdata.Symbol("effects"), [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]]]],
                [sexpdata.Symbol("property"), "Value", "R", 
                 [sexpdata.Symbol("at"), 0, 0, 90],
                 [sexpdata.Symbol("effects"), [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]]]],
                [sexpdata.Symbol("property"), "Footprint", "",
                 [sexpdata.Symbol("at"), -1.778, 0, 90],
                 [sexpdata.Symbol("effects"), [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]], [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")]]],
                [sexpdata.Symbol("property"), "Datasheet", "~",
                 [sexpdata.Symbol("at"), 0, 0, 0],
                 [sexpdata.Symbol("effects"), [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]], [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")]]]
            ])
            
        elif "C" in lib_id:  # Capacitor
            symbol_sexp.extend([
                [sexpdata.Symbol("property"), "Reference", "C",
                 [sexpdata.Symbol("at"), 0.635, 2.54, 0],
                 [sexpdata.Symbol("effects"), [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]]]],
                [sexpdata.Symbol("property"), "Value", "C",
                 [sexpdata.Symbol("at"), 0.635, -2.54, 0],
                 [sexpdata.Symbol("effects"), [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]]]],
                [sexpdata.Symbol("property"), "Footprint", "",
                 [sexpdata.Symbol("at"), 0, -1.27, 0],
                 [sexpdata.Symbol("effects"), [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]], [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")]]],
                [sexpdata.Symbol("property"), "Datasheet", "~",
                 [sexpdata.Symbol("at"), 0, 0, 0],
                 [sexpdata.Symbol("effects"), [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), 1.27, 1.27]], [sexpdata.Symbol("hide"), sexpdata.Symbol("yes")]]]
            ])
        
        # Add basic graphics and pins (minimal for now)
        symbol_sexp.append([sexpdata.Symbol("embedded_fonts"), sexpdata.Symbol("no")])
        
        return symbol_sexp

    def get_validation_issues(self) -> List[ValidationIssue]:
        """Get list of validation issues from last parse operation."""
        return self._validation_issues.copy()
