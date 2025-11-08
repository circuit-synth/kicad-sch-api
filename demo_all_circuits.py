#!/usr/bin/env python3
"""
Complete Demo Schematic - All Parametric Circuits Combined

This demo combines all parametric circuit generators into one comprehensive schematic:
1. Voltage Divider (10k/10k) - 2.5V output
2. 5V Power Supply (LM7805) - regulated power
3. RC Low-Pass Filter (1kHz) - signal filtering

Each circuit is self-contained and reusable with x/y offset parameters.
"""

import kicad_sch_api as ksa


def snap_to_grid(value: float, grid_size: float = 1.27) -> float:
    """Snap a coordinate value to the nearest grid point."""
    return round(value / grid_size) * grid_size


# ============================================================================
# VOLTAGE DIVIDER CIRCUIT
# ============================================================================

def create_voltage_divider(sch, x_offset: float, y_offset: float, instance: int = 1):
    """Create a voltage divider circuit at specified location."""
    GRID = 2.54

    rect_x = snap_to_grid(x_offset)
    rect_y = snap_to_grid(y_offset)

    x = snap_to_grid(rect_x + GRID * 3)
    y = snap_to_grid(rect_y + GRID * 5)

    # Title
    title_x = snap_to_grid(x + GRID * 2.5)
    title_y = snap_to_grid(y - GRID * 4.1)
    sch.add_text("VOLTAGE DIVIDER", position=(title_x, title_y), size=2.0)

    # Generate unique references
    r1_ref = f"R{instance}1" if instance > 1 else "R1"
    r2_ref = f"R{instance}2" if instance > 1 else "R2"

    # R1 and R2 positions
    r1_x, r1_y = snap_to_grid(x), snap_to_grid(y)
    r2_x, r2_y = snap_to_grid(x), snap_to_grid(y + GRID * 4.5)

    # Components
    r1 = sch.components.add("Device:R", r1_ref, "10k", position=(r1_x, r1_y))
    r2 = sch.components.add("Device:R", r2_ref, "10k", position=(r2_x, r2_y))

    # Junction point between resistors
    junction_x = snap_to_grid(x)
    junction_y = snap_to_grid(y + GRID * 2.5)
    sch.junctions.add(position=(junction_x, junction_y))

    # Labels
    vcc_x, vcc_y = snap_to_grid(x), snap_to_grid(r1_y - GRID * 2)
    vout_x, vout_y = snap_to_grid(x + GRID * 2), snap_to_grid(junction_y)
    gnd_x, gnd_y = snap_to_grid(x), snap_to_grid(r2_y + GRID * 2)

    sch.add_label("VCC", position=(vcc_x, vcc_y))
    sch.add_label("VOUT", position=(vout_x, vout_y))
    sch.add_label("GND", position=(gnd_x, gnd_y))

    # Wires
    r1_pins = sch.list_component_pins(r1_ref)
    r2_pins = sch.list_component_pins(r2_ref)

    r1_pin1 = r1_pins[0][1]
    r1_pin2 = r1_pins[1][1]
    r2_pin1 = r2_pins[0][1]
    r2_pin2 = r2_pins[1][1]

    sch.add_wire(start=(vcc_x, vcc_y), end=r1_pin1)
    sch.add_wire(start=r1_pin2, end=(junction_x, junction_y))
    sch.add_wire(start=(junction_x, junction_y), end=r2_pin1)
    sch.add_wire(start=r2_pin2, end=(gnd_x, gnd_y))
    sch.add_wire(start=(junction_x, junction_y), end=(vout_x, vout_y))

    # Rectangle
    rect_end_x = snap_to_grid(rect_x + GRID * 12)
    rect_end_y = snap_to_grid(rect_y + GRID * 18)
    sch.add_rectangle(start=(rect_x, rect_y), end=(rect_end_x, rect_end_y))

    # Formula annotation - centered text box at bottom of rectangle
    text_box_x = snap_to_grid(rect_x + GRID * 1)
    text_box_y = snap_to_grid(rect_end_y - GRID * 3.5)
    text_box_width = snap_to_grid(GRID * 10)
    text_box_height = snap_to_grid(GRID * 3)

    formula_text = "Vout = Vin × R2/(R1+R2)\nVout = 2.5V @ Vin=5V"
    sch.add_text_box(
        formula_text,
        position=(text_box_x, text_box_y),
        size=(text_box_width, text_box_height),
        font_size=1.27
    )

    return {r1_ref: r1, r2_ref: r2}


# ============================================================================
# 5V POWER SUPPLY CIRCUIT
# ============================================================================

def create_power_supply(sch, x_offset: float, y_offset: float, instance: int = 1):
    """Create a 5V power supply circuit using LM7805."""
    GRID = 2.54

    rect_x = snap_to_grid(x_offset)
    rect_y = snap_to_grid(y_offset)

    u_x = snap_to_grid(rect_x + GRID * 10)
    u_y = snap_to_grid(rect_y + GRID * 5.7)

    # Generate unique references
    if instance == 1:
        u_ref, c_in_ref, c_out_ref = "U1", "C1", "C2"
        pwr_refs = ["#PWR01", "#PWR02", "#PWR03", "#PWR04", "#PWR05"]
    else:
        u_ref = f"U{instance}"
        c_in_ref = f"C{instance}1"
        c_out_ref = f"C{instance}2"
        pwr_refs = [f"#PWR{instance}01", f"#PWR{instance}02", f"#PWR{instance}03",
                    f"#PWR{instance}04", f"#PWR{instance}05"]

    # Title
    title_x = snap_to_grid(u_x)
    title_y = snap_to_grid(rect_y + GRID * 1.35)
    sch.add_text("5V POWER SUPPLY", position=(title_x, title_y), size=2.0)

    # Component positions
    c_in_x = snap_to_grid(u_x - GRID * 6.5)
    c_in_y = snap_to_grid(u_y + GRID * 1.5)
    c_out_x = snap_to_grid(u_x + GRID * 5.5)
    c_out_y = snap_to_grid(u_y + GRID * 1.5)

    # Components
    c_in = sch.components.add("Device:C_Polarized", c_in_ref, "10uF", position=(c_in_x, c_in_y))
    u = sch.components.add("Regulator_Linear:LM7805_TO220", u_ref, "LM7805", position=(u_x, u_y))
    c_out = sch.components.add("Device:C", c_out_ref, "10uF", position=(c_out_x, c_out_y))

    # Power symbols
    vbus_x, vbus_y = c_in_x, snap_to_grid(c_in_y - GRID * 2)
    v5_x, v5_y = c_out_x, snap_to_grid(c_out_y - GRID * 2)

    sch.components.add("power:VBUS", pwr_refs[0], "VBUS", position=(vbus_x, vbus_y))
    sch.components.add("power:+5V", pwr_refs[1], "+5V", position=(v5_x, v5_y))

    # Ground symbols
    gnd_c_in_y = snap_to_grid(c_in_y + GRID * 1.5)
    gnd_u_y = snap_to_grid(u_y + GRID * 3)
    gnd_c_out_y = snap_to_grid(c_out_y + GRID * 1.5)

    sch.components.add("power:GND", pwr_refs[2], "GND", position=(c_in_x, gnd_c_in_y))
    sch.components.add("power:GND", pwr_refs[3], "GND", position=(u_x, gnd_u_y))
    sch.components.add("power:GND", pwr_refs[4], "GND", position=(c_out_x, gnd_c_out_y))

    # Junctions
    junction_in_x = c_in_x
    junction_in_y = snap_to_grid(vbus_y + GRID * 0.5)
    junction_out_x = c_out_x
    junction_out_y = snap_to_grid(v5_y + GRID * 0.5)

    sch.junctions.add(position=(junction_in_x, junction_in_y))
    sch.junctions.add(position=(junction_out_x, junction_out_y))

    # Get pin positions
    u_pins = sch.list_component_pins(u_ref)
    c_in_pins = sch.list_component_pins(c_in_ref)
    c_out_pins = sch.list_component_pins(c_out_ref)
    vbus_pins = sch.list_component_pins(pwr_refs[0])
    v5_pins = sch.list_component_pins(pwr_refs[1])
    gnd_in_pins = sch.list_component_pins(pwr_refs[2])
    gnd_u_pins = sch.list_component_pins(pwr_refs[3])
    gnd_out_pins = sch.list_component_pins(pwr_refs[4])

    # Wires - Input rail
    sch.add_wire(start=vbus_pins[0][1], end=(junction_in_x, junction_in_y))
    sch.add_wire(start=(junction_in_x, junction_in_y), end=c_in_pins[0][1])
    sch.add_wire(start=(junction_in_x, junction_in_y), end=u_pins[0][1])

    # Wires - Output rail
    sch.add_wire(start=u_pins[2][1], end=(junction_out_x, junction_out_y))
    sch.add_wire(start=(junction_out_x, junction_out_y), end=c_out_pins[0][1])
    sch.add_wire(start=(junction_out_x, junction_out_y), end=v5_pins[0][1])

    # Wires - Ground
    sch.add_wire(start=c_in_pins[1][1], end=gnd_in_pins[0][1])
    sch.add_wire(start=u_pins[1][1], end=gnd_u_pins[0][1])
    sch.add_wire(start=c_out_pins[1][1], end=gnd_out_pins[0][1])

    # Rectangle
    rect_end_x = snap_to_grid(rect_x + GRID * 20.5)
    rect_end_y = snap_to_grid(rect_y + GRID * 17)
    sch.add_rectangle(start=(rect_x, rect_y), end=(rect_end_x, rect_end_y))

    # Text box with specs - positioned up and to the right
    text_box_x = snap_to_grid(rect_x + GRID * 11)
    text_box_y = snap_to_grid(rect_end_y - GRID * 4.5)
    text_box_width = snap_to_grid(GRID * 8.5)
    text_box_height = snap_to_grid(GRID * 4)

    specs_text = "Input: 7-35V DC\nOutput: 5V @ 1.5A max\nDropout: ~2V min"
    sch.add_text_box(
        specs_text,
        position=(text_box_x, text_box_y),
        size=(text_box_width, text_box_height),
        font_size=1.27
    )

    return {u_ref: u, c_in_ref: c_in, c_out_ref: c_out}


# ============================================================================
# RC LOW-PASS FILTER CIRCUIT
# ============================================================================

def create_rc_filter(sch, x_offset: float, y_offset: float, instance: int = 1):
    """Create an RC low-pass filter circuit."""
    import math

    GRID = 2.54

    rect_x = snap_to_grid(x_offset)
    rect_y = snap_to_grid(y_offset)

    # Generate unique references
    if instance == 1:
        r_ref, c_ref = "R3", "C3"
        pwr_ref = "#PWR06"
    else:
        r_ref = f"R{instance}3"
        c_ref = f"C{instance}3"
        pwr_ref = f"#PWR{instance}06"

    # Title
    title_x = snap_to_grid(rect_x + GRID * 7.75)
    title_y = snap_to_grid(rect_y + GRID * 2.1)
    sch.add_text("RC LOW-PASS FILTER", position=(title_x, title_y), size=2.0)

    # Signal line Y position (horizontal path for IN → R → OUT)
    signal_y = snap_to_grid(rect_y + GRID * 6.5)

    # Resistor position (horizontal, centered on signal line)
    r_x = snap_to_grid(rect_x + GRID * 6.5)
    r_y = signal_y

    # Capacitor position (vertical, output side)
    c_x = snap_to_grid(rect_x + GRID * 10.5)
    c_y = snap_to_grid(signal_y + GRID * 3.5)

    # Junction point (where R pin 2, C pin 1, and OUT meet)
    junction_x = c_x
    junction_y = signal_y

    # Components
    r = sch.components.add("Device:R", r_ref, "1k", position=(r_x, r_y), rotation=90)  # Horizontal (90° in KiCAD)
    c = sch.components.add("Device:C", c_ref, "100nF", position=(c_x, c_y))

    # GND power symbol
    gnd_x = c_x
    gnd_y = snap_to_grid(c_y + GRID * 1.5)
    sch.components.add("power:GND", pwr_ref, "GND", position=(gnd_x, gnd_y))

    # Labels (on signal line)
    in_label_x = snap_to_grid(rect_x + GRID * 3)
    in_label_y = signal_y
    out_label_x = snap_to_grid(rect_x + GRID * 13)
    out_label_y = signal_y

    sch.add_label("IN", position=(in_label_x, in_label_y))
    sch.add_label("OUT", position=(out_label_x, out_label_y))

    # Junction at output node
    sch.junctions.add(position=(junction_x, junction_y))

    # Get pin positions
    r_pins = sch.list_component_pins(r_ref)
    c_pins = sch.list_component_pins(c_ref)
    gnd_pins = sch.list_component_pins(pwr_ref)

    # Determine left and right pins based on X position (rotation affects pin order)
    r_pin1_pos = r_pins[0][1]  # Point object
    r_pin2_pos = r_pins[1][1]  # Point object

    # Left pin is the one with smaller X coordinate
    if r_pin1_pos.x < r_pin2_pos.x:
        r_left_pin = r_pin1_pos
        r_right_pin = r_pin2_pos
    else:
        r_left_pin = r_pin2_pos
        r_right_pin = r_pin1_pos

    # Wires
    # IN label to R left pin
    sch.add_wire(start=(in_label_x, in_label_y), end=r_left_pin)
    # R right pin to junction
    sch.add_wire(start=r_right_pin, end=(junction_x, junction_y))
    # Junction to OUT label
    sch.add_wire(start=(junction_x, junction_y), end=(out_label_x, out_label_y))
    # Junction down to C pin 1
    sch.add_wire(start=(junction_x, junction_y), end=c_pins[0][1])
    # C pin 2 to GND
    sch.add_wire(start=c_pins[1][1], end=gnd_pins[0][1])

    # Calculate and display cutoff frequency
    R = 1000  # 1kΩ
    C = 100e-9  # 100nF
    fc = 1 / (2 * math.pi * R * C)

    fc_text_x = snap_to_grid(rect_x + GRID * 6.7)
    fc_text_y = snap_to_grid(rect_y + GRID * 16.5)
    formula_x = snap_to_grid(rect_x + GRID * 6.7)
    formula_y = snap_to_grid(rect_y + GRID * 18)

    sch.add_text(f"fc = {fc/1000:.2f} kHz", position=(fc_text_x, fc_text_y), size=1.27)
    sch.add_text("fc = 1/(2πRC)", position=(formula_x, formula_y), size=1.27)

    # Rectangle
    rect_end_x = snap_to_grid(rect_x + GRID * 17)
    rect_end_y = snap_to_grid(rect_y + GRID * 19.5)
    sch.add_rectangle(start=(rect_x, rect_y), end=(rect_end_x, rect_end_y))

    return {r_ref: r, c_ref: c}


# ============================================================================
# MAIN - CREATE COMBINED DEMO SCHEMATIC
# ============================================================================

def main():
    print("=" * 80)
    print("🚀 COMPREHENSIVE DEMO - All Parametric Circuits Combined")
    print("=" * 80)
    print()

    # Create schematic
    sch = ksa.create_schematic("Demo_All_Circuits")

    # A4 landscape layout - place circuits in a grid
    # Grid spacing for circuit placement
    CIRCUIT_GRID = 60  # 60mm between circuit centers

    # Starting position (upper left)
    START_X = 20
    START_Y = 20

    print("📍 Circuit Placement Layout:")
    print("  Row 1: Voltage Divider | Power Supply | RC Filter")
    print()

    # Row 1: Three circuits side by side
    print("🔧 Circuit 1: Voltage Divider...")
    circuit1_x = START_X
    circuit1_y = START_Y
    create_voltage_divider(sch, circuit1_x, circuit1_y, instance=1)
    print(f"  ✅ Placed at ({circuit1_x}, {circuit1_y})")

    print("🔧 Circuit 2: 5V Power Supply (LM7805)...")
    circuit2_x = START_X + CIRCUIT_GRID
    circuit2_y = START_Y
    create_power_supply(sch, circuit2_x, circuit2_y, instance=1)
    print(f"  ✅ Placed at ({circuit2_x}, {circuit2_y})")

    print("🔧 Circuit 3: RC Low-Pass Filter...")
    circuit3_x = START_X + CIRCUIT_GRID * 2
    circuit3_y = START_Y
    create_rc_filter(sch, circuit3_x, circuit3_y, instance=1)
    print(f"  ✅ Placed at ({circuit3_x}, {circuit3_y})")

    print()
    print("=" * 80)
    print("📊 Schematic Statistics:")
    print("=" * 80)

    # Count components
    resistors = len([c for c in sch.components if 'Device:R' in c.lib_id])
    capacitors = len([c for c in sch.components if 'Device:C' in c.lib_id or 'C_Polarized' in c.lib_id])
    regulators = len([c for c in sch.components if 'Regulator' in c.lib_id])
    power_symbols = len([c for c in sch.components if c.reference.startswith('#PWR')])

    print(f"  • Total Components: {len(sch.components)}")
    print(f"    - Resistors: {resistors}")
    print(f"    - Capacitors: {capacitors}")
    print(f"    - Voltage Regulators: {regulators}")
    print(f"    - Power Symbols: {power_symbols}")
    print(f"  • Wires: {len(sch.wires)}")
    print(f"  • Labels: {len(sch.labels)}")
    print(f"  • Junctions: {len(sch.junctions)}")
    print(f"  • Rectangles: 3 (grouping boxes)")
    print()

    # Save
    output_file = "demo_all_circuits.kicad_sch"
    print(f"💾 Saving schematic to: {output_file}")
    sch.save(output_file)
    print(f"✅ Saved successfully!")
    print()

    print("=" * 80)
    print("🎉 DEMO COMPLETE!")
    print("=" * 80)
    print()
    print("Circuits Included:")
    print("  1. ⚡ Voltage Divider - 10kΩ/10kΩ resistive divider (Vout = Vin/2)")
    print("  2. 🔌 5V Power Supply - LM7805 linear regulator with filter caps")
    print("  3. 📊 RC Low-Pass Filter - 1kΩ/100nF filter (fc = 1.59 kHz)")
    print()
    print("Features Demonstrated:")
    print("  ✅ Parametric circuit functions (reusable at any position)")
    print("  ✅ Grid-aligned component placement (1.27mm grid)")
    print("  ✅ Automatic wire routing with pin position queries")
    print("  ✅ Power symbols and ground connections")
    print("  ✅ Net labels for signal identification")
    print("  ✅ Junctions at connection points")
    print("  ✅ Grouping rectangles for visual organization")
    print("  ✅ Text annotations and formulas")
    print("  ✅ Unique reference designators per circuit")
    print()
    print("Open in KiCAD:")
    print(f"  open {output_file}")
    print()
    print("Generate PDF:")
    print(f"  kicad-cli sch export pdf {output_file}")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
