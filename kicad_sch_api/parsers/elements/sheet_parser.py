"""
Hierarchical sheet elements parser for KiCAD schematics.

Handles parsing and serialization of Hierarchical sheet elements.
"""

import logging
from typing import Any, Dict, List, Optional

import sexpdata

from ...core.config import config
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class SheetParser(BaseElementParser):
    """Parser for Hierarchical sheet elements."""

    def __init__(self):
        """Initialize sheet parser."""
        super().__init__("sheet")

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
            "page_number": "2",
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
                            sheet_data["fill_color"] = (
                                int(fill_elem[1]),
                                int(fill_elem[2]),
                                int(fill_elem[3]),
                                float(fill_elem[4]),
                            )
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
                                        sheet_data["page_number"] = (
                                            str(page_elem[1]) if len(page_elem) > 1 else "2"
                                        )

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
            "size": config.defaults.font_size,
            "justify": "right",
            "uuid": None,
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
        from ...core.config import config

        name_prop = [sexpdata.Symbol("property"), "Sheetname", name]
        name_prop.append(
            [sexpdata.Symbol("at"), x, round(y + config.sheet.name_offset_y, 4), 0]
        )  # Above sheet
        name_prop.append(
            [
                sexpdata.Symbol("effects"),
                [
                    sexpdata.Symbol("font"),
                    [sexpdata.Symbol("size"), config.defaults.font_size, config.defaults.font_size],
                ],
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
                [
                    sexpdata.Symbol("font"),
                    [sexpdata.Symbol("size"), config.defaults.font_size, config.defaults.font_size],
                ],
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
        size = pin_data.get("size", config.defaults.font_size)
        effects = [sexpdata.Symbol("effects")]
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), size, size]]
        effects.append(font)
        justify = pin_data.get("justify", "right")
        effects.append([sexpdata.Symbol("justify"), sexpdata.Symbol(justify)])
        pin_sexp.append(effects)

        return pin_sexp

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
