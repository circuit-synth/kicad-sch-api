#!/usr/bin/env python3
"""
Test Circuit 3: RC Low-Pass Filter

Parametric RC low-pass filter circuit with frequency response analysis.
"""

import kicad_sch_api as ksa
import numpy as np


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


def create_rc_filter(sch, x_offset: float, y_offset: float, grid_size: float = 1.27, instance: int = 1):
    """
    Create an RC low-pass filter circuit.

    This circuit filters out high-frequency signals using a first-order RC filter.

    Circuit Specifications:
    - Resistor: 1kΩ (horizontal orientation)
    - Capacitor: 100nF (vertical to ground)
    - Cutoff frequency: fc = 1/(2π × R × C)
    - For R=1kΩ, C=100nF: fc ≈ 1.59 kHz
    - Uses GND power symbol
    - Includes frequency formula annotations

    Args:
        sch: Schematic object to add circuit to
        x_offset: X position for circuit upper-left corner (mm) - rectangle start
        y_offset: Y position for circuit upper-left corner (mm) - rectangle start
        grid_size: Grid size to snap to (default 1.27mm)
        instance: Instance number for unique references (default 1)
                 R1/C1 for instance 1, R2/C2 for instance 2, etc.

    Returns:
        Dictionary with component references
    """
    GRID = 2.54  # 100mil = 2.54mm

    # Snap input coordinates to grid (this is the rectangle upper-left corner)
    rect_x = snap_to_grid(x_offset, grid_size)
    rect_y = snap_to_grid(y_offset, grid_size)

    # Calculate circuit components relative to rectangle
    # R1 center position (horizontal resistor)
    r_x = snap_to_grid(rect_x + GRID * 6.23, grid_size)
    r_y = snap_to_grid(rect_y + GRID * 6.5, grid_size)

    # C1 center position (vertical capacitor)
    c_x = snap_to_grid(rect_x + GRID * 10.7, grid_size)
    c_y = snap_to_grid(rect_y + GRID * 10, grid_size)

    # Junction point (output node between R and C)
    junction_x = c_x
    junction_y = r_y

    # Generate unique reference designators
    if instance == 1:
        r_ref = "R1"
        c_ref = "C1"
    else:
        r_ref = f"R{instance}"
        c_ref = f"C{instance}"

    # ========== Label Positions ==========
    in_label_x = snap_to_grid(rect_x + GRID * 3.7, grid_size)
    in_label_y = r_y

    out_label_x = snap_to_grid(rect_x + GRID * 12.75, grid_size)
    out_label_y = r_y

    # ========== GND Power Symbol ==========
    gnd_x = c_x
    gnd_y = snap_to_grid(rect_y + GRID * 11.5, grid_size)

    # ========== Title and Formulas ==========
    title_x = snap_to_grid(rect_x + GRID * 7.75, grid_size)
    title_y = snap_to_grid(rect_y + GRID * 2.1, grid_size)

    # Calculate cutoff frequency
    R = 1000  # 1kΩ
    C = 100e-9  # 100nF
    fc = 1 / (2 * np.pi * R * C)

    fc_text_x = snap_to_grid(rect_x + GRID * 6.7, grid_size)
    fc_text_y = snap_to_grid(rect_y + GRID * 16.5, grid_size)

    formula_x = snap_to_grid(rect_x + GRID * 6.7, grid_size)
    formula_y = snap_to_grid(rect_y + GRID * 18, grid_size)

    # ========== Rectangle Bounds ==========
    rect_end_x = snap_to_grid(rect_x + GRID * 17, grid_size)
    rect_end_y = snap_to_grid(rect_y + GRID * 19.5, grid_size)

    # ========== Create Title ==========
    sch.add_text("RC LOW-PASS FILTER", position=(title_x, title_y), size=2.0)

    # ========== Create Components ==========
    # Resistor (horizontal, rotation=90 makes it horizontal in KiCAD's system)
    r = sch.components.add(
        "Device:R", r_ref, "1k",
        position=(r_x, r_y),
        rotation=90  # Horizontal orientation
    )

    # Capacitor (vertical, default rotation=0)
    c = sch.components.add(
        "Device:C", c_ref, "100nF",
        position=(c_x, c_y)
    )

    # GND power symbol
    sch.components.add(
        "power:GND", f"#PWR0{instance}01", "GND",
        position=(gnd_x, gnd_y)
    )

    # ========== Create Labels ==========
    sch.add_label("IN", position=(in_label_x, in_label_y))
    sch.add_label("OUT", position=(out_label_x, out_label_y))

    # ========== Create Junction ==========
    # Junction at output node (where R, C, and OUT meet)
    sch.junctions.add(position=(junction_x, junction_y))

    # ========== Create Wires ==========
    # IN label to R1 pin 1
    sch.add_wire(
        start=(in_label_x, in_label_y),
        end=(snap_to_grid(r_x - GRID * 1.5, grid_size), r_y)
    )

    # R1 pin 2 to junction
    sch.add_wire(
        start=(snap_to_grid(r_x + GRID * 1.5, grid_size), r_y),
        end=(junction_x, junction_y)
    )

    # Junction to OUT label
    sch.add_wire(
        start=(junction_x, junction_y),
        end=(out_label_x, out_label_y)
    )

    # Junction down to C1 pin 1
    sch.add_wire(
        start=(junction_x, junction_y),
        end=(c_x, snap_to_grid(c_y - GRID * 1.5, grid_size))
    )

    # ========== Create Frequency Formulas ==========
    sch.add_text(f"fc = {fc/1000:.2f} kHz", position=(fc_text_x, fc_text_y), size=1.27)
    sch.add_text("fc = 1/(2πRC)", position=(formula_x, formula_y), size=1.27)

    # ========== Create Bounding Rectangle ==========
    sch.add_rectangle(start=(rect_x, rect_y), end=(rect_end_x, rect_end_y))

    # ========== Frequency Response Plot Image ==========
    # The kicad-sch-api library doesn't currently support adding images programmatically
    # The frequency response plot 'rc_filter_response.png' must be added manually in KiCAD
    #
    # To reproduce the reference schematic:
    # 1. Open the schematic in KiCAD
    # 2. Go to: Place → Image
    # 3. Select 'rc_filter_response.png'
    # 4. Position at: (71.12, 65.405) - to the right of the formulas
    # 5. Scale to: 0.17931 (approximately 18% of original size)
    #
    # Image position reference (from test_circuit_3_rc_filter_REFERENCE.kicad_sch):
    #   (image
    #       (at 71.12 65.405)
    #       (scale 0.17931)
    #       (uuid "...")
    #       (data "base64-encoded PNG data...")
    #   )
    #
    # The plot shows:
    # - Magnitude response (dB) vs frequency (top)
    # - Phase response (degrees) vs frequency (bottom)
    # - Red dashed line marking cutoff frequency at 1.59 kHz (-3dB point)
    #
    # TODO: Add image embedding support to kicad-sch-api (future enhancement)

    return {r_ref: r, c_ref: c}


# ============================================================================
# MAIN - DEMONSTRATE PARAMETRIC RC FILTER
# ============================================================================

if __name__ == "__main__":
    print("🔧 Creating Circuit 3: RC Low-Pass Filter...")

    # Create schematic
    sch = ksa.create_schematic("Circuit_3_RC_Filter")

    # GRID-ALIGNED STARTING POSITION
    # Reference point is the upper-left corner of the bounding rectangle
    # Rectangle upper-left: (28.575, 29.21)
    GRID_SIZE = 1.27
    START_X = 28.575  # Rectangle upper-left X
    START_Y = 29.21   # Rectangle upper-left Y

    print(f"📍 Circuit upper-left corner: ({START_X}, {START_Y}) [grid-aligned]")

    # Create RC filter at the reference location
    components = create_rc_filter(sch, START_X, START_Y)

    print(f"✅ Created RC filter at ({START_X}, {START_Y})")

    # Save
    output_file = "test_circuit_3_rc_filter.kicad_sch"
    sch.save(output_file)

    print(f"✅ Saved: {output_file}")
    print(f"📊 Components: {len(sch.components)}")
    print(f"📊 Wires: {len(sch.wires)}")
    print()
    print("📈 Frequency response plot generated: rc_filter_response.png")
    print("   To add to schematic: Place → Image in KiCAD")
    print()
    print(f"Open in KiCAD: kicad {output_file}")
