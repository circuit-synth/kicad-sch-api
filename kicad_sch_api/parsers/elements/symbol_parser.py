"""
Component symbol elements parser for KiCAD schematics.

Handles parsing and serialization of Component symbol elements.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

import sexpdata

from ...core.parsing_utils import parse_bool_property
from ...core.types import ComponentProperty, Point, PropertyEffects
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class SymbolParser(BaseElementParser):
    """Parser for Component symbol elements."""

    def __init__(self):
        """Initialize symbol parser."""
        super().__init__("symbol")

    def _parse_symbol(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a symbol (component) definition."""
        try:
            symbol_data = {
                "lib_id": None,
                "position": Point(0, 0),
                "rotation": 0,
                "uuid": None,
                # Property objects with complete formatting
                "reference_property": None,
                "value_property": None,
                "footprint_property": None,
                "custom_properties": {},
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
                    prop = self._parse_property(sub_item)  # Returns ComponentProperty
                    if prop:
                        if prop.name == "Reference":
                            symbol_data["reference_property"] = prop
                        elif prop.name == "Value":
                            symbol_data["value_property"] = prop
                        elif prop.name == "Footprint":
                            symbol_data["footprint_property"] = prop
                        else:
                            # Unescape quotes in custom property values when loading
                            if prop.value:
                                prop.value = str(prop.value).replace('\\"', '"')
                            symbol_data["custom_properties"][prop.name] = prop
                elif element_type == "in_bom":
                    symbol_data["in_bom"] = parse_bool_property(
                        sub_item[1] if len(sub_item) > 1 else None,
                        default=True
                    )
                elif element_type == "on_board":
                    symbol_data["on_board"] = parse_bool_property(
                        sub_item[1] if len(sub_item) > 1 else None,
                        default=True
                    )

            return symbol_data

        except Exception as e:
            logger.warning(f"Error parsing symbol: {e}")
            return None


    def _parse_property(self, item: List[Any]) -> Optional[ComponentProperty]:
        """
        Parse a complete property definition with all attributes.

        Args:
            item: S-expression list for property

        Returns:
            ComponentProperty with all formatting data, or None if invalid
        """
        if len(item) < 3:
            return None

        # Create property with name and value
        prop = ComponentProperty(
            name=str(item[1]),
            value=str(item[2])
        )

        # Parse sub-elements (position, rotation, effects)
        for sub_item in item[3:]:
            if not isinstance(sub_item, list) or len(sub_item) == 0:
                continue

            element_type = str(sub_item[0]) if isinstance(sub_item[0], sexpdata.Symbol) else None

            # Parse position and rotation
            if element_type == "at" and len(sub_item) >= 3:
                prop.position = (float(sub_item[1]), float(sub_item[2]))
                if len(sub_item) > 3:
                    prop.rotation = float(sub_item[3])

            # Parse effects
            elif element_type == "effects":
                prop.effects = self._parse_property_effects(sub_item)

        return prop

    def _parse_property_effects(self, effects_sexp: List) -> PropertyEffects:
        """
        Parse (effects ...) sub-element of a property.

        Args:
            effects_sexp: S-expression list for effects

        Returns:
            PropertyEffects object with font, justification, and hide flag
        """
        effects = PropertyEffects()

        for item in effects_sexp[1:]:
            if not isinstance(item, list):
                continue

            element_type = str(item[0]) if isinstance(item[0], sexpdata.Symbol) else None

            if element_type == "font":
                # Parse font size
                for font_item in item[1:]:
                    if isinstance(font_item, list) and len(font_item) >= 3:
                        if str(font_item[0]) == "size":
                            effects.font_size = (float(font_item[1]), float(font_item[2]))

            elif element_type == "justify" and len(item) > 1:
                effects.justification = str(item[1])

            elif element_type == "hide":
                effects.hide = True

        return effects


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

        # Add properties - use property objects if available, otherwise fallback to creating defaults
        lib_id = symbol_data.get("lib_id", "")
        is_power_symbol = "power:" in lib_id

        # Reference property
        ref_prop = symbol_data.get("reference_property")
        if ref_prop:
            # Use stored property object (preserves formatting)
            sexp.append(ref_prop.to_sexp())
        elif symbol_data.get("reference"):
            # Fallback: create with defaults (for programmatically created components)
            ref_prop = ComponentProperty(
                "Reference",
                symbol_data["reference"],
                effects=PropertyEffects(hide=is_power_symbol)
            )
            # Add default positioning if not specified
            ref_prop = self._create_property_with_positioning(
                "Reference", symbol_data["reference"], pos, 0, "left", hide=is_power_symbol
            )
            sexp.append(ref_prop)

        # Value property
        val_prop = symbol_data.get("value_property")
        if val_prop:
            # Use stored property object (preserves formatting)
            sexp.append(val_prop.to_sexp())
        elif symbol_data.get("value"):
            # Fallback: create with defaults
            if is_power_symbol:
                val_prop = self._create_power_symbol_value_property(
                    symbol_data["value"], pos, lib_id
                )
            else:
                val_prop = self._create_property_with_positioning(
                    "Value", symbol_data["value"], pos, 1, "left"
                )
            sexp.append(val_prop)

        # Footprint property
        fp_prop = symbol_data.get("footprint_property")
        if fp_prop:
            # Use stored property object (preserves formatting)
            sexp.append(fp_prop.to_sexp())
        elif symbol_data.get("footprint") is not None:
            # Fallback: create with defaults
            fp_prop = self._create_property_with_positioning(
                "Footprint", symbol_data["footprint"], pos, 2, "left", hide=True
            )
            sexp.append(fp_prop)

        # Custom properties
        for prop_name, prop in symbol_data.get("custom_properties", {}).items():
            # Escape quotes in custom property values
            if prop.value:
                prop.value = str(prop.value).replace('"', '\\"')
            sexp.append(prop.to_sexp())

        # Add pin UUID assignments (required by KiCAD)
        for pin in symbol_data.get("pins", []):
            pin_uuid = str(uuid.uuid4())
            # Ensure pin number is a string for proper quoting
            pin_number = str(pin.number)
            sexp.append([sexpdata.Symbol("pin"), pin_number, [sexpdata.Symbol("uuid"), pin_uuid]])

        # Add instances section (required by KiCAD)
        from ...core.config import config

        # Get project name from config or custom properties
        custom_props = symbol_data.get("custom_properties", {})
        project_name = custom_props.get("project_name").value if "project_name" in custom_props else None
        if not project_name:
            project_name = getattr(self, "project_name", config.defaults.project_name)

        # CRITICAL FIX: Use the FULL hierarchy_path from properties if available
        # For hierarchical schematics, this contains the complete path: /root_uuid/sheet_symbol_uuid/...
        # This ensures KiCad can properly annotate components in sub-sheets
        hierarchy_path = custom_props.get("hierarchy_path").value if "hierarchy_path" in custom_props else None
        if hierarchy_path:
            # Use the full hierarchical path (includes root + all sheet symbols)
            instance_path = hierarchy_path
            logger.debug(
                f"🔧 Using FULL hierarchy_path: {instance_path} for component {symbol_data.get('reference_property').value if symbol_data.get('reference_property') else 'unknown'}"
            )
        else:
            # Fallback: use root_uuid or schematic_uuid for flat designs
            root_uuid = (
                custom_props.get("root_uuid").value if "root_uuid" in custom_props else None
            ) or schematic_uuid or str(uuid.uuid4())
            instance_path = f"/{root_uuid}"
            logger.debug(
                f"🔧 Using root UUID path: {instance_path} for component {symbol_data.get('reference_property').value if symbol_data.get('reference_property') else 'unknown'}"
            )

        logger.debug(
            f"🔧 Component custom properties keys: {list(symbol_data.get('custom_properties', {}).keys())}"
        )
        logger.debug(f"🔧 Using project name: '{project_name}'")

        # Get reference value from property object
        reference = (
            symbol_data.get("reference_property").value
            if symbol_data.get("reference_property")
            else "U?"
        )

        sexp.append(
            [
                sexpdata.Symbol("instances"),
                [
                    sexpdata.Symbol("project"),
                    project_name,
                    [
                        sexpdata.Symbol("path"),
                        instance_path,
                        [sexpdata.Symbol("reference"), reference],
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
        from ...core.config import config

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


