"""
Text effects parsing and manipulation utilities.

Provides functions to parse, merge, and create KiCAD text effects S-expressions.
Effects control font, size, position, rotation, color, and visibility of text.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from sexpdata import Symbol

logger = logging.getLogger(__name__)


def parse_effects_from_sexp(property_sexp: List[Any]) -> Dict[str, Any]:
    """
    Parse text effects from a property S-expression.

    Extracts all effect properties from a KiCAD property S-expression including
    position, rotation, font properties, justification, and visibility.

    Args:
        property_sexp: Property S-expression list from KiCAD file
                      Format: [Symbol('property'), 'Name', 'Value', (at ...), (effects ...)]

    Returns:
        Dictionary with effect properties:
        {
            'position': (x, y),           # Position relative to component
            'rotation': float,            # Rotation in degrees
            'font_face': str,             # Font family name (or None for default)
            'font_size': (h, w),          # Font size (height, width) in mm
            'font_thickness': float,      # Font line thickness (or None)
            'bold': bool,                 # Bold flag
            'italic': bool,               # Italic flag
            'color': (r, g, b, a),        # RGBA color (or None)
            'justify_h': str,             # Horizontal justification (or None)
            'justify_v': str,             # Vertical justification (or None)
            'visible': bool,              # Visibility (True = visible, False = hidden)
        }

    Example:
        >>> sexp = [Symbol('property'), 'Reference', 'R1',
        ...         [Symbol('at'), 100, 100, 90],
        ...         [Symbol('effects'), [Symbol('font'), [Symbol('size'), 2, 2]]]]
        >>> effects = parse_effects_from_sexp(sexp)
        >>> effects['position']
        (100, 100)
        >>> effects['rotation']
        90
        >>> effects['font_size']
        (2, 2)
    """
    effects = {
        "position": None,
        "rotation": 0,
        "font_face": None,
        "font_size": (1.27, 1.27),  # KiCAD default
        "font_thickness": None,
        "bold": False,
        "italic": False,
        "color": None,
        "justify_h": None,
        "justify_v": None,
        "visible": True,  # Default is visible
    }

    # Parse (at x y rotation) section - position and rotation
    for item in property_sexp:
        if isinstance(item, list) and len(item) > 0:
            if isinstance(item[0], Symbol) and str(item[0]) == "at":
                if len(item) >= 3:
                    effects["position"] = (float(item[1]), float(item[2]))
                if len(item) >= 4:
                    effects["rotation"] = float(item[3])

    # Parse (effects ...) section
    for item in property_sexp:
        if isinstance(item, list) and len(item) > 0:
            if isinstance(item[0], Symbol) and str(item[0]) == "effects":
                _parse_effects_section(item, effects)

    return effects


def _parse_effects_section(effects_sexp: List[Any], effects: Dict[str, Any]) -> None:
    """
    Parse the (effects ...) section of a property.

    Updates the effects dict in-place with values from the S-expression.

    Args:
        effects_sexp: Effects S-expression list [Symbol('effects'), ...]
        effects: Dictionary to update with parsed values
    """
    # Parse (font ...) section
    for item in effects_sexp[1:]:
        if isinstance(item, list) and len(item) > 0:
            tag = str(item[0]) if isinstance(item[0], Symbol) else None

            if tag == "font":
                _parse_font_section(item, effects)
            elif tag == "justify":
                _parse_justify(item, effects)
            elif tag == "hide":
                effects["visible"] = False


def _parse_font_section(font_sexp: List[Any], effects: Dict[str, Any]) -> None:
    """
    Parse the (font ...) section.

    Args:
        font_sexp: Font S-expression list [Symbol('font'), ...]
        effects: Dictionary to update with parsed values
    """
    for item in font_sexp[1:]:
        if isinstance(item, list) and len(item) > 0:
            tag = str(item[0]) if isinstance(item[0], Symbol) else None

            if tag == "size" and len(item) >= 3:
                effects["font_size"] = (float(item[1]), float(item[2]))
            elif tag == "face" and len(item) >= 2:
                effects["font_face"] = str(item[1])
            elif tag == "thickness" and len(item) >= 2:
                effects["font_thickness"] = float(item[1])
            elif tag == "color" and len(item) >= 5:
                effects["color"] = (int(item[1]), int(item[2]), int(item[3]), float(item[4]))
            elif tag == "bold":
                effects["bold"] = True
            elif tag == "italic":
                effects["italic"] = True


def _parse_justify(justify_sexp: List[Any], effects: Dict[str, Any]) -> None:
    """
    Parse the (justify ...) section.

    Args:
        justify_sexp: Justify S-expression list [Symbol('justify'), 'left', ...]
        effects: Dictionary to update with parsed values
    """
    for item in justify_sexp[1:]:
        if isinstance(item, Symbol):
            value = str(item)
            if value in ["left", "right", "center"]:
                effects["justify_h"] = value
            elif value in ["top", "bottom"]:
                effects["justify_v"] = value


def merge_effects(existing: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge updated effects with existing effects.

    User-provided updates override existing values. Values not specified in updates
    are preserved from existing. Allows partial updates without losing other settings.

    Args:
        existing: Current effects dictionary
        updates: User-provided updates (only changed values)

    Returns:
        Merged effects dictionary

    Example:
        >>> existing = {'font_size': (1.27, 1.27), 'bold': False}
        >>> updates = {'bold': True}
        >>> merged = merge_effects(existing, updates)
        >>> merged
        {'font_size': (1.27, 1.27), 'bold': True}
    """
    merged = existing.copy()

    for key, value in updates.items():
        if key in merged:
            merged[key] = value
        else:
            logger.warning(f"Unknown effect property '{key}' - ignoring")

    return merged


def create_effects_sexp(effects: Dict[str, Any]) -> List[Any]:
    """
    Create an (effects ...) S-expression from effects dictionary.

    Generates KiCAD-format S-expression with proper field ordering:
    (effects
        (font ...)
        (justify ...)
        (hide yes)  # if not visible
    )

    Args:
        effects: Effects dictionary with properties

    Returns:
        S-expression list for effects section

    Example:
        >>> effects = {'font_size': (2, 2), 'bold': True, 'visible': True}
        >>> sexp = create_effects_sexp(effects)
        >>> # Returns: [Symbol('effects'), [Symbol('font'), [Symbol('size'), 2, 2], Symbol('bold')]]
    """
    effects_list = [Symbol("effects")]

    # Create font section
    font_list = [Symbol("font")]

    # Font face (if specified)
    if effects.get("font_face"):
        font_list.append([Symbol("face"), effects["font_face"]])

    # Font size (always include)
    if effects.get("font_size"):
        h, w = effects["font_size"]
        font_list.append([Symbol("size"), h, w])

    # Font thickness (if specified)
    if effects.get("font_thickness") is not None:
        font_list.append([Symbol("thickness"), effects["font_thickness"]])

    # Bold flag
    if effects.get("bold"):
        font_list.append([Symbol("bold"), Symbol("yes")])

    # Italic flag
    if effects.get("italic"):
        font_list.append([Symbol("italic"), Symbol("yes")])

    # Color (if specified)
    if effects.get("color"):
        r, g, b, a = effects["color"]
        font_list.append([Symbol("color"), r, g, b, a])

    effects_list.append(font_list)

    # Justification (if specified)
    justify_h = effects.get("justify_h")
    justify_v = effects.get("justify_v")
    if justify_h or justify_v:
        justify_list = [Symbol("justify")]
        if justify_h:
            justify_list.append(Symbol(justify_h))
        if justify_v:
            justify_list.append(Symbol(justify_v))
        effects_list.append(justify_list)

    # Hide flag (if not visible)
    if not effects.get("visible", True):
        effects_list.append([Symbol("hide"), Symbol("yes")])

    return effects_list


def update_property_sexp_with_effects(
    property_sexp: List[Any], effects: Dict[str, Any]
) -> List[Any]:
    """
    Update a property S-expression with new effects.

    Replaces the (effects ...) section and updates the (at x y rotation) section
    in a property S-expression while preserving other fields like property name and value.

    Args:
        property_sexp: Original property S-expression
        effects: New effects dictionary

    Returns:
        Updated property S-expression

    Example:
        >>> sexp = [Symbol('property'), 'Reference', 'R1',
        ...         [Symbol('at'), 100, 100, 0],
        ...         [Symbol('effects'), ...]]  # Old effects
        >>> effects = {'bold': True, 'font_size': (2, 2), 'visible': True}
        >>> new_sexp = update_property_sexp_with_effects(sexp, effects)
        >>> # Returns property with updated effects section
    """
    # Start with property tag, name, and value
    new_sexp = []
    effects_found = False

    for item in property_sexp:
        if isinstance(item, list) and len(item) > 0:
            if isinstance(item[0], Symbol) and str(item[0]) == "effects":
                # Replace old effects with new
                new_sexp.append(create_effects_sexp(effects))
                effects_found = True
            elif isinstance(item[0], Symbol) and str(item[0]) == "at":
                # Update (at x y rotation) section if position or rotation changed
                at_section = list(item)  # Copy

                # Update position if specified
                if effects.get("position"):
                    x, y = effects["position"]
                    if len(at_section) >= 3:
                        at_section[1] = x
                        at_section[2] = y

                # Update rotation if specified
                if effects.get("rotation") is not None:
                    rotation = effects["rotation"]
                    if len(at_section) >= 4:
                        at_section[3] = rotation
                    else:
                        # Add rotation if not present
                        at_section.append(rotation)

                new_sexp.append(at_section)
            else:
                # Keep other sections (show_name, etc.)
                new_sexp.append(item)
        else:
            # Keep property tag, name, value
            new_sexp.append(item)

    # If no effects section existed, add one
    if not effects_found:
        new_sexp.append(create_effects_sexp(effects))

    return new_sexp
