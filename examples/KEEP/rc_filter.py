"""
kicad-sch-api Example: RC Low-Pass Filter

Demonstrates:
- Grid-based parametric circuit design
- Horizontal component rotation (90°)
- Pin position queries for rotated components
- Junction creation at signal tap point
- Text annotations with formulas

This is a basic 1kΩ/100nF RC low-pass filter with fc = 1.59 kHz.
"""

import kicad_sch_api as ksa
import math

# Enable grid units globally for cleaner parametric design
ksa.use_grid_units(True)


# ============================================================================
# RC LOW-PASS FILTER
# ============================================================================

def rc_filter(sch, x_grid, y_grid):
    """
    Create a parametric RC low-pass filter circuit.

    This function creates a complete RC filter that can be placed anywhere
    on the schematic by specifying grid coordinates. All internal positions are
    relative offsets from the origin point (x_grid, y_grid).

    Args:
        sch: Schematic object to add components to
        x_grid: X origin position in grid units (integer)
        y_grid: Y origin position in grid units (integer)

    Circuit: IN -> R (1k) -> OUT -> C (100nF) -> GND
    Cutoff Frequency: fc = 1/(2πRC) = 1.59 kHz
    """

    # Helper function for grid-relative positioning
    def p(dx, dy):
        """Position helper for parametric placement"""
        return (x_grid + dx, y_grid + dy)

    # Signal line Y position (horizontal path for IN → R → OUT)
    signal_y_offset = 5

    # ===== RESISTOR (HORIZONTAL) =====
    # Rotated 90° to align horizontally along signal line
    r = sch.components.add('Device:R', 'R1', '1k',
                          position=p(5, signal_y_offset),
                          rotation=90)

    # ===== CAPACITOR (VERTICAL) =====
    # Vertical orientation (default 0°)
    c = sch.components.add('Device:C', 'C1', '100nF',
                          position=p(9, signal_y_offset + 3))

    # ===== POWER SYMBOL =====
    sch.components.add('power:GND', '#PWR01', 'GND',
                      position=p(9, signal_y_offset + 5))

    # ===== JUNCTION =====
    # Junction at output node (where R, C, and OUT meet)
    junction_x = 9
    junction_y = signal_y_offset
    sch.junctions.add(position=p(junction_x, junction_y))

    # ===== LABELS =====
    sch.add_label('IN', position=p(2, signal_y_offset))
    sch.add_label('OUT', position=p(12, signal_y_offset))

    # ===== WIRING =====
    # Get pin positions (accounting for rotation)
    r_pins = sch.list_component_pins('R1')
    c_pins = sch.list_component_pins('C1')
    gnd_pins = sch.list_component_pins('#PWR01')

    # Determine left and right resistor pins (rotation affects order)
    r_pin1_pos = r_pins[0][1]
    r_pin2_pos = r_pins[1][1]

    if r_pin1_pos.x < r_pin2_pos.x:
        r_left_pin = r_pin1_pos
        r_right_pin = r_pin2_pos
    else:
        r_left_pin = r_pin2_pos
        r_right_pin = r_pin1_pos

    # Wire connections
    sch.add_wire(start=p(2, signal_y_offset), end=r_left_pin)
    sch.add_wire(start=r_right_pin, end=p(junction_x, junction_y))
    sch.add_wire(start=p(junction_x, junction_y), end=p(12, signal_y_offset))
    sch.add_wire(start=p(junction_x, junction_y), end=c_pins[0][1])
    sch.add_wire(start=c_pins[1][1], end=gnd_pins[0][1])

    # ===== ANNOTATIONS =====
    # Calculate cutoff frequency
    R = 1000  # 1kΩ
    C = 100e-9  # 100nF
    fc = 1 / (2 * math.pi * R * C)

    # Display cutoff frequency and formula
    sch.add_text(f"fc = {fc/1000:.2f} kHz", position=p(6, 14), size=1.27)
    sch.add_text("fc = 1/(2πRC)", position=p(6, 15), size=1.27)

    # ===== DECORATIVE ELEMENTS =====
    # Rectangle border for visual grouping
    sch.add_rectangle(start=p(-2, -2), end=p(16, 17))

    # Title text
    sch.add_text("RC Low-Pass Filter", position=p(3, 0), size=1.27)


def main():
    """Generate the RC filter example schematic."""
    print("Creating RC low-pass filter circuit...")

    # Create a new schematic
    sch = ksa.create_schematic("Example_RCFilter")

    # Place the RC filter at grid position (20, 20)
    # This positions the reference origin at (20, 20) and all other components
    # are placed relative to this origin point
    rc_filter(sch, 20, 20)

    # Save the schematic
    sch.save("rc_filter.kicad_sch")
    print("✅ Saved: rc_filter.kicad_sch")
    print()
    print("Open in KiCAD to see the result:")
    print("  open rc_filter.kicad_sch")


if __name__ == "__main__":
    main()
