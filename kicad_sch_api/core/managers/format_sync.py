"""
Format Synchronization Manager for KiCAD schematic data consistency.

Handles bidirectional synchronization between Python object models and
raw S-expression data structures while maintaining exact format preservation
and tracking changes for efficient updates.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Union

from ..components import Component
from ..types import Point, Wire
from .base import BaseManager

logger = logging.getLogger(__name__)


class FormatSyncManager(BaseManager):
    """
    Manages synchronization between object models and S-expression data.

    Responsible for:
    - Bidirectional data synchronization
    - Change tracking and dirty flag management
    - Format preservation during updates
    - Incremental update optimization
    - Data consistency validation
    """

    def __init__(self, schematic_data: Dict[str, Any]):
        """
        Initialize FormatSyncManager.

        Args:
            schematic_data: Reference to schematic data
        """
        super().__init__(schematic_data)
        self._dirty_flags: Set[str] = set()
        self._change_log: List[Dict[str, Any]] = []
        self._sync_lock = False

    def mark_dirty(
        self, section: str, operation: str = "update", context: Optional[Dict] = None
    ) -> None:
        """
        Mark a data section as dirty for synchronization.

        Args:
            section: Data section that changed (e.g., 'components', 'wires')
            operation: Type of operation (update, add, remove)
            context: Additional context about the change
        """
        if self._sync_lock:
            logger.debug(f"Sync locked, deferring dirty mark for {section}")
            return

        self._dirty_flags.add(section)

        change_entry = {
            "section": section,
            "operation": operation,
            "timestamp": None,  # Would use datetime in real implementation
            "context": context or {},
        }
        self._change_log.append(change_entry)

        logger.debug(f"Marked section '{section}' as dirty ({operation})")

    def sync_component_to_data(self, component: Component) -> None:
        """
        Synchronize a component object back to S-expression data.

        Args:
            component: Component to sync
        """
        symbols = self._data.get("symbol", [])

        # Find the corresponding symbol entry
        for symbol_data in symbols:
            if symbol_data.get("uuid") == component.uuid:
                self._update_symbol_data_from_component(symbol_data, component)
                self.mark_dirty("symbol", "update", {"uuid": component.uuid})
                return

        logger.warning(f"Component not found in data for sync: {component.uuid}")

    def sync_component_from_data(self, component: Component, symbol_data: Dict[str, Any]) -> None:
        """
        Update component object from S-expression data.

        Args:
            component: Component to update
            symbol_data: Source symbol data
        """
        # Update component properties from symbol data
        if "at" in symbol_data:
            at_data = symbol_data["at"]
            component.position = Point(at_data[0], at_data[1])
            if len(at_data) > 2:
                component.rotation = at_data[2]

        # Update properties
        if "property" in symbol_data:
            for prop in symbol_data["property"]:
                name = prop.get("name")
                value = prop.get("value")
                if name and value is not None:
                    component.set_property(name, value)

        logger.debug(f"Synced component from data: {component.uuid}")

    def sync_wire_to_data(self, wire: Wire) -> None:
        """
        Synchronize a wire object back to S-expression data.

        Args:
            wire: Wire to sync
        """
        wires = self._data.get("wire", [])

        # Find the corresponding wire entry
        for wire_data in wires:
            if wire_data.get("uuid") == wire.uuid:
                self._update_wire_data_from_object(wire_data, wire)
                self.mark_dirty("wire", "update", {"uuid": wire.uuid})
                return

        logger.warning(f"Wire not found in data for sync: {wire.uuid}")

    def sync_wire_from_data(self, wire: Wire, wire_data: Dict[str, Any]) -> None:
        """
        Update wire object from S-expression data.

        Args:
            wire: Wire to update
            wire_data: Source wire data
        """
        # Update wire endpoints
        if "pts" in wire_data:
            pts = wire_data["pts"]
            if len(pts) >= 2:
                start_pt = pts[0]
                end_pt = pts[-1]
                wire.start = Point(start_pt["xy"][0], start_pt["xy"][1])
                wire.end = Point(end_pt["xy"][0], end_pt["xy"][1])

        # Update stroke properties
        if "stroke" in wire_data:
            wire.stroke_width = wire_data["stroke"].get("width", 0.0)

        logger.debug(f"Synced wire from data: {wire.uuid}")

    def sync_all_to_data(self, component_collection=None, wire_collection=None) -> None:
        """
        Perform full synchronization of all objects to S-expression data.

        Args:
            component_collection: Collection of components to sync
            wire_collection: Collection of wires to sync
        """
        self._sync_lock = True

        try:
            # Sync components
            if component_collection:
                for component in component_collection:
                    self.sync_component_to_data(component)

            # Sync wires
            if wire_collection:
                for wire in wire_collection:
                    self.sync_wire_to_data(wire)

            # Clear dirty flags after successful sync
            self._dirty_flags.clear()
            logger.info("Full synchronization to data completed")

        finally:
            self._sync_lock = False

    def sync_all_from_data(self, component_collection=None, wire_collection=None) -> None:
        """
        Perform full synchronization from S-expression data to objects.

        Args:
            component_collection: Collection of components to update
            wire_collection: Collection of wires to update
        """
        self._sync_lock = True

        try:
            # Sync components from symbols
            if component_collection:
                symbols = self._data.get("symbol", [])
                for symbol_data in symbols:
                    uuid = symbol_data.get("uuid")
                    if uuid:
                        component = component_collection.get_by_uuid(uuid)
                        if component:
                            self.sync_component_from_data(component, symbol_data)

            # Sync wires
            if wire_collection:
                wires = self._data.get("wire", [])
                for wire_data in wires:
                    uuid = wire_data.get("uuid")
                    if uuid:
                        wire = wire_collection.get_by_uuid(uuid)
                        if wire:
                            self.sync_wire_from_data(wire, wire_data)

            logger.info("Full synchronization from data completed")

        finally:
            self._sync_lock = False

    def perform_incremental_sync(self, component_collection=None, wire_collection=None) -> None:
        """
        Perform incremental synchronization of only dirty sections.

        Args:
            component_collection: Collection of components
            wire_collection: Collection of wires
        """
        if not self._dirty_flags:
            logger.debug("No dirty sections, skipping sync")
            return

        self._sync_lock = True

        try:
            # Sync dirty components
            if "symbol" in self._dirty_flags and component_collection:
                for component in component_collection:
                    self.sync_component_to_data(component)

            # Sync dirty wires
            if "wire" in self._dirty_flags and wire_collection:
                for wire in wire_collection:
                    self.sync_wire_to_data(wire)

            # Clear processed dirty flags
            self._dirty_flags.clear()
            logger.info("Incremental synchronization completed")

        finally:
            self._sync_lock = False

    def add_component_to_data(self, component: Component) -> None:
        """
        Add a new component to S-expression data.

        Args:
            component: Component to add
        """
        symbol_data = self._create_symbol_data_from_component(component)

        if "symbol" not in self._data:
            self._data["symbol"] = []

        self._data["symbol"].append(symbol_data)
        self.mark_dirty("symbol", "add", {"uuid": component.uuid})

        logger.debug(f"Added component to data: {component.reference}")

    def remove_component_from_data(self, component_uuid: str) -> bool:
        """
        Remove a component from S-expression data.

        Args:
            component_uuid: UUID of component to remove

        Returns:
            True if removed, False if not found
        """
        symbols = self._data.get("symbol", [])

        for i, symbol_data in enumerate(symbols):
            if symbol_data.get("uuid") == component_uuid:
                del symbols[i]
                self.mark_dirty("symbol", "remove", {"uuid": component_uuid})
                logger.debug(f"Removed component from data: {component_uuid}")
                return True

        logger.warning(f"Component not found for removal: {component_uuid}")
        return False

    def add_wire_to_data(self, wire: Wire) -> None:
        """
        Add a new wire to S-expression data.

        Args:
            wire: Wire to add
        """
        wire_data = self._create_wire_data_from_object(wire)

        if "wire" not in self._data:
            self._data["wire"] = []

        self._data["wire"].append(wire_data)
        self.mark_dirty("wire", "add", {"uuid": wire.uuid})

        logger.debug(f"Added wire to data: {wire.uuid}")

    def remove_wire_from_data(self, wire_uuid: str) -> bool:
        """
        Remove a wire from S-expression data.

        Args:
            wire_uuid: UUID of wire to remove

        Returns:
            True if removed, False if not found
        """
        wires = self._data.get("wire", [])

        for i, wire_data in enumerate(wires):
            if wire_data.get("uuid") == wire_uuid:
                del wires[i]
                self.mark_dirty("wire", "remove", {"uuid": wire_uuid})
                logger.debug(f"Removed wire from data: {wire_uuid}")
                return True

        logger.warning(f"Wire not found for removal: {wire_uuid}")
        return False

    def is_dirty(self, section: Optional[str] = None) -> bool:
        """
        Check if data sections are dirty.

        Args:
            section: Specific section to check, or None for any

        Returns:
            True if section(s) are dirty
        """
        if section:
            return section in self._dirty_flags
        return bool(self._dirty_flags)

    def get_dirty_sections(self) -> Set[str]:
        """
        Get all dirty data sections.

        Returns:
            Set of dirty section names
        """
        return self._dirty_flags.copy()

    def clear_dirty_flags(self) -> None:
        """Clear all dirty flags."""
        self._dirty_flags.clear()
        logger.debug("Cleared all dirty flags")

    def get_change_log(self) -> List[Dict[str, Any]]:
        """
        Get the change log.

        Returns:
            List of change entries
        """
        return self._change_log.copy()

    def clear_change_log(self) -> None:
        """Clear the change log."""
        self._change_log.clear()
        logger.debug("Cleared change log")

    def _update_symbol_data_from_component(
        self, symbol_data: Dict[str, Any], component: Component
    ) -> None:
        """Update symbol S-expression data from component object."""
        # Update position and rotation
        symbol_data["at"] = [component.position.x, component.position.y, component.rotation]

        # Update lib_id
        symbol_data["lib_id"] = component.lib_id

        # Update properties
        if "property" not in symbol_data:
            symbol_data["property"] = []

        properties = symbol_data["property"]

        # Update existing properties and add new ones
        property_names = {prop.get("name") for prop in properties}

        for name, value in component.properties.items():
            # Find existing property or create new one
            existing_prop = None
            for prop in properties:
                if prop.get("name") == name:
                    existing_prop = prop
                    break

            if existing_prop:
                existing_prop["value"] = value
            else:
                new_prop = {
                    "name": name,
                    "value": value,
                    "at": [0, 0, 0],  # Default position
                    "effects": {"font": {"size": [1.27, 1.27]}},
                }
                properties.append(new_prop)

    def _update_wire_data_from_object(self, wire_data: Dict[str, Any], wire: Wire) -> None:
        """Update wire S-expression data from wire object."""
        # Update endpoints
        wire_data["pts"] = [{"xy": [wire.start.x, wire.start.y]}, {"xy": [wire.end.x, wire.end.y]}]

        # Update stroke
        if "stroke" not in wire_data:
            wire_data["stroke"] = {}

        wire_data["stroke"]["width"] = wire.stroke_width

    def _create_symbol_data_from_component(self, component: Component) -> Dict[str, Any]:
        """Create S-expression data structure from component object."""
        symbol_data = {
            "lib_id": component.lib_id,
            "at": [component.position.x, component.position.y, component.rotation],
            "uuid": component.uuid,
            "property": [],
        }

        # Add properties
        for name, value in component.properties.items():
            prop_data = {
                "name": name,
                "value": value,
                "at": [0, 0, 0],  # Default position relative to symbol
                "effects": {"font": {"size": [1.27, 1.27]}},
            }
            symbol_data["property"].append(prop_data)

        return symbol_data

    def _create_wire_data_from_object(self, wire: Wire) -> Dict[str, Any]:
        """Create S-expression data structure from wire object."""
        wire_data = {
            "pts": [{"xy": [wire.start.x, wire.start.y]}, {"xy": [wire.end.x, wire.end.y]}],
            "stroke": {"width": wire.stroke_width, "type": "default"},
            "uuid": wire.uuid,
        }

        return wire_data

    def validate_data_consistency(
        self, component_collection=None, wire_collection=None
    ) -> List[str]:
        """
        Validate consistency between objects and S-expression data.

        Args:
            component_collection: Collection of components to validate
            wire_collection: Collection of wires to validate

        Returns:
            List of consistency issues found
        """
        issues = []

        # Validate components
        if component_collection:
            symbols = self._data.get("symbol", [])
            symbol_uuids = {sym.get("uuid") for sym in symbols if sym.get("uuid")}
            component_uuids = {comp.uuid for comp in component_collection}

            # Check for missing symbols
            missing_symbols = component_uuids - symbol_uuids
            for uuid in missing_symbols:
                issues.append(f"Component {uuid} missing from symbol data")

            # Check for orphaned symbols
            orphaned_symbols = symbol_uuids - component_uuids
            for uuid in orphaned_symbols:
                issues.append(f"Symbol {uuid} has no corresponding component object")

        # Validate wires
        if wire_collection:
            wires = self._data.get("wire", [])
            wire_data_uuids = {w.get("uuid") for w in wires if w.get("uuid")}
            wire_object_uuids = {wire.uuid for wire in wire_collection}

            # Check for missing wire data
            missing_wire_data = wire_object_uuids - wire_data_uuids
            for uuid in missing_wire_data:
                issues.append(f"Wire {uuid} missing from wire data")

            # Check for orphaned wire data
            orphaned_wire_data = wire_data_uuids - wire_object_uuids
            for uuid in orphaned_wire_data:
                issues.append(f"Wire data {uuid} has no corresponding wire object")

        if issues:
            logger.warning(f"Found {len(issues)} data consistency issues")
        else:
            logger.debug("Data consistency validation passed")

        return issues
