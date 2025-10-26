"""
Net management for KiCAD schematics.

This module provides collection classes for managing electrical nets,
featuring fast lookup, bulk operations, and validation.
"""

import logging
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
from .collections import BaseCollection
from .types import Net

logger = logging.getLogger(__name__)


class NetElement:
    """
    Enhanced wrapper for schematic net elements with modern API.

    Provides intuitive access to net properties and operations
    while maintaining exact format preservation.
    """

    def __init__(self, net_data: Net, parent_collection: "NetCollection"):
        """
        Initialize net element wrapper.

        Args:
            net_data: Underlying net data
            parent_collection: Parent collection for updates
        """
        self._data = net_data
        self._collection = parent_collection
        self._validator = SchematicValidator()

    # Core properties with validation
    @property
    def uuid(self) -> str:
        """Net UUID (uses name as unique identifier)."""
        return self._data.name

    @property
    def name(self) -> str:
        """Net name."""
        return self._data.name

    @name.setter
    def name(self, value: str):
        """Set net name with validation."""
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Net name cannot be empty")
        old_name = self._data.name
        self._data.name = value.strip()
        # Update name index and rebuild base UUID index since UUID changed
        self._collection._update_name_index(old_name, self)
        self._collection._rebuild_index()
        self._collection._mark_modified()

    @property
    def components(self) -> List[Tuple[str, str]]:
        """List of component connections (reference, pin) tuples."""
        return self._data.components.copy()

    @property
    def wires(self) -> List[str]:
        """List of wire UUIDs in this net."""
        return self._data.wires.copy()

    @property
    def labels(self) -> List[str]:
        """List of label UUIDs in this net."""
        return self._data.labels.copy()

    def add_connection(self, reference: str, pin: str):
        """Add component pin to net."""
        self._data.add_connection(reference, pin)
        self._collection._mark_modified()

    def remove_connection(self, reference: str, pin: str):
        """Remove component pin from net."""
        self._data.remove_connection(reference, pin)
        self._collection._mark_modified()

    def add_wire(self, wire_uuid: str):
        """Add wire to net."""
        if wire_uuid not in self._data.wires:
            self._data.wires.append(wire_uuid)
            self._collection._mark_modified()

    def remove_wire(self, wire_uuid: str):
        """Remove wire from net."""
        if wire_uuid in self._data.wires:
            self._data.wires.remove(wire_uuid)
            self._collection._mark_modified()

    def add_label(self, label_uuid: str):
        """Add label to net."""
        if label_uuid not in self._data.labels:
            self._data.labels.append(label_uuid)
            self._collection._mark_modified()

    def remove_label(self, label_uuid: str):
        """Remove label from net."""
        if label_uuid in self._data.labels:
            self._data.labels.remove(label_uuid)
            self._collection._mark_modified()

    def validate(self) -> List[ValidationIssue]:
        """Validate this net element."""
        return self._validator.validate_net(self._data.__dict__)

    def to_dict(self) -> Dict[str, Any]:
        """Convert net element to dictionary representation."""
        return {
            "name": self.name,
            "components": self.components,
            "wires": self.wires,
            "labels": self.labels,
        }

    def __str__(self) -> str:
        """String representation."""
        return f"<Net '{self.name}' ({len(self.components)} connections)>"


class NetCollection(BaseCollection[NetElement]):
    """
    Collection class for efficient net management.

    Inherits from BaseCollection for standard operations and adds net-specific
    functionality including name-based indexing.

    Provides fast lookup, filtering, and bulk operations for schematic nets.
    Note: Nets use name as the unique identifier (exposed as .uuid for protocol compatibility).
    """

    def __init__(self, nets: List[Net] = None):
        """
        Initialize net collection.

        Args:
            nets: Initial list of net data
        """
        # Initialize base collection
        super().__init__([], collection_name="nets")

        # Additional net-specific index (for convenience, duplicates base UUID index)
        self._name_index: Dict[str, NetElement] = {}

        # Add initial nets
        if nets:
            for net_data in nets:
                self._add_to_indexes(NetElement(net_data, self))

    def add(
        self,
        name: str,
        components: List[Tuple[str, str]] = None,
        wires: List[str] = None,
        labels: List[str] = None,
    ) -> NetElement:
        """
        Add a new net to the schematic.

        Args:
            name: Net name
            components: Initial component connections
            wires: Initial wire UUIDs
            labels: Initial label UUIDs

        Returns:
            Newly created NetElement

        Raises:
            ValidationError: If net data is invalid
        """
        # Validate inputs
        if not isinstance(name, str) or not name.strip():
            raise ValidationError("Net name cannot be empty")

        name = name.strip()

        # Check for duplicate name
        if name in self._name_index:
            raise ValidationError(f"Net name {name} already exists")

        # Create net data
        net_data = Net(
            name=name,
            components=components or [],
            wires=wires or [],
            labels=labels or [],
        )

        # Create wrapper and add to collection
        net_element = NetElement(net_data, self)
        self._add_to_indexes(net_element)
        self._mark_modified()

        logger.debug(f"Added net: {net_element}")
        return net_element

    def get_by_name(self, name: str) -> Optional[NetElement]:
        """Get net by name (convenience method, equivalent to get(name))."""
        return self.get(name)

    # get() method inherited from BaseCollection (uses name as UUID)

    def remove(self, name: str) -> bool:
        """
        Remove net by name.

        Args:
            name: Name of net to remove

        Returns:
            True if net was removed, False if not found
        """
        net_element = self.get(name)
        if not net_element:
            return False

        # Remove from name index
        if net_element.name in self._name_index:
            del self._name_index[net_element.name]

        # Remove using base class method
        super().remove(name)

        logger.debug(f"Removed net: {net_element}")
        return True

    def find_by_component(self, reference: str, pin: Optional[str] = None) -> List[NetElement]:
        """
        Find nets connected to a component.

        Args:
            reference: Component reference
            pin: Specific pin (if None, returns all nets for component)

        Returns:
            List of matching net elements
        """
        matches = []
        for net_element in self._items:
            for comp_ref, comp_pin in net_element.components:
                if comp_ref == reference and (pin is None or comp_pin == pin):
                    matches.append(net_element)
                    break
        return matches

    def filter(self, predicate: Callable[[NetElement], bool]) -> List[NetElement]:
        """
        Filter nets by predicate function (delegates to base class find).

        Args:
            predicate: Function that returns True for nets to include

        Returns:
            List of nets matching predicate
        """
        return self.find(predicate)

    def bulk_update(self, criteria: Callable[[NetElement], bool], updates: Dict[str, Any]):
        """
        Update multiple nets matching criteria.

        Args:
            criteria: Function to select nets to update
            updates: Dictionary of property updates
        """
        updated_count = 0
        for net_element in self._items:
            if criteria(net_element):
                for prop, value in updates.items():
                    if hasattr(net_element, prop):
                        setattr(net_element, prop, value)
                        updated_count += 1

        if updated_count > 0:
            self._mark_modified()
            logger.debug(f"Bulk updated {updated_count} net properties")

    def clear(self):
        """Remove all nets from collection."""
        self._name_index.clear()
        super().clear()

    def _add_to_indexes(self, net_element: NetElement):
        """Add net to internal indexes (base + name index)."""
        self._add_item(net_element)
        self._name_index[net_element.name] = net_element

    def _update_name_index(self, old_name: str, net_element: NetElement):
        """Update name index when net name changes."""
        if old_name in self._name_index:
            del self._name_index[old_name]
        self._name_index[net_element.name] = net_element

    # Collection interface methods - __len__, __iter__, __getitem__ inherited from BaseCollection
    def __bool__(self) -> bool:
        """Return True if collection has nets."""
        return len(self._items) > 0
