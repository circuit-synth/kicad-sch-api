"""
Exact formatting preservation for KiCAD schematic files.

This module provides precise S-expression formatting that matches KiCAD's native output exactly,
ensuring round-trip compatibility and professional output quality.
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Union

import sexpdata

logger = logging.getLogger(__name__)


@dataclass
class FormatRule:
    """Formatting rule for S-expression elements."""
    inline: bool = False
    max_inline_elements: Optional[int] = None
    quote_indices: Set[int] = None
    custom_handler: Optional[Callable] = None
    indent_level: int = 1

    def __post_init__(self):
        if self.quote_indices is None:
            self.quote_indices = set()


class ExactFormatter:
    """
    S-expression formatter that produces output identical to KiCAD's native formatting.
    
    This formatter ensures exact format preservation for professional schematic manipulation,
    matching KiCAD's indentation, spacing, and quoting conventions precisely.
    """

    def __init__(self):
        """Initialize the formatter with KiCAD-specific rules."""
        self.rules = {}
        self._initialize_kicad_rules()
        logger.debug("Exact formatter initialized with KiCAD rules")

    def _initialize_kicad_rules(self):
        """Initialize formatting rules that match KiCAD's output exactly."""
        
        # Metadata elements - single line
        self.rules["kicad_sch"] = FormatRule(inline=False, indent_level=0)
        self.rules["version"] = FormatRule(inline=True)
        self.rules["generator"] = FormatRule(inline=True, quote_indices={1})
        self.rules["uuid"] = FormatRule(inline=True, quote_indices={1})
        
        # Title block
        self.rules["title_block"] = FormatRule(inline=False)
        self.rules["title"] = FormatRule(inline=True, quote_indices={1})
        self.rules["company"] = FormatRule(inline=True, quote_indices={1})
        self.rules["revision"] = FormatRule(inline=True, quote_indices={1})
        self.rules["date"] = FormatRule(inline=True, quote_indices={1})
        self.rules["size"] = FormatRule(inline=True, quote_indices={1})
        self.rules["comment"] = FormatRule(inline=True, quote_indices={2})
        
        # Library symbols
        self.rules["lib_symbols"] = FormatRule(inline=False)
        self.rules["symbol"] = FormatRule(inline=False, quote_indices={1})
        
        # Component elements
        self.rules["lib_id"] = FormatRule(inline=True, quote_indices={1})
        self.rules["at"] = FormatRule(inline=True)
        self.rules["unit"] = FormatRule(inline=True)
        self.rules["exclude_from_sim"] = FormatRule(inline=True)
        self.rules["in_bom"] = FormatRule(inline=True)
        self.rules["on_board"] = FormatRule(inline=True)
        self.rules["dnp"] = FormatRule(inline=True)
        self.rules["fields_autoplaced"] = FormatRule(inline=True)
        
        # Properties - KiCAD specific format
        self.rules["property"] = FormatRule(
            inline=False,
            quote_indices={1, 2},
            custom_handler=self._format_property
        )
        
        # Pins and connections
        self.rules["pin"] = FormatRule(inline=False, quote_indices={1, 2})
        self.rules["instances"] = FormatRule(inline=False)
        self.rules["project"] = FormatRule(inline=True, quote_indices={1})
        self.rules["path"] = FormatRule(inline=True, quote_indices={1})
        self.rules["reference"] = FormatRule(inline=True, quote_indices={1})
        
        # Wire elements
        self.rules["wire"] = FormatRule(inline=False)
        self.rules["pts"] = FormatRule(inline=False)
        self.rules["xy"] = FormatRule(inline=True)
        self.rules["stroke"] = FormatRule(inline=False)
        self.rules["width"] = FormatRule(inline=True)
        self.rules["type"] = FormatRule(inline=True)
        
        # Junction
        self.rules["junction"] = FormatRule(inline=False)
        self.rules["diameter"] = FormatRule(inline=True)
        
        # Labels
        self.rules["label"] = FormatRule(inline=False, quote_indices={1})
        self.rules["global_label"] = FormatRule(inline=False, quote_indices={1})
        self.rules["hierarchical_label"] = FormatRule(inline=False, quote_indices={1})
        
        # Effects and text formatting
        self.rules["effects"] = FormatRule(inline=False)
        self.rules["font"] = FormatRule(inline=False)
        self.rules["size"] = FormatRule(inline=True)
        self.rules["thickness"] = FormatRule(inline=True)
        self.rules["justify"] = FormatRule(inline=True)
        self.rules["hide"] = FormatRule(inline=True)

    def format(self, data: Any) -> str:
        """
        Format S-expression data with exact KiCAD formatting.
        
        Args:
            data: S-expression data structure
            
        Returns:
            Formatted string matching KiCAD's output exactly
        """
        return self._format_element(data, 0)

    def format_preserving_write(self, new_data: Any, original_content: str) -> str:
        """
        Write new data while preserving as much original formatting as possible.
        
        This method attempts to maintain the original file's formatting style
        while incorporating changes from the new data structure.
        
        Args:
            new_data: New S-expression data to write
            original_content: Original file content for format reference
            
        Returns:
            Formatted string with preserved styling where possible
        """
        # For now, use standard formatting - future enhancement could
        # analyze original formatting patterns and apply them
        return self.format(new_data)

    def _format_element(self, element: Any, indent_level: int) -> str:
        """Format a single S-expression element."""
        if isinstance(element, list):
            return self._format_list(element, indent_level)
        elif isinstance(element, sexpdata.Symbol):
            return str(element)
        elif isinstance(element, str):
            # Quote strings that need quoting
            if self._needs_quoting(element):
                return f'"{element}"'
            return element
        else:
            return str(element)

    def _format_list(self, lst: List[Any], indent_level: int) -> str:
        """Format a list (S-expression)."""
        if not lst:
            return "()"
            
        # Get the tag (first element)
        tag = str(lst[0]) if isinstance(lst[0], sexpdata.Symbol) else None
        rule = self.rules.get(tag, FormatRule())
        
        # Use custom handler if available
        if rule.custom_handler:
            return rule.custom_handler(lst, indent_level)
        
        # Format based on rule
        if rule.inline or self._should_format_inline(lst, rule):
            return self._format_inline(lst, rule)
        else:
            return self._format_multiline(lst, indent_level, rule)

    def _format_inline(self, lst: List[Any], rule: FormatRule) -> str:
        """Format list on a single line."""
        elements = []
        for i, element in enumerate(lst):
            if i in rule.quote_indices and isinstance(element, str):
                elements.append(f'"{element}"')
            else:
                elements.append(self._format_element(element, 0))
        return f"({' '.join(elements)})"

    def _format_multiline(self, lst: List[Any], indent_level: int, rule: FormatRule) -> str:
        """Format list across multiple lines with proper indentation."""
        if not lst:
            return "()"
            
        result = []
        indent = "\t" * indent_level
        
        # First element (tag) on opening line
        tag = str(lst[0])
        
        if len(lst) == 1:
            return f"({tag})"
        
        # Handle different multiline formats based on tag
        if tag == "property":
            return self._format_property(lst, indent_level)
        elif tag in ("symbol", "wire", "junction", "label"):
            return self._format_component_like(lst, indent_level, rule)
        else:
            return self._format_generic_multiline(lst, indent_level, rule)

    def _format_property(self, lst: List[Any], indent_level: int) -> str:
        """Format property elements in KiCAD style."""
        if len(lst) < 3:
            return self._format_inline(lst, FormatRule(quote_indices={1, 2}))
            
        indent = "\t" * indent_level
        next_indent = "\t" * (indent_level + 1)
        
        # Property format: (property "Name" "Value" (at x y rotation) (effects ...))
        result = f"({lst[0]} \"{lst[1]}\" \"{lst[2]}\""
        
        # Add position and effects on separate lines
        for element in lst[3:]:
            if isinstance(element, list):
                result += f"\n{next_indent}{self._format_element(element, indent_level + 1)}"
            else:
                result += f" {element}"
                
        result += ")"
        return result

    def _format_component_like(self, lst: List[Any], indent_level: int, rule: FormatRule) -> str:
        """Format component-like elements (symbol, wire, etc.)."""
        indent = "\t" * indent_level
        next_indent = "\t" * (indent_level + 1)
        
        tag = str(lst[0])
        result = f"({tag}"
        
        # Add quoted elements if specified
        for i in range(1, len(lst)):
            element = lst[i]
            if isinstance(element, list):
                result += f"\n{next_indent}{self._format_element(element, indent_level + 1)}"
            else:
                if i in rule.quote_indices and isinstance(element, str):
                    result += f" \"{element}\""
                else:
                    result += f" {self._format_element(element, 0)}"
        
        result += ")"
        return result

    def _format_generic_multiline(self, lst: List[Any], indent_level: int, rule: FormatRule) -> str:
        """Generic multiline formatting."""
        indent = "\t" * indent_level
        next_indent = "\t" * (indent_level + 1)
        
        result = f"({lst[0]}"
        
        for i, element in enumerate(lst[1:], 1):
            if isinstance(element, list):
                result += f"\n{next_indent}{self._format_element(element, indent_level + 1)}"
            else:
                if i in rule.quote_indices and isinstance(element, str):
                    result += f" \"{element}\""
                else:
                    result += f" {self._format_element(element, 0)}"
        
        result += ")"
        return result

    def _should_format_inline(self, lst: List[Any], rule: FormatRule) -> bool:
        """Determine if list should be formatted inline."""
        if rule.max_inline_elements is not None:
            if len(lst) > rule.max_inline_elements:
                return False
                
        # Check if any element is a list (nested structure)
        for element in lst[1:]:  # Skip tag
            if isinstance(element, list):
                return False
                
        return True

    def _needs_quoting(self, text: str) -> bool:
        """Check if string needs to be quoted."""
        # Quote if contains spaces, special characters, or is empty
        if not text or ' ' in text or '"' in text:
            return True
            
        # Quote if contains S-expression special characters
        special_chars = '()[]{}#'
        return any(c in text for c in special_chars)


class CompactFormatter(ExactFormatter):
    """Compact formatter for minimal output size."""
    
    def _format_multiline(self, lst: List[Any], indent_level: int, rule: FormatRule) -> str:
        """Override to use minimal spacing."""
        # Use single spaces instead of tabs for compact output
        return super()._format_multiline(lst, indent_level, rule).replace('\t', ' ')


class DebugFormatter(ExactFormatter):
    """Debug formatter with extra spacing and comments."""
    
    def format(self, data: Any) -> str:
        """Format with debug information."""
        result = super().format(data)
        return f"; Generated by kicad-sch-api ExactFormatter\n{result}"