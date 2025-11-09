"""
Network connectivity analysis for KiCAD schematics.

Implements comprehensive net tracing through wires, junctions, labels,
hierarchical connections, and power symbols.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from .geometry import points_equal
from .types import Junction, Label, LabelType, Point, SchematicSymbol, Wire

logger = logging.getLogger(__name__)


@dataclass
class PinConnection:
    """Represents a component pin in the connectivity graph."""

    reference: str  # Component reference (e.g., "R1")
    pin_number: str  # Pin number (e.g., "2")
    position: Point  # Absolute position of pin

    def __hash__(self):
        return hash((self.reference, self.pin_number))

    def __eq__(self, other):
        return self.reference == other.reference and self.pin_number == other.pin_number

    def __repr__(self):
        return f"{self.reference}.{self.pin_number}@({self.position.x:.2f},{self.position.y:.2f})"


@dataclass
class Net:
    """Represents an electrical net (connected set of pins/wires/labels)."""

    name: Optional[str] = None  # Net name (from label, or auto-generated)
    pins: Set[PinConnection] = field(default_factory=set)  # Connected pins
    wires: Set[str] = field(default_factory=set)  # Wire UUIDs
    junctions: Set[str] = field(default_factory=set)  # Junction UUIDs
    labels: Set[str] = field(default_factory=set)  # Label UUIDs
    points: Set[Tuple[float, float]] = field(default_factory=set)  # All connection points

    def add_pin(self, pin: PinConnection):
        """Add a pin to this net."""
        self.pins.add(pin)
        self.points.add((pin.position.x, pin.position.y))

    def merge(self, other: "Net"):
        """Merge another net into this one."""
        self.pins.update(other.pins)
        self.wires.update(other.wires)
        self.junctions.update(other.junctions)
        self.labels.update(other.labels)
        self.points.update(other.points)

        # Prefer named nets over unnamed
        if other.name and not self.name:
            self.name = other.name

    def __repr__(self):
        name_str = f"'{self.name}'" if self.name else "unnamed"
        return f"Net({name_str}, {len(self.pins)} pins, {len(self.wires)} wires)"


class ConnectivityAnalyzer:
    """
    Analyzes schematic connectivity and builds electrical nets.

    Traces connections through:
    - Direct wire-to-pin connections
    - Junction points connecting multiple wires
    - Labels connecting separated wire segments
    - Global labels (cross-schematic connections)
    - Hierarchical labels (parent-child sheet connections)
    - Power symbols (implicit global connections)
    """

    def __init__(self, tolerance: float = 0.01):
        """
        Initialize connectivity analyzer.

        Args:
            tolerance: Position matching tolerance in mm (default: 0.01)
        """
        self.tolerance = tolerance
        self.nets: List[Net] = []
        self._point_to_net: Dict[Tuple[float, float], Net] = {}
        self._pin_to_net: Dict[PinConnection, Net] = {}
        self._label_name_to_nets: Dict[str, List[Net]] = defaultdict(list)

        logger.info(f"Initialized ConnectivityAnalyzer (tolerance={tolerance}mm)")

    def analyze(self, schematic, hierarchical=True) -> List[Net]:
        """
        Analyze schematic connectivity and return all nets.

        Args:
            schematic: Schematic object to analyze (root schematic)
            hierarchical: If True, also analyze child sheets (default: True)

        Returns:
            List of Net objects representing all electrical connections
        """
        logger.info("Starting connectivity analysis...")

        # Collect all schematics (parent + children if hierarchical)
        if hierarchical:
            schematics = self._load_hierarchical_schematics(schematic)
            logger.info(f"Analyzing {len(schematics)} schematics (hierarchical)")
        else:
            schematics = [schematic]

        # Step 1: Build component pin positions from all schematics
        all_pin_positions = {}
        for sch in schematics:
            pin_positions = self._build_pin_positions(sch)
            all_pin_positions.update(pin_positions)
        logger.info(f"Found {len(all_pin_positions)} component pins across all sheets")

        # Step 2: Create initial nets from wire-to-pin connections
        for sch in schematics:
            sch_pins = {
                pc: pos
                for pc, pos in all_pin_positions.items()
                if any(c.reference == pc.reference for c in sch.components)
            }
            self._trace_wire_connections(sch, sch_pins)
        logger.info(f"Created {len(self.nets)} nets from wire connections")

        # Step 3: Merge nets connected by junctions
        for sch in schematics:
            self._merge_junction_nets(sch)
        logger.info(f"After junction merging: {len(self.nets)} nets")

        # Step 4: Merge nets connected by local labels
        for sch in schematics:
            self._merge_label_nets(sch)
        logger.info(f"After label merging: {len(self.nets)} nets")

        # Step 5: Process hierarchical connections (sheet pins ↔ hierarchical labels)
        if hierarchical and len(schematics) > 1:
            self._process_hierarchical_connections(schematic, schematics)
            logger.info(f"After hierarchical connections: {len(self.nets)} nets")

        # Step 6: Process power symbols (implicit global connections across ALL sheets)
        for sch in schematics:
            self._process_power_symbols(sch)
        logger.info(f"After power symbols: {len(self.nets)} nets")

        # Step 7: Handle global labels
        for sch in schematics:
            self._process_global_labels(sch)
        logger.info(f"After global labels: {len(self.nets)} nets")

        # Step 8: Auto-generate net names for unnamed nets
        self._generate_net_names()

        logger.info(f"Connectivity analysis complete: {len(self.nets)} nets")
        return self.nets

    def _build_pin_positions(self, schematic) -> Dict[PinConnection, Point]:
        """
        Build mapping of all component pins to their absolute positions.

        Args:
            schematic: Schematic to analyze

        Returns:
            Dict mapping PinConnection to absolute Point
        """
        from .pin_utils import list_component_pins

        pin_positions = {}

        for component in schematic.components:
            # Get all pins for this component
            pins = list_component_pins(component)

            for pin_number, pin_position in pins:
                if pin_position is not None:
                    pin_conn = PinConnection(
                        reference=component.reference, pin_number=pin_number, position=pin_position
                    )
                    pin_positions[pin_conn] = pin_position
                    logger.debug(f"  {pin_conn}")

        return pin_positions

    def _trace_wire_connections(self, schematic, pin_positions: Dict[PinConnection, Point]):
        """
        Create initial nets by tracing wire-to-pin connections.

        Args:
            schematic: Schematic to analyze
            pin_positions: Mapping of pins to positions
        """
        for wire in schematic.wires:
            # Get wire endpoints
            wire_points = wire.points
            if len(wire_points) < 2:
                logger.warning(f"Wire {wire.uuid} has < 2 points, skipping")
                continue

            # Find which pins connect to this wire
            connected_pins = set()

            for pin_conn, pin_pos in pin_positions.items():
                # Check if pin connects to any point on the wire
                for wire_point in wire_points:
                    if points_equal(wire_point, pin_pos, self.tolerance):
                        connected_pins.add(pin_conn)
                        logger.debug(f"  Wire {wire.uuid} connects to {pin_conn}")
                        break

            # Create or update net for this wire
            # Always create a net for the wire, even if no pins connect yet
            # (labels, junctions, or hierarchical connections may merge it later)
            if connected_pins:
                self._add_wire_to_net(wire, connected_pins, wire_points)
            else:
                # Create net for wire without pins (will be merged via labels/junctions)
                net = Net()
                net.wires.add(wire.uuid)
                for point in wire_points:
                    net.points.add((point.x, point.y))
                    self._point_to_net[(point.x, point.y)] = net
                self.nets.append(net)
                logger.debug(f"  Created net for wire {wire.uuid} without pins")

    def _add_wire_to_net(self, wire: Wire, pins: Set[PinConnection], wire_points: List[Point]):
        """
        Add wire and its connected pins to a net (create new or merge existing).

        Args:
            wire: Wire object
            pins: Set of pins connected to this wire
            wire_points: Points along the wire
        """
        # Check if any of these pins are already in a net
        existing_nets = set()
        for pin in pins:
            if pin in self._pin_to_net:
                existing_nets.add(self._pin_to_net[pin])

        if existing_nets:
            # Merge all existing nets into the first one
            primary_net = existing_nets.pop()
            for other_net in existing_nets:
                primary_net.merge(other_net)
                self.nets.remove(other_net)

            # Add new pins and wire to primary net
            for pin in pins:
                primary_net.add_pin(pin)
                self._pin_to_net[pin] = primary_net

            primary_net.wires.add(wire.uuid)
            for point in wire_points:
                primary_net.points.add((point.x, point.y))
                self._point_to_net[(point.x, point.y)] = primary_net
        else:
            # Create new net
            net = Net()
            for pin in pins:
                net.add_pin(pin)
                self._pin_to_net[pin] = net

            net.wires.add(wire.uuid)
            for point in wire_points:
                net.points.add((point.x, point.y))
                self._point_to_net[(point.x, point.y)] = net

            self.nets.append(net)
            logger.debug(f"  Created new {net}")

    def _merge_junction_nets(self, schematic):
        """
        Merge nets that are connected by junction points.

        Also includes wires at the junction that don't connect to pins
        (e.g., test point taps, voltage monitoring points).

        Args:
            schematic: Schematic to analyze
        """
        for junction in schematic.junctions:
            junc_pos = junction.position

            # Find all nets that have points at this junction position
            nets_at_junction = []

            for net in self.nets:
                for point in net.points:
                    if points_equal(Point(point[0], point[1]), junc_pos, self.tolerance):
                        if net not in nets_at_junction:  # Avoid duplicates
                            nets_at_junction.append(net)
                        break

            # Also find wires at this junction that aren't in any net yet
            # (e.g., tap wires that don't connect to component pins)
            unconnected_wires = []
            for wire in schematic.wires:
                # Check if wire has a point at junction
                wire_at_junction = False
                for wire_point in wire.points:
                    if points_equal(wire_point, junc_pos, self.tolerance):
                        wire_at_junction = True
                        break

                if wire_at_junction:
                    # Check if this wire is already in a net
                    wire_in_net = False
                    for net in nets_at_junction:
                        if wire.uuid in net.wires:
                            wire_in_net = True
                            break

                    if not wire_in_net:
                        unconnected_wires.append(wire)

            # If we have nets at junction, merge them and add unconnected wires
            if len(nets_at_junction) >= 1:
                primary_net = nets_at_junction[0]

                # Merge other nets
                for other_net in nets_at_junction[1:]:
                    primary_net.merge(other_net)

                    # Update all pin mappings
                    for pin in other_net.pins:
                        self._pin_to_net[pin] = primary_net

                    # Update all point mappings
                    for point in other_net.points:
                        self._point_to_net[point] = primary_net

                    self.nets.remove(other_net)

                # Add unconnected wires to the primary net
                for wire in unconnected_wires:
                    primary_net.wires.add(wire.uuid)
                    for point in wire.points:
                        primary_net.points.add((point.x, point.y))
                        self._point_to_net[(point.x, point.y)] = primary_net
                    logger.debug(f"Added unconnected wire {wire.uuid[:8]} to net at junction")

                primary_net.junctions.add(junction.uuid)

    def _merge_label_nets(self, schematic):
        """
        Merge nets that are connected by labels with the same name.

        Args:
            schematic: Schematic to analyze
        """
        # Process local labels only (global labels handled separately)
        local_labels = [
            label
            for label in schematic.labels
            if hasattr(label, "_data") and label._data.label_type == LabelType.LOCAL
        ]

        for label in local_labels:
            label_pos = label.position

            # Find which net this label is on
            net_for_label = None
            for net in self.nets:
                for point in net.points:
                    if points_equal(Point(point[0], point[1]), label_pos, self.tolerance):
                        net_for_label = net
                        break
                if net_for_label:
                    break

            if net_for_label:
                # Set or merge net name
                if not net_for_label.name:
                    net_for_label.name = label.text
                    logger.debug(f"Named {net_for_label} from label")

                net_for_label.labels.add(label.uuid)
                self._label_name_to_nets[label.text].append(net_for_label)

        # Merge nets with the same label name
        for label_name, nets_with_label in self._label_name_to_nets.items():
            if len(nets_with_label) > 1:
                logger.debug(f"Label '{label_name}' connects {len(nets_with_label)} nets")

                primary_net = nets_with_label[0]
                for other_net in nets_with_label[1:]:
                    if other_net in self.nets:  # Check if not already merged
                        primary_net.merge(other_net)

                        # Update mappings
                        for pin in other_net.pins:
                            self._pin_to_net[pin] = primary_net
                        for point in other_net.points:
                            self._point_to_net[point] = primary_net

                        self.nets.remove(other_net)

    def _process_power_symbols(self, schematic):
        """
        Process power symbols and create implicit global connections.

        Power symbols (like GND, VCC, +5V) create implicit global nets.
        All power symbols with the same value are electrically connected,
        even if they're not physically wired together.

        Args:
            schematic: Schematic to analyze
        """
        # Group power symbols by their value property
        power_symbol_nets_by_value = defaultdict(list)

        for component in schematic.components:
            # Identify power symbols by lib_id pattern
            if component.lib_id.startswith("power:"):
                power_value = component.value

                logger.debug(f"Found power symbol: {component.reference} (value={power_value})")

                # Find the net this power symbol is connected to
                # Power symbols have a single pin (usually pin "1")
                power_pin_conn = None
                for pin_conn in self._pin_to_net.keys():
                    if pin_conn.reference == component.reference:
                        power_pin_conn = pin_conn
                        break

                if power_pin_conn:
                    net = self._pin_to_net[power_pin_conn]
                    power_symbol_nets_by_value[power_value].append(net)
                    logger.debug(f"  Power symbol {component.reference} on net '{net.name}'")

        # Merge all nets with the same power symbol value
        for power_value, nets_to_merge in power_symbol_nets_by_value.items():
            if len(nets_to_merge) > 1:
                logger.debug(f"Merging {len(nets_to_merge)} nets for power symbol '{power_value}'")

                # Merge all nets into the first one
                primary_net = nets_to_merge[0]

                # Set the net name from power symbol value
                primary_net.name = power_value

                for other_net in nets_to_merge[1:]:
                    if other_net in self.nets:  # Check if not already merged
                        primary_net.merge(other_net)

                        # Update mappings
                        for pin in other_net.pins:
                            self._pin_to_net[pin] = primary_net
                        for point in other_net.points:
                            self._point_to_net[point] = primary_net

                        self.nets.remove(other_net)
            elif len(nets_to_merge) == 1:
                # Single power symbol - just name the net
                nets_to_merge[0].name = power_value

    def _process_global_labels(self, schematic):
        """
        Process global labels (cross-schematic connections).

        Args:
            schematic: Schematic to analyze
        """
        # TODO: Implement global label handling
        # Global labels with same name should connect across schematics
        pass

    def _generate_net_names(self):
        """Generate names for nets that don't have explicit names."""
        unnamed_counter = 1

        for net in self.nets:
            if not net.name:
                # Try to name from connected component pins
                if net.pins:
                    first_pin = next(iter(net.pins))
                    net.name = f"Net-({first_pin.reference}-Pad{first_pin.pin_number})"
                else:
                    net.name = f"Net-(unnamed-{unnamed_counter})"
                    unnamed_counter += 1

    def are_connected(self, ref1: str, pin1: str, ref2: str, pin2: str) -> bool:
        """
        Check if two pins are electrically connected.

        Args:
            ref1: First component reference
            pin1: First pin number
            ref2: Second component reference
            pin2: Second pin number

        Returns:
            True if pins are on the same net, False otherwise
        """
        # Find pins in the connectivity graph
        pin_conn1 = None
        pin_conn2 = None

        for pin in self._pin_to_net.keys():
            if pin.reference == ref1 and pin.pin_number == pin1:
                pin_conn1 = pin
            if pin.reference == ref2 and pin.pin_number == pin2:
                pin_conn2 = pin

        if not pin_conn1 or not pin_conn2:
            return False

        # Check if both pins are in the same net
        net1 = self._pin_to_net.get(pin_conn1)
        net2 = self._pin_to_net.get(pin_conn2)

        return net1 is not None and net1 is net2

    def _load_hierarchical_schematics(self, root_schematic):
        """
        Load root schematic and all child schematics.

        Args:
            root_schematic: Root schematic object

        Returns:
            List of all schematics (root + children)
        """
        from pathlib import Path

        schematics = [root_schematic]

        # Check if root schematic has hierarchical sheets
        if not hasattr(root_schematic, "_data") or "sheets" not in root_schematic._data:
            return schematics

        sheets = root_schematic._data.get("sheets", [])

        # Load each child schematic
        root_path = Path(root_schematic.file_path) if root_schematic.file_path else None

        for sheet in sheets:
            sheet_filename = sheet.get("filename")
            if not sheet_filename:
                continue

            # Build path to child schematic
            if root_path:
                child_path = root_path.parent / sheet_filename
            else:
                child_path = Path(sheet_filename)

            if child_path.exists():
                try:
                    # Import Schematic class - use absolute import to avoid circular dependency
                    import kicad_sch_api as ksa

                    child_sch = ksa.Schematic.load(str(child_path))
                    schematics.append(child_sch)
                    logger.info(f"Loaded child schematic: {sheet_filename}")
                except Exception as e:
                    logger.warning(f"Could not load child schematic {sheet_filename}: {e}")
            else:
                logger.warning(f"Child schematic not found: {child_path}")

        return schematics

    def _process_hierarchical_connections(self, root_schematic, all_schematics):
        """
        Process hierarchical connections between parent and child sheets.

        Connects sheet pins in parent to hierarchical labels in child sheets.

        Args:
            root_schematic: Root schematic with hierarchical sheets
            all_schematics: List of all schematics (root + children)
        """
        from pathlib import Path

        if not hasattr(root_schematic, "_data") or "sheets" not in root_schematic._data:
            return

        sheets = root_schematic._data.get("sheets", [])

        for sheet_data in sheets:
            sheet_filename = sheet_data.get("filename")
            sheet_pins = sheet_data.get("pins", [])

            if not sheet_filename or not sheet_pins:
                continue

            # Find the child schematic
            child_sch = None
            for sch in all_schematics:
                if sch.file_path and Path(sch.file_path).name == sheet_filename:
                    child_sch = sch
                    break

            if not child_sch:
                logger.warning(f"Child schematic not found for sheet: {sheet_filename}")
                continue

            # For each sheet pin, find matching hierarchical label in child
            for pin_data in sheet_pins:
                pin_name = pin_data.get("name")
                pin_position = pin_data.get("position")

                if not pin_name or not pin_position:
                    continue

                pin_pos = Point(pin_position["x"], pin_position["y"])

                # Find net at sheet pin position in parent
                parent_net = None
                for net in self.nets:
                    for point in net.points:
                        if points_equal(Point(point[0], point[1]), pin_pos, self.tolerance):
                            parent_net = net
                            break
                    if parent_net:
                        break

                if not parent_net:
                    logger.debug(f"No net found at sheet pin '{pin_name}' position")
                    continue

                # Find matching hierarchical label in child schematic
                for hier_label in child_sch.hierarchical_labels:
                    if hier_label.text == pin_name:
                        label_pos = hier_label.position

                        # Find net at hierarchical label position in child
                        child_net = None
                        for net in self.nets:
                            for point in net.points:
                                if points_equal(
                                    Point(point[0], point[1]), label_pos, self.tolerance
                                ):
                                    child_net = net
                                    break
                            if child_net:
                                break

                        if child_net and child_net is not parent_net:
                            # Merge child net into parent net
                            logger.debug(f"Merging nets via hierarchical connection '{pin_name}'")
                            parent_net.merge(child_net)

                            # Update mappings
                            for pin in child_net.pins:
                                self._pin_to_net[pin] = parent_net
                            for point in child_net.points:
                                self._point_to_net[point] = parent_net

                            self.nets.remove(child_net)

                        break

    def get_net_for_pin(self, reference: str, pin_number: str) -> Optional[Net]:
        """
        Get the net connected to a specific pin.

        Args:
            reference: Component reference
            pin_number: Pin number

        Returns:
            Net object if pin is connected, None otherwise
        """
        for pin in self._pin_to_net.keys():
            if pin.reference == reference and pin.pin_number == pin_number:
                return self._pin_to_net[pin]

        return None

    def get_connected_pins(self, reference: str, pin_number: str) -> List[Tuple[str, str]]:
        """
        Get all pins connected to a specific pin.

        Args:
            reference: Component reference
            pin_number: Pin number

        Returns:
            List of (reference, pin_number) tuples for connected pins
        """
        net = self.get_net_for_pin(reference, pin_number)
        if not net:
            return []

        return [
            (pin.reference, pin.pin_number)
            for pin in net.pins
            if not (pin.reference == reference and pin.pin_number == pin_number)
        ]
