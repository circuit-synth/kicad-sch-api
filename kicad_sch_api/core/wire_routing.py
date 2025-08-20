"""
Simple wire routing and connectivity detection for KiCAD schematics.

Provides basic wire routing between component pins and pin connectivity detection.
All positioning follows KiCAD's 1.27mm grid alignment rules.
"""

from typing import List, Optional, Tuple, Union
from .types import Point


def snap_to_kicad_grid(position: Union[Point, Tuple[float, float]], grid_size: float = 1.27) -> Point:
    """
    Snap position to KiCAD's standard 1.27mm grid.
    
    KiCAD uses a 1.27mm (0.05 inch) grid for precise electrical connections.
    ALL components, wires, and labels must be exactly on grid points.
    
    Args:
        position: Point or (x, y) tuple to snap
        grid_size: Grid size in mm (default 1.27mm)
        
    Returns:
        Point snapped to grid
    """
    if isinstance(position, Point):
        x, y = position.x, position.y
    else:
        x, y = position
    
    # Round to nearest grid point
    snapped_x = round(x / grid_size) * grid_size
    snapped_y = round(y / grid_size) * grid_size
    
    return Point(snapped_x, snapped_y)


def calculate_component_position_for_grid_pins(pin_offsets: List[Tuple[float, float]], target_pin_grid_pos: Point, target_pin_index: int = 0) -> Point:
    """
    Calculate component position so that pins land exactly on grid points.
    
    Args:
        pin_offsets: List of (x_offset, y_offset) tuples for each pin relative to component center
        target_pin_grid_pos: Desired grid position for the target pin
        target_pin_index: Index of pin to align to grid (default: pin 0)
        
    Returns:
        Component center position that places target pin on grid
    """
    target_offset_x, target_offset_y = pin_offsets[target_pin_index]
    
    # Component center = target pin position - pin offset
    comp_center_x = target_pin_grid_pos.x - target_offset_x
    comp_center_y = target_pin_grid_pos.y - target_offset_y
    
    return Point(comp_center_x, comp_center_y)


def get_resistor_grid_position(target_pin1_grid: Point) -> Point:
    """
    Get component position for Device:R resistor so pin 1 is at target grid position.
    
    Device:R resistor pin offsets: Pin 1 = (0, +3.81), Pin 2 = (0, -3.81)
    
    Args:
        target_pin1_grid: Desired grid position for pin 1
        
    Returns:
        Component center position
    """
    # Device:R pin offsets (standard KiCAD library values)
    pin_offsets = [(0.0, 3.81), (0.0, -3.81)]  # Pin 1 and Pin 2 offsets
    return calculate_component_position_for_grid_pins(pin_offsets, target_pin1_grid, 0)


def route_pins_direct(pin1_position: Point, pin2_position: Point) -> Point:
    """
    Simple direct routing between two pins.
    Just draws a straight wire - ok to go through other components.
    
    Args:
        pin1_position: Position of first pin
        pin2_position: Position of second pin
        
    Returns:
        End point (pin2_position) for wire creation
    """
    return pin2_position


def are_pins_connected(schematic, comp1_ref: str, pin1_num: str, comp2_ref: str, pin2_num: str) -> bool:
    """
    Detect if two component pins are connected via wires or labels (local or hierarchical).
    
    Checks for electrical connectivity through:
    1. Direct wire connections
    2. Indirect wire network connections  
    3. Local labels on connected nets
    4. Hierarchical labels for inter-sheet connections
    
    Args:
        schematic: The schematic object to analyze
        comp1_ref: Reference of first component (e.g., 'R1')
        pin1_num: Pin number on first component (e.g., '1')
        comp2_ref: Reference of second component (e.g., 'R2') 
        pin2_num: Pin number on second component (e.g., '2')
        
    Returns:
        True if pins are electrically connected, False otherwise
    """
    # Get pin positions
    pin1_pos = schematic.get_component_pin_position(comp1_ref, pin1_num)
    pin2_pos = schematic.get_component_pin_position(comp2_ref, pin2_num)
    
    if not pin1_pos or not pin2_pos:
        return False
    
    # 1. Check for direct wire connection between the pins
    for wire in schematic.wires:
        wire_start = wire.points[0]
        wire_end = wire.points[-1]  # Last point for multi-segment wires
        
        # Check if wire directly connects the two pins
        if ((wire_start.x == pin1_pos.x and wire_start.y == pin1_pos.y and 
             wire_end.x == pin2_pos.x and wire_end.y == pin2_pos.y) or
            (wire_start.x == pin2_pos.x and wire_start.y == pin2_pos.y and 
             wire_end.x == pin1_pos.x and wire_end.y == pin1_pos.y)):
            return True
    
    # 2. Check for indirect connection through wire network
    visited_wires = set()
    if _pins_connected_via_wire_network(schematic, pin1_pos, pin2_pos, visited_wires):
        return True
    
    # 3. Check for connection via local labels
    if _pins_connected_via_labels(schematic, pin1_pos, pin2_pos):
        return True
    
    # 4. Check for connection via hierarchical labels  
    if _pins_connected_via_hierarchical_labels(schematic, pin1_pos, pin2_pos):
        return True
    
    return False


def _pins_connected_via_wire_network(schematic, pin1_pos: Point, pin2_pos: Point, visited_wires: set) -> bool:
    """
    Check if pins are connected through wire network tracing.
    
    Args:
        schematic: The schematic object
        pin1_pos: First pin position
        pin2_pos: Second pin position  
        visited_wires: Set to track visited wires
        
    Returns:
        True if pins connected via wire network
    """
    # Find all wires connected to pin1
    pin1_wires = []
    for wire in schematic.wires:
        for point in wire.points:
            if point.x == pin1_pos.x and point.y == pin1_pos.y:
                pin1_wires.append(wire)
                break
    
    # For each wire connected to pin1, trace the network to see if it reaches pin2
    visited_wire_uuids = set()  # Use UUIDs instead of Wire objects
    for start_wire in pin1_wires:
        if _trace_wire_network(schematic, start_wire, pin2_pos, visited_wire_uuids):
            return True
    
    return False


def _pins_connected_via_labels(schematic, pin1_pos: Point, pin2_pos: Point) -> bool:
    """
    Check if pins are connected via local labels (net names).
    
    Two pins are connected if they're on nets with the same label name.
    
    Args:
        schematic: The schematic object
        pin1_pos: First pin position
        pin2_pos: Second pin position
        
    Returns:
        True if pins connected via same local label
    """
    # Get labels connected to pin1's net
    pin1_labels = _get_net_labels_at_position(schematic, pin1_pos)
    if not pin1_labels:
        return False
    
    # Get labels connected to pin2's net  
    pin2_labels = _get_net_labels_at_position(schematic, pin2_pos)
    if not pin2_labels:
        return False
    
    # Check if any label names match (case-insensitive)
    pin1_names = {label.text.upper() for label in pin1_labels}
    pin2_names = {label.text.upper() for label in pin2_labels}
    
    return bool(pin1_names.intersection(pin2_names))


def _pins_connected_via_hierarchical_labels(schematic, pin1_pos: Point, pin2_pos: Point) -> bool:
    """
    Check if pins are connected via hierarchical labels.
    
    Hierarchical labels create connections between different sheets in a hierarchy.
    
    Args:
        schematic: The schematic object
        pin1_pos: First pin position
        pin2_pos: Second pin position
        
    Returns:
        True if pins connected via hierarchical labels
    """
    # Get hierarchical labels connected to pin1's net
    pin1_hier_labels = _get_hierarchical_labels_at_position(schematic, pin1_pos)
    if not pin1_hier_labels:
        return False
    
    # Get hierarchical labels connected to pin2's net
    pin2_hier_labels = _get_hierarchical_labels_at_position(schematic, pin2_pos)
    if not pin2_hier_labels:
        return False
    
    # Check if any hierarchical label names match (case-insensitive)
    pin1_names = {label.text.upper() for label in pin1_hier_labels}
    pin2_names = {label.text.upper() for label in pin2_hier_labels}
    
    return bool(pin1_names.intersection(pin2_names))


def _get_net_labels_at_position(schematic, position: Point) -> List:
    """
    Get all local labels connected to the wire network at the given position.
    
    Uses coordinate proximity matching like kicad-skip (0.6mm tolerance).
    
    Args:
        schematic: The schematic object
        position: Pin position to check
        
    Returns:
        List of labels connected to this position's net
    """
    connected_labels = []
    tolerance = 0.0  # Zero tolerance - KiCAD requires exact coordinate matching
    
    # Find all wires connected to this position
    connected_wires = []
    for wire in schematic.wires:
        for point in wire.points:
            if point.x == position.x and point.y == position.y:
                connected_wires.append(wire)
                break
    
    # Find labels near any connected wire points
    labels_data = schematic._data.get("labels", [])
    for label_dict in labels_data:
        label_pos_dict = label_dict.get("position", {})
        label_pos = Point(label_pos_dict.get("x", 0), label_pos_dict.get("y", 0))
        
        # Check if label is near any connected wire
        for wire in connected_wires:
            for wire_point in wire.points:
                if (label_pos.x == wire_point.x and 
                    label_pos.y == wire_point.y):
                    # Create a simple object with text attribute
                    class SimpleLabel:
                        def __init__(self, text):
                            self.text = text
                    connected_labels.append(SimpleLabel(label_dict.get("text", "")))
                    break
    
    return connected_labels


def _get_hierarchical_labels_at_position(schematic, position: Point) -> List:
    """
    Get all hierarchical labels connected to the wire network at the given position.
    
    Args:
        schematic: The schematic object
        position: Pin position to check
        
    Returns:
        List of hierarchical labels connected to this position's net
    """
    connected_labels = []
    tolerance = 0.0  # Zero tolerance - KiCAD requires exact coordinate matching
    
    # Find all wires connected to this position
    connected_wires = []
    for wire in schematic.wires:
        for point in wire.points:
            if point.x == position.x and point.y == position.y:
                connected_wires.append(wire)
                break
    
    # Find hierarchical labels near any connected wire points  
    hier_labels_data = schematic._data.get("hierarchical_labels", [])
    for label_dict in hier_labels_data:
        label_pos_dict = label_dict.get("position", {})
        label_pos = Point(label_pos_dict.get("x", 0), label_pos_dict.get("y", 0))
        
        # Check if hierarchical label is near any connected wire
        for wire in connected_wires:
            for wire_point in wire.points:
                if (label_pos.x == wire_point.x and 
                    label_pos.y == wire_point.y):
                    # Create a simple object with text attribute
                    class SimpleLabel:
                        def __init__(self, text):
                            self.text = text
                    connected_labels.append(SimpleLabel(label_dict.get("text", "")))
                    break
    
    return connected_labels


def _trace_wire_network(schematic, current_wire, target_position: Point, visited_uuids: set) -> bool:
    """
    Recursively trace wire network to find if it reaches target position.
    
    Args:
        schematic: The schematic object
        current_wire: Current wire being traced
        target_position: Target pin position we're looking for
        visited_uuids: Set of already visited wire UUIDs to prevent infinite loops
        
    Returns:
        True if network reaches target position
    """
    wire_uuid = current_wire.uuid
    if wire_uuid in visited_uuids:
        return False
    
    visited_uuids.add(wire_uuid)
    
    # Check if current wire reaches target
    for point in current_wire.points:
        if point.x == target_position.x and point.y == target_position.y:
            return True
    
    # Find other wires connected to this wire's endpoints and trace them
    for wire_point in current_wire.points:
        for other_wire in schematic.wires:
            if other_wire.uuid == wire_uuid or other_wire.uuid in visited_uuids:
                continue
                
            # Check if other wire shares an endpoint with current wire
            for other_point in other_wire.points:
                if wire_point.x == other_point.x and wire_point.y == other_point.y:
                    if _trace_wire_network(schematic, other_wire, target_position, visited_uuids):
                        return True
    
    return False