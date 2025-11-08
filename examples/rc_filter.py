"""
kicad-sch-api Example: RC Low-Pass Filter

Demonstrates:
- Grid-based parametric circuit design
- Component placement with p() helper
- Auto-routing between component pins
- Text annotations

This is a basic 1kΩ/100nF RC low-pass filter with fc = 1.59 kHz.
"""

import kicad_sch_api as ksa

# Enable grid units globally for cleaner parametric design
ksa.use_grid_units(True)


# ============================================================================
# RC LOW-PASS FILTER
# ============================================================================

def rc_filter(sch, x_grid, y_grid):
    """
    Create a parametric RC low-pass filter circuit.

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

    # ===== COMPONENTS =====
    sch.components.add('Device:R', 'R1', '1k', position=p(5, 5))
    sch.components.add('Device:C', 'C1', '100nF', position=p(5, 12))
    sch.components.add('power:GND', '#PWR01', 'GND', position=p(5, 16))

    # ===== JUNCTION =====
    sch.junctions.add(position=p(5, 9))

    # ===== LABELS =====
    sch.add_label('IN', position=p(5, 1))
    sch.add_label('OUT', position=p(9, 9))

    # ===== WIRING =====
    # Manual wiring for power
    sch.add_wire(start=p(5, 1), end=p(5, 2))      # IN to R1 pin 1
    sch.add_wire(start=p(5, 15), end=p(5, 16))    # C1 pin 2 to GND

    # Auto-route between components
    sch.auto_route_pins('R1', '2', 'C1', '1', routing_strategy='direct')

    # Horizontal tap to OUT label
    sch.add_wire(start=p(5, 9), end=p(9, 9))

    # ===== DECORATIVE ELEMENTS =====
    sch.add_rectangle(start=p(-3, -4), end=p(14, 23))
    sch.add_text("RC Filter", position=p(3, -2), size=1.27)


def main():
    """Generate the RC filter example schematic."""
    print("Creating RC low-pass filter circuit...")

    # Create a new schematic
    sch = ksa.create_schematic("Example_RCFilter")

    # Place the RC filter at grid position (20, 20)
    rc_filter(sch, 20, 20)

    # Save the schematic
    sch.save("rc_filter.kicad_sch")
    print("✅ Saved: rc_filter.kicad_sch")
    print()
    print("Open in KiCAD to see the result:")
    print("  open rc_filter.kicad_sch")


if __name__ == "__main__":
    main()
