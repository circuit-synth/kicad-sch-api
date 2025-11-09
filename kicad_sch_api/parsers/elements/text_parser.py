"""
Text and text box elements parser for KiCAD schematics.

Handles parsing and serialization of Text and text box elements.
"""

import logging
from typing import Any, Dict, List, Optional

import sexpdata

from ...core.config import config
from ..base import BaseElementParser

logger = logging.getLogger(__name__)


class TextParser(BaseElementParser):
    """Parser for Text and text box elements."""

    def __init__(self):
        """Initialize text parser."""
        super().__init__("text")

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
            "size": config.defaults.font_size,
            "uuid": None,
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
                            if isinstance(font_elem, list):
                                font_prop = str(font_elem[0])
                                if font_prop == "size" and len(font_elem) >= 2:
                                    text_data["size"] = float(font_elem[1])
                                elif font_prop == "thickness" and len(font_elem) >= 2:
                                    text_data["thickness"] = float(font_elem[1])
                                elif font_prop == "bold" and len(font_elem) >= 2:
                                    text_data["bold"] = str(font_elem[1]) == "yes"
                                elif font_prop == "italic" and len(font_elem) >= 2:
                                    text_data["italic"] = str(font_elem[1]) == "yes"
                                elif font_prop == "color" and len(font_elem) >= 5:
                                    text_data["color"] = (
                                        int(font_elem[1]),
                                        int(font_elem[2]),
                                        int(font_elem[3]),
                                        float(font_elem[4]),
                                    )
                                elif font_prop == "face" and len(font_elem) >= 2:
                                    text_data["face"] = str(font_elem[1])
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
            "font_size": config.defaults.font_size,
            "justify_horizontal": "left",
            "justify_vertical": "top",
            "uuid": None,
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
                    text_box_data["margins"] = (
                        float(elem[1]),
                        float(elem[2]),
                        float(elem[3]),
                        float(elem[4]),
                    )
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
                        text_box_data["fill_type"] = (
                            str(fill_elem[1]) if len(fill_elem) >= 2 else "none"
                        )
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
        size = text_data.get("size", config.defaults.font_size)
        effects = [sexpdata.Symbol("effects")]
        font = [sexpdata.Symbol("font"), [sexpdata.Symbol("size"), size, size]]

        # Add optional font properties
        if text_data.get("thickness") is not None:
            font.append([sexpdata.Symbol("thickness"), text_data["thickness"]])
        if text_data.get("bold", False):
            font.append([sexpdata.Symbol("bold"), sexpdata.Symbol("yes")])
        if text_data.get("italic", False):
            font.append([sexpdata.Symbol("italic"), sexpdata.Symbol("yes")])
        if text_data.get("color") is not None:
            r, g, b, a = text_data["color"]
            font.append([sexpdata.Symbol("color"), r, g, b, a])
        if text_data.get("face") is not None:
            font.append([sexpdata.Symbol("face"), text_data["face"]])

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
        font_size = text_box_data.get("font_size", config.defaults.font_size)
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
