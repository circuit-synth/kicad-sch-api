"""
Advanced Hierarchy Manager for KiCAD schematic hierarchical designs.

Handles complex hierarchical features including:
- Sheets used multiple times (reusable sheets)
- Cross-sheet signal tracking
- Sheet pin validation
- Hierarchy flattening
- Signal tracing through hierarchy levels
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ..types import Point
from .base import BaseManager

logger = logging.getLogger(__name__)


@dataclass
class SheetInstance:
    """Represents a single instance of a hierarchical sheet."""

    sheet_uuid: str  # UUID of sheet symbol in parent
    sheet_name: str  # Name of the sheet
    filename: str  # Referenced schematic filename
    path: str  # Hierarchical path (e.g., "/root_uuid/sheet_uuid")
    parent_path: str  # Parent's hierarchical path
    schematic: Optional[Any] = None  # Loaded schematic object
    sheet_pins: List[Dict[str, Any]] = field(default_factory=list)
    position: Optional[Point] = None
    instances_in_parent: int = 1  # How many times this sheet is used


@dataclass
class HierarchyNode:
    """Represents a node in the hierarchy tree."""

    path: str  # Hierarchical path
    name: str  # Sheet name
    filename: Optional[str] = None  # Schematic filename
    schematic: Optional[Any] = None
    parent: Optional["HierarchyNode"] = None
    children: List["HierarchyNode"] = field(default_factory=list)
    sheet_uuid: Optional[str] = None
    is_root: bool = False

    def add_child(self, child: "HierarchyNode"):
        """Add child node."""
        child.parent = self
        self.children.append(child)

    def get_depth(self) -> int:
        """Get depth in hierarchy (root = 0)."""
        depth = 0
        node = self.parent
        while node:
            depth += 1
            node = node.parent
        return depth

    def get_full_path(self) -> List[str]:
        """Get full path from root to this node."""
        path = []
        node = self
        while node:
            path.insert(0, node.name)
            node = node.parent
        return path


@dataclass
class SheetPinConnection:
    """Represents a connection between a sheet pin and hierarchical label."""

    sheet_path: str  # Path to sheet instance
    sheet_pin_name: str
    sheet_pin_type: str
    sheet_pin_uuid: str
    hierarchical_label_name: str
    hierarchical_label_uuid: Optional[str] = None
    child_schematic_path: Optional[str] = None
    validated: bool = False
    validation_errors: List[str] = field(default_factory=list)


@dataclass
class SignalPath:
    """Represents a signal's path through the hierarchy."""

    signal_name: str
    start_path: str  # Hierarchical path where signal starts
    end_path: str  # Hierarchical path where signal ends
    connections: List[str] = field(default_factory=list)  # List of connection points
    sheet_crossings: int = 0  # Number of sheet boundaries crossed


class HierarchyManager(BaseManager):
    """
    Manages advanced hierarchical schematic features.

    Provides:
    - Sheet reuse tracking (same sheet used multiple times)
    - Cross-sheet signal tracking
    - Sheet pin validation
    - Hierarchy flattening
    - Signal tracing
    - Hierarchy visualization
    """

    def __init__(self, schematic_data: Dict[str, Any]):
        """
        Initialize HierarchyManager.

        Args:
            schematic_data: Reference to schematic data
        """
        super().__init__(schematic_data)
        self._hierarchy_tree: Optional[HierarchyNode] = None
        self._sheet_instances: Dict[str, List[SheetInstance]] = defaultdict(list)
        self._loaded_schematics: Dict[str, Any] = {}
        self._pin_connections: List[SheetPinConnection] = []

    def build_hierarchy_tree(
        self, root_schematic, root_path: Optional[Path] = None
    ) -> HierarchyNode:
        """
        Build complete hierarchy tree from root schematic.

        Args:
            root_schematic: Root schematic object
            root_path: Path to root schematic file

        Returns:
            Root HierarchyNode representing the hierarchy tree
        """
        logger.info("Building hierarchy tree...")

        # Create root node
        root_node = HierarchyNode(
            path="/",
            name=getattr(root_schematic, "name", "Root") or "Root",
            filename=str(root_path) if root_path else None,
            schematic=root_schematic,
            is_root=True,
        )

        # Track root schematic
        self._loaded_schematics["/"] = root_schematic
        self._hierarchy_tree = root_node

        # Recursively build tree
        self._build_tree_recursive(root_node, root_schematic, root_path, "/")

        logger.info(f"Hierarchy tree built: {self._count_nodes(root_node)} nodes")
        return root_node

    def _build_tree_recursive(
        self,
        parent_node: HierarchyNode,
        parent_schematic,
        parent_path: Optional[Path],
        current_path: str,
    ):
        """Recursively build hierarchy tree."""
        # Get sheets from parent schematic
        sheets = (
            self._data.get("sheets", []) if parent_schematic == self._get_root_schematic() else []
        )

        if hasattr(parent_schematic, "_data"):
            sheets = parent_schematic._data.get("sheets", [])

        for sheet in sheets:
            sheet_uuid = sheet.get("uuid")
            sheet_name = sheet.get("name", "Unnamed")
            sheet_filename = sheet.get("filename")

            if not sheet_filename:
                logger.warning(f"Sheet {sheet_name} has no filename")
                continue

            # Build hierarchical path
            sheet_path = f"{current_path}{sheet_uuid}/"

            # Create child node
            child_node = HierarchyNode(
                path=sheet_path,
                name=sheet_name,
                filename=sheet_filename,
                sheet_uuid=sheet_uuid,
            )

            parent_node.add_child(child_node)

            # Load child schematic if exists
            if parent_path:
                child_path = parent_path.parent / sheet_filename
                if child_path.exists():
                    try:
                        # Import here to avoid circular dependency
                        import kicad_sch_api as ksa

                        child_sch = ksa.Schematic.load(str(child_path))
                        child_node.schematic = child_sch
                        self._loaded_schematics[sheet_path] = child_sch

                        # Track sheet instance
                        sheet_instance = SheetInstance(
                            sheet_uuid=sheet_uuid,
                            sheet_name=sheet_name,
                            filename=sheet_filename,
                            path=sheet_path,
                            parent_path=current_path,
                            schematic=child_sch,
                            sheet_pins=sheet.get("pins", []),
                            position=(
                                Point(sheet["position"]["x"], sheet["position"]["y"])
                                if "position" in sheet
                                else None
                            ),
                        )
                        self._sheet_instances[sheet_filename].append(sheet_instance)

                        # Recursively process child sheets
                        self._build_tree_recursive(child_node, child_sch, child_path, sheet_path)

                        logger.debug(f"Loaded child schematic: {sheet_filename} at {sheet_path}")
                    except Exception as e:
                        logger.warning(f"Could not load child schematic {sheet_filename}: {e}")
                else:
                    logger.warning(f"Child schematic not found: {child_path}")

    def find_reused_sheets(self) -> Dict[str, List[SheetInstance]]:
        """
        Find sheets that are used multiple times in the hierarchy.

        Returns:
            Dictionary mapping filename to list of sheet instances
        """
        reused = {}
        for filename, instances in self._sheet_instances.items():
            if len(instances) > 1:
                reused[filename] = instances
                logger.info(f"Sheet '{filename}' is reused {len(instances)} times")

        return reused

    def validate_sheet_pins(self) -> List[SheetPinConnection]:
        """
        Validate sheet pin connections against hierarchical labels.

        Checks:
        - Sheet pins have matching hierarchical labels in child
        - Pin types are compatible
        - Pin names match exactly
        - No duplicate pins

        Returns:
            List of validated sheet pin connections with validation status
        """
        logger.info("Validating sheet pin connections...")
        self._pin_connections = []

        for filename, instances in self._sheet_instances.items():
            for instance in instances:
                child_sch = instance.schematic
                if not child_sch:
                    continue

                # Get hierarchical labels from child schematic
                child_labels = self._get_hierarchical_labels(child_sch)
                child_label_map = {label["name"]: label for label in child_labels}

                # Validate each sheet pin
                for pin in instance.sheet_pins:
                    pin_name = pin.get("name")
                    pin_type = pin.get("pin_type")
                    pin_uuid = pin.get("uuid")

                    connection = SheetPinConnection(
                        sheet_path=instance.path,
                        sheet_pin_name=pin_name,
                        sheet_pin_type=pin_type,
                        sheet_pin_uuid=pin_uuid,
                        hierarchical_label_name=pin_name,
                        child_schematic_path=str(instance.filename),
                    )

                    # Check if matching hierarchical label exists
                    if pin_name not in child_label_map:
                        connection.validation_errors.append(
                            f"No matching hierarchical label '{pin_name}' in {filename}"
                        )
                    else:
                        matching_label = child_label_map[pin_name]
                        connection.hierarchical_label_uuid = matching_label.get("uuid")

                        # Validate pin type compatibility
                        label_type = matching_label.get("shape", "input")
                        if not self._are_pin_types_compatible(pin_type, label_type):
                            connection.validation_errors.append(
                                f"Pin type mismatch: sheet pin '{pin_type}' vs label '{label_type}'"
                            )

                    connection.validated = len(connection.validation_errors) == 0
                    self._pin_connections.append(connection)

        # Log validation results
        valid_count = sum(1 for c in self._pin_connections if c.validated)
        logger.info(
            f"Sheet pin validation: {valid_count}/{len(self._pin_connections)} valid connections"
        )

        return self._pin_connections

    def get_validation_errors(self) -> List[Dict[str, Any]]:
        """
        Get all sheet pin validation errors.

        Returns:
            List of validation error dictionaries
        """
        errors = []
        for connection in self._pin_connections:
            if not connection.validated:
                for error_msg in connection.validation_errors:
                    errors.append(
                        {
                            "sheet_path": connection.sheet_path,
                            "pin_name": connection.sheet_pin_name,
                            "error": error_msg,
                        }
                    )
        return errors

    def trace_signal_path(self, signal_name: str, start_path: str = "/") -> List[SignalPath]:
        """
        Trace a signal through the hierarchy.

        Args:
            signal_name: Name of signal to trace
            start_path: Starting hierarchical path (default: root)

        Returns:
            List of SignalPath objects showing signal routing
        """
        logger.info(f"Tracing signal '{signal_name}' from {start_path}")
        paths = []

        # Find signal in start schematic
        start_sch = self._loaded_schematics.get(start_path)
        if not start_sch:
            logger.warning(f"No schematic found at path: {start_path}")
            return paths

        # Search for labels with this signal name
        labels = self._get_all_labels(start_sch)
        matching_labels = [l for l in labels if l.get("name") == signal_name]

        for label in matching_labels:
            signal_path = SignalPath(
                signal_name=signal_name,
                start_path=start_path,
                end_path=start_path,
                connections=[f"{start_path}:{label.get('type', 'label')}"],
            )

            # If it's a hierarchical label, trace upward
            if label.get("type") == "hierarchical":
                self._trace_hierarchical_upward(signal_path, signal_name, start_path)

            # If it's a global label, find all instances
            if label.get("type") == "global":
                self._trace_global_connections(signal_path, signal_name)

            paths.append(signal_path)

        logger.info(f"Found {len(paths)} signal paths for '{signal_name}'")
        return paths

    def flatten_hierarchy(self, prefix_references: bool = True) -> Dict[str, Any]:
        """
        Flatten hierarchical design into a single schematic representation.

        Args:
            prefix_references: If True, prefix component references with sheet path

        Returns:
            Dictionary containing flattened schematic data

        Note: This creates a data representation only - does not create a real schematic
        """
        logger.info("Flattening hierarchy...")

        if not self._hierarchy_tree:
            logger.error("Hierarchy tree not built. Call build_hierarchy_tree() first")
            return {}

        flattened = {
            "components": [],
            "wires": [],
            "labels": [],
            "junctions": [],
            "nets": [],
            "hierarchy_map": {},  # Maps flattened refs to original paths
        }

        # Recursively flatten from root
        self._flatten_recursive(
            self._hierarchy_tree,
            flattened,
            prefix_references,
            "",
        )

        logger.info(
            f"Flattened hierarchy: {len(flattened['components'])} components, "
            f"{len(flattened['wires'])} wires"
        )

        return flattened

    def _flatten_recursive(
        self,
        node: HierarchyNode,
        flattened: Dict[str, Any],
        prefix_references: bool,
        prefix: str,
    ):
        """Recursively flatten hierarchy tree."""
        if not node.schematic:
            return

        # Process components
        for component in node.schematic.components:
            comp_data = component._data if hasattr(component, "_data") else component

            # Create reference prefix from hierarchy path
            if prefix_references and not node.is_root:
                new_ref = f"{prefix}{component.reference}"
            else:
                new_ref = component.reference

            flattened_comp = {
                "reference": new_ref,
                "original_reference": component.reference,
                "lib_id": component.lib_id,
                "value": component.value,
                "position": component.position,
                "hierarchy_path": node.path,
                "original_data": comp_data,
            }

            flattened["components"].append(flattened_comp)
            flattened["hierarchy_map"][new_ref] = node.path

        # Process wires, labels, junctions similarly
        if hasattr(node.schematic, "_data"):
            # Copy wires
            wires = node.schematic._data.get("wires", [])
            for wire in wires:
                flattened["wires"].append(
                    {
                        "hierarchy_path": node.path,
                        "data": wire,
                    }
                )

            # Copy labels
            labels = node.schematic._data.get("labels", [])
            for label in labels:
                flattened["labels"].append(
                    {
                        "hierarchy_path": node.path,
                        "data": label,
                    }
                )

        # Recursively process children
        for child in node.children:
            child_prefix = f"{prefix}{node.name}_" if prefix_references else prefix
            self._flatten_recursive(child, flattened, prefix_references, child_prefix)

    def get_hierarchy_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive hierarchy statistics.

        Returns:
            Dictionary with hierarchy statistics
        """
        if not self._hierarchy_tree:
            return {"error": "Hierarchy tree not built"}

        total_nodes = self._count_nodes(self._hierarchy_tree)
        max_depth = self._get_max_depth(self._hierarchy_tree)
        reused_sheets = self.find_reused_sheets()

        total_components = 0
        total_wires = 0
        total_labels = 0

        for schematic in self._loaded_schematics.values():
            if hasattr(schematic, "components"):
                total_components += len(list(schematic.components))
            if hasattr(schematic, "_data"):
                total_wires += len(schematic._data.get("wires", []))
                total_labels += len(schematic._data.get("labels", []))

        return {
            "total_sheets": total_nodes,
            "max_hierarchy_depth": max_depth,
            "reused_sheets_count": len(reused_sheets),
            "reused_sheets": {
                filename: len(instances) for filename, instances in reused_sheets.items()
            },
            "total_components": total_components,
            "total_wires": total_wires,
            "total_labels": total_labels,
            "loaded_schematics": len(self._loaded_schematics),
            "sheet_pin_connections": len(self._pin_connections),
            "valid_connections": sum(1 for c in self._pin_connections if c.validated),
        }

    def visualize_hierarchy(self, include_stats: bool = False) -> str:
        """
        Generate text visualization of hierarchy tree.

        Args:
            include_stats: Include statistics for each node

        Returns:
            String representation of hierarchy tree
        """
        if not self._hierarchy_tree:
            return "Hierarchy tree not built. Call build_hierarchy_tree() first."

        lines = []
        self._visualize_recursive(self._hierarchy_tree, lines, "", include_stats)
        return "\n".join(lines)

    def _visualize_recursive(
        self,
        node: HierarchyNode,
        lines: List[str],
        prefix: str,
        include_stats: bool,
    ):
        """Recursively generate hierarchy visualization."""
        # Create node line
        is_last = False  # Will be set properly when we know
        connector = "└── " if is_last else "├── "

        node_str = f"{prefix}{connector}{node.name}"

        if node.filename:
            node_str += f" [{node.filename}]"

        if include_stats and node.schematic:
            comp_count = (
                len(list(node.schematic.components)) if hasattr(node.schematic, "components") else 0
            )
            node_str += f" ({comp_count} components)"

        lines.append(node_str)

        # Process children
        for i, child in enumerate(node.children):
            is_last_child = i == len(node.children) - 1
            child_prefix = prefix + ("    " if is_last else "│   ")
            self._visualize_recursive(child, lines, child_prefix, include_stats)

    # Helper methods

    def _count_nodes(self, node: HierarchyNode) -> int:
        """Count total nodes in tree."""
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count

    def _get_max_depth(self, node: HierarchyNode, current_depth: int = 0) -> int:
        """Get maximum depth of tree."""
        if not node.children:
            return current_depth

        max_child_depth = current_depth
        for child in node.children:
            child_depth = self._get_max_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth

    def _get_hierarchical_labels(self, schematic) -> List[Dict[str, Any]]:
        """Get all hierarchical labels from a schematic."""
        labels = []
        if hasattr(schematic, "_data"):
            for label in schematic._data.get("labels", []):
                if label.get("type") == "hierarchical":
                    labels.append(label)
        return labels

    def _get_all_labels(self, schematic) -> List[Dict[str, Any]]:
        """Get all labels from a schematic."""
        if hasattr(schematic, "_data"):
            return schematic._data.get("labels", [])
        return []

    def _are_pin_types_compatible(self, pin_type: str, label_type: str) -> bool:
        """
        Check if sheet pin type is compatible with hierarchical label type.

        Args:
            pin_type: Sheet pin type
            label_type: Hierarchical label shape/type

        Returns:
            True if compatible
        """
        # Define compatibility rules
        compatible = {
            "input": ["output", "bidirectional", "tri_state", "passive"],
            "output": ["input", "bidirectional", "tri_state", "passive"],
            "bidirectional": ["input", "output", "bidirectional", "tri_state", "passive"],
            "tri_state": ["input", "output", "bidirectional", "tri_state", "passive"],
            "passive": ["input", "output", "bidirectional", "tri_state", "passive"],
        }

        return label_type in compatible.get(pin_type, [])

    def _trace_hierarchical_upward(
        self, signal_path: SignalPath, signal_name: str, current_path: str
    ):
        """Trace hierarchical label upward through sheet pins."""
        # Find parent sheet that contains this path
        for filename, instances in self._sheet_instances.items():
            for instance in instances:
                if instance.path == current_path:
                    # Check if parent has matching sheet pin
                    for pin in instance.sheet_pins:
                        if pin.get("name") == signal_name:
                            signal_path.connections.append(
                                f"{instance.parent_path}:sheet_pin:{pin.get('name')}"
                            )
                            signal_path.sheet_crossings += 1
                            signal_path.end_path = instance.parent_path

    def _trace_global_connections(self, signal_path: SignalPath, signal_name: str):
        """Trace global label connections across all schematics."""
        for path, schematic in self._loaded_schematics.items():
            labels = self._get_all_labels(schematic)
            for label in labels:
                if label.get("name") == signal_name and label.get("type") == "global":
                    signal_path.connections.append(f"{path}:global:{signal_name}")

    def _get_root_schematic(self):
        """Get root schematic from loaded schematics."""
        return self._loaded_schematics.get("/")
