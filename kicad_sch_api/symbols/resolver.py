"""
Symbol resolution with inheritance support for KiCAD symbols.

Provides authoritative symbol inheritance and resolution, separating
this concern from caching for better testability and maintainability.
"""

import copy
import logging
from typing import Any, Dict, List, Optional

import sexpdata

from ..library.cache import SymbolDefinition
from .cache import ISymbolCache

logger = logging.getLogger(__name__)


class SymbolResolver:
    """
    Authoritative symbol inheritance and resolution.

    Handles the complex logic of resolving symbol inheritance chains
    while maintaining clean separation from caching concerns.
    """

    def __init__(self, cache: ISymbolCache):
        """
        Initialize symbol resolver.

        Args:
            cache: Symbol cache implementation
        """
        self._cache = cache
        self._inheritance_cache: Dict[str, SymbolDefinition] = {}
        self._resolution_stack: List[str] = []  # Track resolution to detect cycles

    def resolve_symbol(self, lib_id: str) -> Optional[SymbolDefinition]:
        """
        Resolve symbol with full inheritance chain.

        Args:
            lib_id: Library identifier (e.g., "Device:R")

        Returns:
            Fully resolved symbol with inheritance applied, or None if not found
        """
        # Check inheritance cache first
        if lib_id in self._inheritance_cache:
            symbol = self._inheritance_cache[lib_id]
            symbol.access_count += 1
            return symbol

        # Get raw symbol from cache
        symbol = self._cache.get_symbol(lib_id)
        if not symbol:
            return None

        # If symbol has no inheritance, cache and return as-is
        if not symbol.extends:
            resolved_symbol = copy.deepcopy(symbol)
            self._inheritance_cache[lib_id] = resolved_symbol
            return resolved_symbol

        # Resolve inheritance chain
        resolved_symbol = self._resolve_with_inheritance(symbol)
        if resolved_symbol:
            self._inheritance_cache[lib_id] = resolved_symbol

        return resolved_symbol

    def clear_inheritance_cache(self) -> None:
        """Clear the inheritance resolution cache."""
        self._inheritance_cache.clear()
        logger.debug("Cleared inheritance cache")

    def get_inheritance_statistics(self) -> Dict[str, Any]:
        """
        Get inheritance resolution statistics.

        Returns:
            Dictionary with inheritance statistics
        """
        inheritance_chains = 0
        max_chain_length = 0

        for symbol in self._inheritance_cache.values():
            if hasattr(symbol, "_inheritance_depth"):
                inheritance_chains += 1
                max_chain_length = max(max_chain_length, symbol._inheritance_depth)

        return {
            "resolved_symbols": len(self._inheritance_cache),
            "inheritance_chains": inheritance_chains,
            "max_chain_length": max_chain_length,
            "cache_size": len(self._inheritance_cache),
        }

    def _resolve_with_inheritance(self, symbol: SymbolDefinition) -> Optional[SymbolDefinition]:
        """
        Private implementation of inheritance resolution.

        Args:
            symbol: Symbol to resolve

        Returns:
            Resolved symbol or None if resolution failed
        """
        if not symbol.extends:
            return copy.deepcopy(symbol)

        # Check for circular inheritance
        if symbol.lib_id in self._resolution_stack:
            logger.error(
                f"Circular inheritance detected: {' -> '.join(self._resolution_stack + [symbol.lib_id])}"
            )
            return None

        self._resolution_stack.append(symbol.lib_id)

        try:
            # Get parent symbol
            parent_lib_id = self._resolve_parent_lib_id(symbol.extends, symbol.library)
            parent_symbol = self._cache.get_symbol(parent_lib_id)

            if not parent_symbol:
                logger.warning(f"Parent symbol {parent_lib_id} not found for {symbol.lib_id}")
                return None

            # Recursively resolve parent inheritance
            resolved_parent = self._resolve_with_inheritance(parent_symbol)
            if not resolved_parent:
                logger.error(f"Failed to resolve parent {parent_lib_id} for {symbol.lib_id}")
                return None

            # Merge parent into child
            resolved_symbol = self._merge_parent_into_child(symbol, resolved_parent)

            # Track inheritance depth for statistics
            parent_depth = getattr(resolved_parent, "_inheritance_depth", 0)
            resolved_symbol._inheritance_depth = parent_depth + 1

            logger.debug(f"Resolved inheritance: {symbol.lib_id} extends {parent_lib_id}")
            return resolved_symbol

        except Exception as e:
            logger.error(f"Error resolving inheritance for {symbol.lib_id}: {e}")
            return None

        finally:
            self._resolution_stack.pop()

    def _resolve_parent_lib_id(self, parent_name: str, current_library: str) -> str:
        """
        Resolve parent symbol lib_id from extends name.

        Args:
            parent_name: Name from extends directive
            current_library: Current symbol's library

        Returns:
            Full lib_id for parent symbol
        """
        # If parent_name contains library (e.g., "Device:R"), use as-is
        if ":" in parent_name:
            return parent_name

        # Otherwise, assume same library
        return f"{current_library}:{parent_name}"

    def _merge_parent_into_child(
        self, child: SymbolDefinition, parent: SymbolDefinition
    ) -> SymbolDefinition:
        """
        Merge parent symbol into child symbol.

        Args:
            child: Child symbol definition
            parent: Resolved parent symbol definition

        Returns:
            New symbol definition with inheritance applied
        """
        # Start with deep copy of child
        merged = copy.deepcopy(child)

        # Merge raw KiCAD data for exact format preservation
        if child.raw_kicad_data and parent.raw_kicad_data:
            merged.raw_kicad_data = self._merge_kicad_data(
                child.raw_kicad_data, parent.raw_kicad_data, child.name, parent.name
            )

        # Merge other properties
        merged = self._merge_symbol_properties(merged, parent)

        # Clear extends since we've resolved it
        merged.extends = None

        logger.debug(f"Merged {parent.lib_id} into {child.lib_id}")
        return merged

    def _merge_kicad_data(
        self, child_data: List, parent_data: List, child_name: str, parent_name: str
    ) -> List:
        """
        Merge parent KiCAD data into child KiCAD data.

        Args:
            child_data: Child symbol S-expression data
            parent_data: Parent symbol S-expression data
            child_name: Child symbol name for unit renaming
            parent_name: Parent symbol name for unit renaming

        Returns:
            Merged S-expression data
        """
        # Start with child data structure
        merged = copy.deepcopy(child_data)

        # Remove extends directive from child
        merged = [
            item
            for item in merged
            if not (
                isinstance(item, list) and len(item) >= 2 and item[0] == sexpdata.Symbol("extends")
            )
        ]

        # Copy symbol units and graphics from parent
        for item in parent_data[1:]:
            if isinstance(item, list) and len(item) > 0:
                if item[0] == sexpdata.Symbol("symbol"):
                    # Copy symbol unit with name adjustment
                    unit_item = copy.deepcopy(item)
                    if len(unit_item) > 1:
                        old_unit_name = str(unit_item[1]).strip('"')
                        new_unit_name = old_unit_name.replace(parent_name, child_name)
                        unit_item[1] = new_unit_name
                        logger.debug(f"Renamed unit {old_unit_name} -> {new_unit_name}")
                    merged.append(unit_item)

                elif item[0] not in [sexpdata.Symbol("property")]:
                    # Copy other non-property elements (child properties take precedence)
                    merged.append(copy.deepcopy(item))

        return merged

    def _merge_symbol_properties(
        self, child: SymbolDefinition, parent: SymbolDefinition
    ) -> SymbolDefinition:
        """
        Merge symbol properties, with child properties taking precedence.

        Args:
            child: Child symbol (will be modified)
            parent: Parent symbol (source of inherited properties)

        Returns:
            Child symbol with inherited properties
        """
        # Inherit parent properties where child doesn't have them
        if not child.description and parent.description:
            child.description = parent.description

        if not child.keywords and parent.keywords:
            child.keywords = parent.keywords

        if not child.datasheet and parent.datasheet:
            child.datasheet = parent.datasheet

        # Merge pins from parent (child pins take precedence)
        parent_pin_numbers = {pin.number for pin in child.pins}
        for parent_pin in parent.pins:
            if parent_pin.number not in parent_pin_numbers:
                child.pins.append(copy.deepcopy(parent_pin))

        # Merge graphic elements from parent
        child.graphic_elements.extend(copy.deepcopy(parent.graphic_elements))

        # Inherit unit information
        if parent.units > child.units:
            child.units = parent.units

        # Merge unit names
        for unit_num, unit_name in parent.unit_names.items():
            if unit_num not in child.unit_names:
                child.unit_names[unit_num] = unit_name

        return child

    def validate_inheritance_chain(self, lib_id: str) -> List[str]:
        """
        Validate inheritance chain for cycles and missing parents.

        Args:
            lib_id: Symbol to validate

        Returns:
            List of issues found (empty if valid)
        """
        issues = []
        visited = set()
        chain = []

        def check_symbol(current_lib_id: str) -> None:
            if current_lib_id in visited:
                issues.append(
                    f"Circular inheritance detected: {' -> '.join(chain + [current_lib_id])}"
                )
                return

            visited.add(current_lib_id)
            chain.append(current_lib_id)

            symbol = self._cache.get_symbol(current_lib_id)
            if not symbol:
                issues.append(f"Symbol not found: {current_lib_id}")
                return

            if symbol.extends:
                parent_lib_id = self._resolve_parent_lib_id(symbol.extends, symbol.library)
                if not self._cache.has_symbol(parent_lib_id):
                    issues.append(
                        f"Parent symbol not found: {parent_lib_id} (extended by {current_lib_id})"
                    )
                else:
                    check_symbol(parent_lib_id)

            chain.pop()

        check_symbol(lib_id)
        return issues

    def get_inheritance_chain(self, lib_id: str) -> List[str]:
        """
        Get the complete inheritance chain for a symbol.

        Args:
            lib_id: Symbol to get chain for

        Returns:
            List of lib_ids in inheritance order (child to parent)
        """
        chain = []
        current_lib_id = lib_id

        while current_lib_id:
            if current_lib_id in chain:
                # Circular inheritance
                break

            chain.append(current_lib_id)
            symbol = self._cache.get_symbol(current_lib_id)

            if not symbol or not symbol.extends:
                break

            current_lib_id = self._resolve_parent_lib_id(symbol.extends, symbol.library)

        return chain
