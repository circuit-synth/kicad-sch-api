"""
Component symbol elements parser for KiCAD schematics.

Handles parsing and serialization of Component symbol elements.
"""

import logging
import uuid
from typing import Any, Dict, List, Optional

import sexpdata

from ...core.parsing_utils import parse_bool_property
from ...core.types import Point
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

                        # Store original S-expression for format preservation
                        sexp_key = f"__sexp_{prop_name}"
                        symbol_data["properties"][sexp_key] = sub_item

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


    def _parse_property(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a property definition."""
        if len(item) < 3:
            return None

        return {
            "name": item[1] if len(item) > 1 else None,
            "value": item[2] if len(item) > 2 else None,
        }


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
        rotation = symbol_data.get("rotation", 0)

        if symbol_data.get("reference"):
            # Check for preserved S-expression
            preserved_ref = symbol_data.get("properties", {}).get("__sexp_Reference")
            if preserved_ref:
                # Use preserved format but update the value
                ref_prop = list(preserved_ref)
                if len(ref_prop) >= 3:
                    ref_prop[2] = symbol_data["reference"]
                sexp.append(ref_prop)
            else:
                # No preserved format - create new (for newly added components)
                ref_hide = is_power_symbol
                ref_prop = self._create_property_with_positioning(
                    "Reference", symbol_data["reference"], pos, 0, "left", hide=ref_hide, rotation=rotation
                )
                sexp.append(ref_prop)

        if symbol_data.get("value"):
            # Check for preserved S-expression
            preserved_val = symbol_data.get("properties", {}).get("__sexp_Value")
            if preserved_val:
                # Use preserved format but update the value
                val_prop = list(preserved_val)
                if len(val_prop) >= 3:
                    val_prop[2] = symbol_data["value"]
                sexp.append(val_prop)
            else:
                # No preserved format - create new (for newly added components)
                if is_power_symbol:
                    val_prop = self._create_power_symbol_value_property(
                        symbol_data["value"], pos, lib_id, rotation
                    )
                else:
                    val_prop = self._create_property_with_positioning(
                        "Value", symbol_data["value"], pos, 1, "left", rotation=rotation
                    )
                sexp.append(val_prop)

        footprint = symbol_data.get("footprint")
        if footprint is not None:  # Include empty strings but not None
            # Check for preserved S-expression
            preserved_fp = symbol_data.get("properties", {}).get("__sexp_Footprint")
            if preserved_fp:
                # Use preserved format but update the value
                fp_prop = list(preserved_fp)
                if len(fp_prop) >= 3:
                    fp_prop[2] = footprint
                sexp.append(fp_prop)
            else:
                # No preserved format - create new (for newly added components)
                fp_prop = self._create_property_with_positioning(
                    "Footprint", footprint, pos, 2, "left", hide=True
                )
                sexp.append(fp_prop)

        for prop_name, prop_value in symbol_data.get("properties", {}).items():
            # Skip internal preservation keys
            if prop_name.startswith("__sexp_"):
                continue

            # Check if we have a preserved S-expression for this custom property
            preserved_prop = symbol_data.get("properties", {}).get(f"__sexp_{prop_name}")
            if preserved_prop:
                # Use preserved format but update the value
                prop = list(preserved_prop)
                if len(prop) >= 3:
                    # Re-escape quotes when saving
                    escaped_value = str(prop_value).replace('"', '\\"')
                    prop[2] = escaped_value
                sexp.append(prop)
            else:
                # No preserved format - create new (for newly added properties)
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
        from ...core.config import config

        # HIERARCHICAL FIX: Check if user explicitly set instances
        # If so, preserve them exactly as-is (don't generate!)
        user_instances = symbol_data.get("instances")
        if user_instances:
            logger.debug(f"🔍 HIERARCHICAL FIX: Component {symbol_data.get('reference')} has {len(user_instances)} user-set instance(s)")
            # Build instances sexp from user data
            instances_sexp = [sexpdata.Symbol("instances")]
            for inst in user_instances:
                project = inst.get('project', getattr(self, 'project_name', 'circuit'))
                path = inst.get('path', '/')
                reference = inst.get('reference', symbol_data.get('reference', 'U?'))
                unit = inst.get('unit', 1)

                logger.debug(f"   Instance: project={project}, path={path}, ref={reference}, unit={unit}")

                instances_sexp.append([
                    sexpdata.Symbol("project"),
                    project,
                    [
                        sexpdata.Symbol("path"),
                        path,  # PRESERVE user-set hierarchical path!
                        [sexpdata.Symbol("reference"), reference],
                        [sexpdata.Symbol("unit"), unit],
                    ],
                ])
            sexp.append(instances_sexp)
        else:
            # No user-set instances - generate default (backward compatibility)
            logger.debug(f"🔍 HIERARCHICAL FIX: Component {symbol_data.get('reference')} has NO user instances, generating default")

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
                logger.debug(
                    f"🔧 Using FULL hierarchy_path: {instance_path} for component {symbol_data.get('reference', 'unknown')}"
                )
            else:
                # Fallback: use root_uuid or schematic_uuid for flat designs
                root_uuid = (
                    symbol_data.get("properties", {}).get("root_uuid")
                    or schematic_uuid
                    or str(uuid.uuid4())
                )
                instance_path = f"/{root_uuid}"
                logger.debug(
                    f"🔧 Using root UUID path: {instance_path} for component {symbol_data.get('reference', 'unknown')}"
                )

            logger.debug(
                f"🔧 Component properties keys: {list(symbol_data.get('properties', {}).keys())}"
            )
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
        rotation: float = 0,
    ) -> List[Any]:
        """Create a property with proper positioning and effects like KiCAD."""
        from ...core.config import config

        # Calculate property position using configuration
        prop_x, prop_y, text_rotation = config.get_property_position(
            prop_name, (component_pos.x, component_pos.y), offset_index, rotation
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
                text_rotation,
            ],
            effects,
        ]

        return prop_sexp


    def _create_power_symbol_value_property(
        self, value: str, component_pos: Point, lib_id: str, rotation: float = 0
    ) -> List[Any]:
        """Create Value property for power symbols with correct positioning.

        Matches circuit-synth power_symbol_positioning.py logic exactly.
        """
        offset = 5.08  # KiCad standard offset
        is_gnd_type = "GND" in lib_id.upper() or "VSS" in lib_id.upper()

        # Rotation-aware positioning (matching circuit-synth logic)
        if rotation == 0:
            if is_gnd_type:
                prop_x, prop_y = component_pos.x, component_pos.y + offset  # GND points down, text below
            else:
                prop_x, prop_y = component_pos.x, component_pos.y - offset  # VCC points up, text above
        elif rotation == 90:
            if is_gnd_type:
                prop_x, prop_y = component_pos.x - offset, component_pos.y  # GND left, text left
            else:
                prop_x, prop_y = component_pos.x + offset, component_pos.y  # VCC right, text right
        elif rotation == 180:
            if is_gnd_type:
                prop_x, prop_y = component_pos.x, component_pos.y - offset  # GND inverted up, text above
            else:
                prop_x, prop_y = component_pos.x, component_pos.y + offset  # VCC inverted down, text below
        elif rotation == 270:
            if is_gnd_type:
                prop_x, prop_y = component_pos.x + offset, component_pos.y  # GND right, text right
            else:
                prop_x, prop_y = component_pos.x - offset, component_pos.y  # VCC left, text left
        else:
            # Fallback for non-standard rotations
            prop_x, prop_y = component_pos.x, component_pos.y - offset if not is_gnd_type else component_pos.y + offset

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


