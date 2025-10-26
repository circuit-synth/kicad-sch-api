"""
Net management for KiCAD schematics.

This module provides collection classes for managing electrical nets,
featuring fast lookup, bulk operations, and validation.
"""

import logging
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union

from ..utils.validation import SchematicValidator, ValidationError, ValidationIssue
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
        self._collection._update_name_index(old_name, self)
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


class NetCollection:
    """
    Collection class for efficient net management.

    Provides fast lookup, filtering, and bulk operations for schematic nets.
    """

    def __init__(self, nets: List[Net] = None):
        """
        Initialize net collection.

        Args:
            nets: Initial list of net data
        """
        self._nets: List[NetElement] = []
        self._name_index: Dict[str, NetElement] = {}
        self._modified = False

        # Add initial nets
        if nets:
            for net_data in nets:
                self._add_to_indexes(NetElement(net_data, self))

        logger.debug(f"NetCollection initialized with {len(self._nets)} nets")

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

    def get(self, name: str) -> Optional[NetElement]:
        """Get net by name."""
        return self._name_index.get(name)

    def remove(self, name: str) -> bool:
        """
        Remove net by name.

        Args:
            name: Name of net to remove

        Returns:
            True if net was removed, False if not found
        """
        net_element = self._name_index.get(name)
        if not net_element:
            return False

        # Remove from indexes
        self._remove_from_indexes(net_element)
        self._mark_modified()

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
        for net_element in self._nets:
            for comp_ref, comp_pin in net_element.components:
                if comp_ref == reference and (pin is None or comp_pin == pin):
                    matches.append(net_element)
                    break
        return matches

    def filter(self, predicate: Callable[[NetElement], bool]) -> List[NetElement]:
        """
        Filter nets by predicate function.

        Args:
            predicate: Function that returns True for nets to include

        Returns:
            List of nets matching predicate
        """
        return [net for net in self._nets if predicate(net)]

    def bulk_update(self, criteria: Callable[[NetElement], bool], updates: Dict[str, Any]):
        """
        Update multiple nets matching criteria.

        Args:
            criteria: Function to select nets to update
            updates: Dictionary of property updates
        """
        updated_count = 0
        for net_element in self._nets:
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
        self._nets.clear()
        self._name_index.clear()
        self._mark_modified()

    def _add_to_indexes(self, net_element: NetElement):
        """Add net to internal indexes."""
        self._nets.append(net_element)
        self._name_index[net_element.name] = net_element

    def _remove_from_indexes(self, net_element: NetElement):
        """Remove net from internal indexes."""
        self._nets.remove(net_element)
        del self._name_index[net_element.name]

    def _update_name_index(self, old_name: str, net_element: NetElement):
        """Update name index when net name changes."""
        if old_name in self._name_index:
            del self._name_index[old_name]
        self._name_index[net_element.name] = net_element

    def _mark_modified(self):
        """Mark collection as modified."""
        self._modified = True

    # Collection interface methods
    def __len__(self) -> int:
        """Return number of nets."""
        return len(self._nets)

    def __iter__(self) -> Iterator[NetElement]:
        """Iterate over nets."""
        return iter(self._nets)

    def __getitem__(self, index: int) -> NetElement:
        """Get net by index."""
        return self._nets[index]

    def __bool__(self) -> bool:
        """Return True if collection has nets."""
        return len(self._nets) > 0
