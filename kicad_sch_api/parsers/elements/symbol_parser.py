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
                "pin_uuids": {},  # Maps pin number to UUID
                "hidden_properties": set(),  # Properties with (hide yes) flag
                "in_bom": True,
                "on_board": True,
                "fields_autoplaced": False,
                "unit": 1,  # Multi-unit component support: unit number (default 1)
                "instances": [],
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
                elif element_type == "unit":
                    # Parse unit number for multi-unit components
                    symbol_data["unit"] = int(sub_item[1]) if len(sub_item) > 1 else 1
                elif element_type == "property":
                    prop_data = self._parse_property(sub_item)
                    if prop_data:
                        prop_name = prop_data.get("name")

                        # Store original S-expression for format preservation
                        sexp_key = f"__sexp_{prop_name}"
                        symbol_data["properties"][sexp_key] = sub_item

                        # Store parsed property dict for easy access (used by tests and API)
                        symbol_data["properties"][prop_name] = prop_data

                        # Check if property is hidden
                        if prop_data.get("hidden", False):
                            symbol_data["hidden_properties"].add(prop_name)

                        # Also extract standard properties to dedicated fields for backward compatibility
                        if prop_name == "Reference":
                            symbol_data["reference"] = prop_data.get("value")
                        elif prop_name == "Value":
                            symbol_data["value"] = prop_data.get("value")
                        elif prop_name == "Footprint":
                            symbol_data["footprint"] = prop_data.get("value")
                elif element_type == "in_bom":
                    symbol_data["in_bom"] = parse_bool_property(
                        sub_item[1] if len(sub_item) > 1 else None, default=True
                    )
                elif element_type == "on_board":
                    symbol_data["on_board"] = parse_bool_property(
                        sub_item[1] if len(sub_item) > 1 else None, default=True
                    )
                elif element_type == "fields_autoplaced":
                    symbol_data["fields_autoplaced"] = parse_bool_property(
                        sub_item[1] if len(sub_item) > 1 else None, default=True
                    )
                elif element_type == "instances":
                    # Parse instances section
                    instances = self._parse_instances(sub_item)
                    if instances:
                        symbol_data["instances"] = instances
                elif element_type == "pin":
                    # Parse pin UUID: (pin "1" (uuid "..."))
                    pin_data = self._parse_pin_uuid(sub_item)
                    if pin_data:
                        pin_number = pin_data.get("number")
                        pin_uuid = pin_data.get("uuid")
                        if pin_number and pin_uuid:
                            symbol_data["pin_uuids"][pin_number] = pin_uuid

            return symbol_data

        except Exception as e:
            logger.warning(f"Error parsing symbol: {e}")
            return None

    def _update_property_hide_flag(self, property_sexp: List[Any], should_hide: bool) -> List[Any]:
        """
        Update the hide flag in a property S-expression.

        Args:
            property_sexp: Property S-expression list
            should_hide: True to add (hide yes), False to remove hide flag

        Returns:
            Updated property S-expression
        """
        # Make a copy to avoid modifying original
        prop = list(property_sexp)

        # Find effects section
        effects_index = None
        for i, item in enumerate(prop):
            if isinstance(item, list) and len(item) > 0:
                if isinstance(item[0], sexpdata.Symbol) and str(item[0]) == "effects":
                    effects_index = i
                    break

        if effects_index is None:
            # No effects section - if we need to hide, we'd need to create one
            # For now, just return as-is (this shouldn't happen with valid KiCAD files)
            return prop

        # Get effects section
        effects = list(prop[effects_index])

        # Find hide clause within effects
        hide_index = None
        for i, item in enumerate(effects):
            if isinstance(item, list) and len(item) > 0:
                if isinstance(item[0], sexpdata.Symbol) and str(item[0]) == "hide":
                    hide_index = i
                    break

        if should_hide:
            # Add hide flag if not present
            if hide_index is None:
                effects.append([sexpdata.Symbol("hide"), sexpdata.Symbol("yes")])
        else:
            # Remove hide flag if present
            if hide_index is not None:
                effects.pop(hide_index)

        # Update effects in property
        prop[effects_index] = effects

        return prop

    def _parse_property(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """Parse a property definition and extract all metadata.

        Returns dict with keys:
        - name: Property name
        - value: Property value
        - hidden: Whether property is hidden
        - at: Position tuple (x, y, rotation)
        - effects: Effects dict with font, justify, hide
        """
        if len(item) < 3:
            return None

        # Extract name and value
        prop_name = item[1] if len(item) > 1 else None
        prop_value = item[2] if len(item) > 2 else None

        # Initialize parsed data
        position = None
        is_hidden = False
        justify = None
        effects_dict = {}

        # Parse sub-elements (at, effects, etc.)
        for sub_item in item[3:]:
            if not isinstance(sub_item, list) or len(sub_item) == 0:
                continue

            element_type = str(sub_item[0]) if isinstance(sub_item[0], sexpdata.Symbol) else None

            if element_type == "at":
                # Parse position: (at x y rotation)
                if len(sub_item) >= 3:
                    x = float(sub_item[1])
                    y = float(sub_item[2])
                    rotation = float(sub_item[3]) if len(sub_item) > 3 else 0.0
                    position = [x, y, rotation]

            elif element_type == "effects":
                # Parse effects section
                for effect_item in sub_item[1:]:
                    if not isinstance(effect_item, list) or len(effect_item) == 0:
                        continue

                    effect_type = (
                        str(effect_item[0]) if isinstance(effect_item[0], sexpdata.Symbol) else None
                    )

                    if effect_type == "hide":
                        # Check if value is "yes"
                        if len(effect_item) > 1:
                            hide_value = str(effect_item[1])
                            is_hidden = hide_value.lower() in ["yes", "true"]
                        else:
                            # Just (hide) with no value defaults to yes
                            is_hidden = True
                        effects_dict["hide"] = "yes" if is_hidden else "no"

                    elif effect_type == "justify":
                        # Extract justify value: (justify left|right|center)
                        if len(effect_item) > 1:
                            justify = str(effect_item[1])
                            effects_dict["justify"] = justify

                    elif effect_type == "font":
                        # Store font info if needed
                        effects_dict["font"] = effect_item

        result = {
            "name": prop_name,
            "value": prop_value,
            "hidden": is_hidden,
        }

        if position is not None:
            result["at"] = position

        if effects_dict:
            result["effects"] = effects_dict

        return result

    def _parse_instances(self, item: List[Any]) -> List[Dict[str, Any]]:
        """
        Parse instances section from S-expression.

        Format:
        (instances
            (project "project_name"
                (path "/root_uuid/sheet_uuid"
                    (reference "R1")
                    (unit 1))))
        """
        from ...core.types import SymbolInstance

        instances = []

        for sub_item in item[1:]:
            if not isinstance(sub_item, list) or len(sub_item) == 0:
                continue

            element_type = str(sub_item[0]) if isinstance(sub_item[0], sexpdata.Symbol) else None

            if element_type == "project":
                # Parse project instance
                project = sub_item[1] if len(sub_item) > 1 else None

                # Find path section within project
                for project_sub in sub_item[2:]:
                    if not isinstance(project_sub, list) or len(project_sub) == 0:
                        continue

                    path_type = (
                        str(project_sub[0]) if isinstance(project_sub[0], sexpdata.Symbol) else None
                    )

                    if path_type == "path":
                        # Extract path value
                        path = project_sub[1] if len(project_sub) > 1 else "/"
                        reference = None
                        unit = 1

                        # Parse reference and unit from path subsections
                        for path_sub in project_sub[2:]:
                            if not isinstance(path_sub, list) or len(path_sub) == 0:
                                continue

                            path_sub_type = (
                                str(path_sub[0])
                                if isinstance(path_sub[0], sexpdata.Symbol)
                                else None
                            )

                            if path_sub_type == "reference":
                                reference = path_sub[1] if len(path_sub) > 1 else None
                            elif path_sub_type == "unit":
                                unit = int(path_sub[1]) if len(path_sub) > 1 else 1

                        # Create instance
                        if path and reference:
                            instance = SymbolInstance(
                                path=path,
                                reference=reference,
                                unit=unit,
                                project=project if project is not None else "",
                            )
                            instances.append(instance)

        return instances

    def _parse_pin_uuid(self, item: List[Any]) -> Optional[Dict[str, Any]]:
        """
        Parse pin UUID from S-expression.

        Format:
        (pin "1" (uuid "df660b58-5cdf-473e-8c0a-859cae977374"))

        Returns:
            Dict with 'number' and 'uuid' keys, or None if invalid
        """
        try:
            if len(item) < 2:
                return None

            # Pin number is the second element
            pin_number = str(item[1])

            # Look for uuid sub-element
            pin_uuid = None
            for sub_item in item[2:]:
                if not isinstance(sub_item, list) or len(sub_item) == 0:
                    continue

                element_type = (
                    str(sub_item[0]) if isinstance(sub_item[0], sexpdata.Symbol) else None
                )
                if element_type == "uuid":
                    pin_uuid = sub_item[1] if len(sub_item) > 1 else None
                    break

            if pin_number and pin_uuid:
                return {
                    "number": pin_number,
                    "uuid": pin_uuid,
                }

            return None

        except Exception as e:
            logger.warning(f"Error parsing pin UUID: {e}")
            return None

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
        sexp.append(
            [
                sexpdata.Symbol("fields_autoplaced"),
                "yes" if symbol_data.get("fields_autoplaced", True) else "no",
            ]
        )

        if symbol_data.get("uuid"):
            sexp.append([sexpdata.Symbol("uuid"), symbol_data["uuid"]])

        # Add properties with proper positioning and effects
        lib_id = symbol_data.get("lib_id", "")
        is_power_symbol = "power:" in lib_id
        rotation = symbol_data.get("rotation", 0)

        # Get hidden_properties set for visibility control
        hidden_props = symbol_data.get("hidden_properties", set())

        if symbol_data.get("reference"):
            # Check for preserved S-expression
            preserved_ref = symbol_data.get("properties", {}).get("__sexp_Reference")
            if preserved_ref:
                # Use preserved format but update value and hide flag
                ref_prop = list(preserved_ref)
                if len(ref_prop) >= 3:
                    ref_prop[2] = symbol_data["reference"]
                # Update hide flag based on hidden_properties set
                ref_should_hide = "Reference" in hidden_props
                ref_prop = self._update_property_hide_flag(ref_prop, ref_should_hide)
                sexp.append(ref_prop)
            else:
                # No preserved format - create new (for newly added components)
                # Default: hide for power symbols, otherwise visible
                ref_hide = (
                    "Reference" in hidden_props
                    if "Reference" in hidden_props or not is_power_symbol
                    else is_power_symbol
                )
                ref_prop = self._create_property_with_positioning(
                    "Reference",
                    symbol_data["reference"],
                    pos,
                    0,
                    "left",
                    hide=ref_hide,
                    rotation=rotation,
                    lib_id=lib_id,
                )
                sexp.append(ref_prop)

        if symbol_data.get("value"):
            # Check for preserved S-expression
            preserved_val = symbol_data.get("properties", {}).get("__sexp_Value")
            if preserved_val:
                # Use preserved format but update value and hide flag
                val_prop = list(preserved_val)
                if len(val_prop) >= 3:
                    val_prop[2] = symbol_data["value"]
                # Update hide flag based on hidden_properties set
                val_should_hide = "Value" in hidden_props
                val_prop = self._update_property_hide_flag(val_prop, val_should_hide)
                sexp.append(val_prop)
            else:
                # No preserved format - create new (for newly added components)
                val_hide = "Value" in hidden_props
                if is_power_symbol:
                    val_prop = self._create_power_symbol_value_property(
                        symbol_data["value"], pos, lib_id, rotation
                    )
                else:
                    val_prop = self._create_property_with_positioning(
                        "Value",
                        symbol_data["value"],
                        pos,
                        1,
                        "left",
                        hide=val_hide,
                        rotation=rotation,
                        lib_id=lib_id,
                    )
                sexp.append(val_prop)

        footprint = symbol_data.get("footprint")
        if footprint is not None:  # Include empty strings but not None
            # Check for preserved S-expression
            preserved_fp = symbol_data.get("properties", {}).get("__sexp_Footprint")
            if preserved_fp:
                # Use preserved format but update value and hide flag
                fp_prop = list(preserved_fp)
                if len(fp_prop) >= 3:
                    fp_prop[2] = footprint
                # Update hide flag based on hidden_properties set
                fp_should_hide = "Footprint" in hidden_props
                fp_prop = self._update_property_hide_flag(fp_prop, fp_should_hide)
                sexp.append(fp_prop)
            else:
                # No preserved format - create new (for newly added components)
                # Default: Footprint is usually hidden
                fp_hide = "Footprint" in hidden_props if "Footprint" in hidden_props else True
                fp_prop = self._create_property_with_positioning(
                    "Footprint", footprint, pos, 2, "left", hide=fp_hide, lib_id=lib_id
                )
                sexp.append(fp_prop)

        # Standard properties that are typically hidden by KiCAD (unless explicitly made visible)
        STANDARD_HIDDEN_PROPS = {
            "Datasheet",
            "Description",
            "ki_keywords",
            "ki_description",
            "ki_fp_filters",
        }

        # Standard properties handled separately above
        STANDARD_PROPERTIES = {"Reference", "Value", "Footprint"}

        for prop_name, prop_value in symbol_data.get("properties", {}).items():
            # Skip internal preservation keys
            if prop_name.startswith("__sexp_"):
                continue

            # Skip standard properties (Reference, Value, Footprint) - already handled above
            if prop_name in STANDARD_PROPERTIES:
                continue

            # Extract actual value - prop_value might be a dict (parsed property) or string (legacy)
            if isinstance(prop_value, dict):
                actual_value = prop_value.get("value", "")
            else:
                actual_value = prop_value

            # Determine hide state:
            # 1. If explicitly in hidden_props -> hide
            # 2. Else if standard property -> default to hidden
            # 3. Else custom property -> default to visible
            if prop_name in hidden_props:
                should_hide = True
            elif prop_name in STANDARD_HIDDEN_PROPS:
                should_hide = True
            else:
                should_hide = False

            # Check if we have a preserved S-expression for this custom property
            preserved_prop = symbol_data.get("properties", {}).get(f"__sexp_{prop_name}")
            if preserved_prop:
                # Use preserved format but update value and hide flag
                prop = list(preserved_prop)
                if len(prop) >= 3:
                    # Re-escape quotes when saving
                    escaped_value = str(actual_value).replace('"', '\\"')
                    prop[2] = escaped_value

                # Update hide flag based on hidden_properties set
                prop = self._update_property_hide_flag(prop, should_hide)
                sexp.append(prop)
            else:
                # No preserved format - create new (for newly added properties)
                escaped_value = str(actual_value).replace('"', '\\"')
                prop = self._create_property_with_positioning(
                    prop_name, escaped_value, pos, 3, "left", hide=should_hide
                )
                sexp.append(prop)

        # Add pin UUID assignments (required by KiCAD)
        pin_uuids_dict = symbol_data.get("pin_uuids", {})
        pins_list = symbol_data.get("pins", [])

        # If we have stored pin UUIDs, use those (loaded from file)
        if pin_uuids_dict:
            for pin_number, pin_uuid in pin_uuids_dict.items():
                sexp.append(
                    [sexpdata.Symbol("pin"), str(pin_number), [sexpdata.Symbol("uuid"), pin_uuid]]
                )
        # Otherwise, generate UUIDs for pins from library definition (newly added components)
        elif pins_list:
            for pin in pins_list:
                pin_number = str(pin.number)
                pin_uuid = str(uuid.uuid4())
                sexp.append(
                    [sexpdata.Symbol("pin"), pin_number, [sexpdata.Symbol("uuid"), pin_uuid]]
                )

        # Add instances section (required by KiCAD)
        from ...core.config import config

        # HIERARCHICAL FIX: Check if user explicitly set instances
        # If so, preserve them exactly as-is (don't generate!)
        user_instances = symbol_data.get("instances")
        if user_instances:
            logger.debug(
                f"🔍 HIERARCHICAL FIX: Component {symbol_data.get('reference')} has {len(user_instances)} user-set instance(s)"
            )
            # Build instances sexp from user data
            instances_sexp = [sexpdata.Symbol("instances")]
            for inst in user_instances:
                # Handle both SymbolInstance objects and dicts for backward compatibility
                if hasattr(inst, "project"):  # SymbolInstance object
                    project = inst.project
                    path = inst.path
                    reference = inst.reference
                    unit = inst.unit
                else:  # Dict (legacy)
                    project = inst.get("project", getattr(self, "project_name", "circuit"))
                    path = inst.get("path", "/")
                    reference = inst.get("reference", symbol_data.get("reference", "U?"))
                    unit = inst.get("unit", 1)

                logger.debug(
                    f"   Instance: project={project}, path={path}, ref={reference}, unit={unit}"
                )

                instances_sexp.append(
                    [
                        sexpdata.Symbol("project"),
                        project,
                        [
                            sexpdata.Symbol("path"),
                            path,  # PRESERVE user-set hierarchical path!
                            [sexpdata.Symbol("reference"), reference],
                            [sexpdata.Symbol("unit"), unit],
                        ],
                    ]
                )
            sexp.append(instances_sexp)
        else:
            # No user-set instances - generate default (backward compatibility)
            logger.debug(
                f"🔍 HIERARCHICAL FIX: Component {symbol_data.get('reference')} has NO user instances, generating default"
            )

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
        lib_id: str = None,
    ) -> List[Any]:
        """Create a property with proper positioning and effects like KiCAD."""
        from ...core.property_positioning import get_property_position

        # Calculate property position using library-specific positioning
        if lib_id and prop_name in ["Reference", "Value", "Footprint"]:
            prop_x, prop_y, text_rotation = get_property_position(
                lib_id, prop_name, (component_pos.x, component_pos.y), rotation
            )
        else:
            # Fallback for custom properties or when lib_id not available
            from ...core.config import config

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
                prop_x, prop_y = (
                    component_pos.x,
                    component_pos.y + offset,
                )  # GND points down, text below
            else:
                prop_x, prop_y = (
                    component_pos.x,
                    component_pos.y - offset,
                )  # VCC points up, text above
        elif rotation == 90:
            if is_gnd_type:
                prop_x, prop_y = component_pos.x - offset, component_pos.y  # GND left, text left
            else:
                prop_x, prop_y = component_pos.x + offset, component_pos.y  # VCC right, text right
        elif rotation == 180:
            if is_gnd_type:
                prop_x, prop_y = (
                    component_pos.x,
                    component_pos.y - offset,
                )  # GND inverted up, text above
            else:
                prop_x, prop_y = (
                    component_pos.x,
                    component_pos.y + offset,
                )  # VCC inverted down, text below
        elif rotation == 270:
            if is_gnd_type:
                prop_x, prop_y = component_pos.x + offset, component_pos.y  # GND right, text right
            else:
                prop_x, prop_y = component_pos.x - offset, component_pos.y  # VCC left, text left
        else:
            # Fallback for non-standard rotations
            prop_x, prop_y = component_pos.x, (
                component_pos.y - offset if not is_gnd_type else component_pos.y + offset
            )

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
