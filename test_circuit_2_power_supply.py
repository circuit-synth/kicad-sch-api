#!/usr/bin/env python3
"""
Test Circuit 2: 5V Power Supply (LM7805)

Parametric power supply circuit using LM7805 voltage regulator.
"""

import kicad_sch_api as ksa


def snap_to_grid(value: float, grid_size: float = 1.27) -> float:
    """
    Snap a coordinate value to the nearest grid point.

    Args:
        value: The coordinate value to snap
        grid_size: Grid size in mm (default 1.27mm = 50mil)

    Returns:
        The value snapped to the nearest grid point
    """
    return round(value / grid_size) * grid_size


def create_power_supply(sch, x_offset: float, y_offset: float, grid_size: float = 1.27, instance: int = 1):
    """
    Create a 5V linear power supply circuit using LM7805 regulator.

    This circuit converts unregulated input voltage (7-35V) to regulated 5V output.

    Circuit Specifications:
    - Input: 7-35V (typically 9V)
    - Output: 5V @ 1.5A max
    - Input filter capacitor: 10µF electrolytic
    - Output decoupling capacitor: 100nF ceramic
    - Regulator: LM7805 (TO-220 package)
    - Uses power symbols: VBUS (input), +5V (output), GND (ground)
    - Text box with specifications

    Args:
        sch: Schematic object to add circuit to
        x_offset: X position for circuit upper-left corner (mm) - rectangle start
        y_offset: Y position for circuit upper-left corner (mm) - rectangle start
        grid_size: Grid size to snap to (default 1.27mm)
        instance: Instance number for unique references (default 1)
                 U1/C11/C12 for instance 1, U2/C21/C22 for instance 2, etc.

    Returns:
        Dictionary with component references
    """
    GRID = 2.54  # 100mil = 2.54mm

    # Snap input coordinates to grid (this is the rectangle upper-left corner)
    rect_x = snap_to_grid(x_offset, grid_size)
    rect_y = snap_to_grid(y_offset, grid_size)

    # Calculate component center position relative to rectangle upper-left
    # U1 (center component) positioned to center the horizontal layout
    u_x = snap_to_grid(rect_x + GRID * 10, grid_size)
    u_y = snap_to_grid(rect_y + GRID * 5.7, grid_size)

    # Generate unique reference designators
    if instance == 1:
        u_ref = "U1"
        c_in_ref = "C11"
        c_out_ref = "C12"
    else:
        u_ref = f"U{instance}"
        c_in_ref = f"C{instance}1"
        c_out_ref = f"C{instance}2"

    # ========== Component Positions (relative to U1 center) ==========
    # C11: Input capacitor (left of U1)
    c_in_x = snap_to_grid(u_x - GRID * 6.5, grid_size)
    c_in_y = snap_to_grid(u_y + GRID * 1.5, grid_size)

    # C12: Output capacitor (right of U1)
    c_out_x = snap_to_grid(u_x + GRID * 5.5, grid_size)
    c_out_y = snap_to_grid(u_y + GRID * 1.5, grid_size)

    # ========== Power Symbol Positions ==========
    # VBUS: Input power (above C11)
    vbus_x = c_in_x
    vbus_y = snap_to_grid(c_in_y - GRID * 2, grid_size)

    # +5V: Output power (above C12)
    v5_x = c_out_x
    v5_y = snap_to_grid(c_out_y - GRID * 2, grid_size)

    # GND: Ground symbols (below components)
    gnd_c_in_y = snap_to_grid(c_in_y + GRID * 1.5, grid_size)
    gnd_u_y = snap_to_grid(u_y + GRID * 3, grid_size)
    gnd_c_out_y = snap_to_grid(c_out_y + GRID * 1.5, grid_size)

    # ========== Junction Positions (power rails) ==========
    junction_in_x = c_in_x
    junction_in_y = snap_to_grid(vbus_y + GRID * 0.5, grid_size)

    junction_out_x = c_out_x
    junction_out_y = snap_to_grid(v5_y + GRID * 0.5, grid_size)

    # ========== Title and Text Box ==========
    # Title centered on U1
    title_x = snap_to_grid(u_x, grid_size)
    title_y = snap_to_grid(rect_y + GRID * 1.35, grid_size)

    # Text box with specifications (below circuit, centered)
    text_box_x = snap_to_grid(rect_x + GRID * 8.5, grid_size)  # More to the right
    text_box_y = snap_to_grid(rect_y + GRID * 14.3, grid_size)  # Barely above lower edge
    text_box_width = snap_to_grid(GRID * 8.25, grid_size)
    text_box_height = snap_to_grid(GRID * 4.25, grid_size)

    # ========== Rectangle Bounds ==========
    # Note: To move bottom edge up, decrease rect_end_y (Y increases downward)
    rect_end_x = snap_to_grid(rect_x + GRID * 20.5, grid_size)
    rect_end_y = snap_to_grid(rect_y + GRID * 17, grid_size)  # Shrunk and moved up

    # ========== Create Title ==========
    sch.add_text("5V POWER SUPPLY", position=(title_x, title_y), size=2.0)

    # ========== Create Components ==========
    # Input filter capacitor (polarized)
    c_in = sch.components.add(
        "Device:C_Polarized", c_in_ref, "10uF",
        position=(c_in_x, c_in_y)
    )

    # Voltage regulator
    u = sch.components.add(
        "Regulator_Linear:LM7805_TO220", u_ref, "LM7805",
        position=(u_x, u_y)
    )

    # Output decoupling capacitor (unpolarized)
    c_out = sch.components.add(
        "Device:C", c_out_ref, "10uF",
        position=(c_out_x, c_out_y)
    )

    # ========== Create Power Symbols ==========
    # Input power (VBUS)
    sch.components.add(
        "power:VBUS", f"#PWR0{instance}01", "VBUS",
        position=(vbus_x, vbus_y)
    )

    # Output power (+5V)
    sch.components.add(
        "power:+5V", f"#PWR0{instance}02", "+5V",
        position=(v5_x, v5_y)
    )

    # Ground symbols (3 total)
    sch.components.add(
        "power:GND", f"#PWR0{instance}03", "GND",
        position=(c_in_x, gnd_c_in_y)
    )
    sch.components.add(
        "power:GND", f"#PWR0{instance}04", "GND",
        position=(u_x, gnd_u_y)
    )
    sch.components.add(
        "power:GND", f"#PWR0{instance}05", "GND",
        position=(c_out_x, gnd_c_out_y)
    )

    # ========== Create Junctions ==========
    sch.junctions.add(position=(junction_in_x, junction_in_y))
    sch.junctions.add(position=(junction_out_x, junction_out_y))

    # ========== Create Wires ==========
    # Input rail: VBUS → junction → C11
    sch.add_wire(
        start=(vbus_x, vbus_y),
        end=(junction_in_x, junction_in_y)
    )
    sch.add_wire(
        start=(junction_in_x, junction_in_y),
        end=(c_in_x, snap_to_grid(c_in_y - GRID * 1.5, grid_size))
    )

    # Input to U1: junction → U1 input
    sch.add_wire(
        start=(junction_in_x, junction_in_y),
        end=(snap_to_grid(u_x - GRID * 3, grid_size), u_y)
    )

    # Output from U1: U1 output → junction
    sch.add_wire(
        start=(snap_to_grid(u_x + GRID * 3, grid_size), u_y),
        end=(junction_out_x, junction_out_y)
    )

    # Output rail: junction → C12 → +5V
    sch.add_wire(
        start=(junction_out_x, junction_out_y),
        end=(c_out_x, snap_to_grid(c_out_y - GRID * 1.5, grid_size))
    )
    sch.add_wire(
        start=(junction_out_x, junction_out_y),
        end=(v5_x, v5_y)
    )

    # ========== Create Text Box with Specifications ==========
    # Note: text_box is not yet supported in kicad-sch-api, using regular text as workaround
    # TODO: Add text_box support to kicad-sch-api (issue to be created)
    sch.add_text(
        "Input: 7-35V\n\nOutput: 5V @ 1.5A",
        position=(text_box_x, text_box_y),
        size=1.27
    )

    # ========== Create Bounding Rectangle ==========
    sch.add_rectangle(start=(rect_x, rect_y), end=(rect_end_x, rect_end_y))

    return {
        u_ref: u,
        c_in_ref: c_in,
        c_out_ref: c_out
    }


# ============================================================================
# MAIN - DEMONSTRATE PARAMETRIC POWER SUPPLY
# ============================================================================

if __name__ == "__main__":
    print("🔧 Creating Circuit 2: 5V Power Supply (LM7805)...")

    # Create schematic
    sch = ksa.create_schematic("Circuit_2_Power_Supply")

    # GRID-ALIGNED STARTING POSITION
    # Reference point is the upper-left corner of the bounding rectangle
    # Rectangle upper-left: (33.655, 38.735)
    GRID_SIZE = 1.27
    START_X = 33.655  # Rectangle upper-left X
    START_Y = 38.735  # Rectangle upper-left Y

    print(f"📍 Circuit upper-left corner: ({START_X}, {START_Y}) [grid-aligned]")

    # Create power supply at the reference location
    components = create_power_supply(sch, START_X, START_Y)

    print(f"✅ Created power supply at ({START_X}, {START_Y})")

    # Save
    output_file = "test_circuit_2_power_supply.kicad_sch"
    sch.save(output_file)

    print(f"✅ Saved: {output_file}")
    print(f"📊 Components: {len(sch.components)}")
    print(f"📊 Wires: {len(sch.wires)}")
    print()
    print(f"Open in KiCAD: kicad {output_file}")
