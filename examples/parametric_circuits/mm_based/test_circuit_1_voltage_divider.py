#!/usr/bin/env python3
"""
Test Circuit 1: Voltage Divider - Parametric Version

DESIGN GUIDELINES FOR LLMs:
=========================

1. GRID ALIGNMENT (CRITICAL):
   - KiCAD schematics use a 1.27mm grid by default
   - All coordinates MUST be divisible by 1.27mm
   - Use snap_to_grid() helper function for all calculated coordinates
   - Common grid values: 0, 1.27, 2.54, 3.81, 5.08, 6.35, 7.62, 8.89, 10.16, ...

2. COORDINATE SYSTEM:
   - KiCAD schematics use INVERTED Y-axis (Y increases downward)
   - Lower Y values = visually HIGHER on screen
   - Higher Y values = visually LOWER on screen
   - Always snap Y coordinates to grid after any calculation

3. PARAMETRIC PLACEMENT:
   - Design circuits as reusable functions with (x_offset, y_offset) parameters
   - This allows circuits to be placed at any location without modification
   - Enables copy/paste of circuit blocks on large schematics

4. WIRE ROUTING:
   - Keep wires on grid - snap wire endpoints to grid values
   - Use small gaps (like 0.5mm) to avoid overlaps with component pins
   - Verify wires don't overlap with labels or rectangles

5. LABEL POSITIONING:
   - Place labels near their connected elements but with clearance
   - Avoid overlapping with wires, rectangles, or other labels
   - Use consistent spacing (e.g., GRID offset for nearby labels)

6. RECTANGLE GROUPING:
   - Use rectangles to group related circuit blocks visually
   - Keep rectangles aligned to grid
   - Leave adequate padding (e.g., GRID * 3) to avoid overlapping with content
"""

import kicad_sch_api as ksa

# ============================================================================
# GRID HELPER FUNCTION
# ============================================================================

def snap_to_grid(value: float, grid_size: float = 1.27) -> float:
    """
    Snap a coordinate value to the nearest grid point.

    KiCAD requires all schematic coordinates to be on the standard 1.27mm grid.
    This helper ensures coordinates stay on grid after calculations.

    Args:
        value: The coordinate value to snap
        grid_size: Grid size in mm (default 1.27mm = 50mil)

    Returns:
        The value snapped to the nearest grid point

    Example:
        snap_to_grid(3.8) -> 3.81 (nearest grid point)
        snap_to_grid(5.0) -> 5.08 (nearest grid point)
    """
    return round(value / grid_size) * grid_size


# ============================================================================
# PARAMETRIC CIRCUIT FUNCTION
# ============================================================================

def create_voltage_divider(sch, x_offset: float, y_offset: float, grid_size: float = 1.27, instance: int = 1):
    """
    Create a voltage divider circuit at a specific location.

    This is a PARAMETRIC CIRCUIT that can be placed at any location by changing
    x_offset and y_offset parameters. This enables circuit reuse and copying.

    Circuit Specifications:
    - Two 10k resistors in series
    - Creates 2.5V output from 5V input (50% divider)
    - Includes VCC, VOUT, and GND labels
    - Visual grouping rectangle
    - Formula annotation

    Args:
        sch: Schematic object to add circuit to
        x_offset: X position for circuit upper-left corner (mm) - rectangle start
        y_offset: Y position for circuit upper-left corner (mm) - rectangle start
        grid_size: Grid size to snap to (default 1.27mm)
        instance: Instance number for unique reference designators (default 1)
                 Use instance=2 for R21, R22; instance=3 for R31, R32, etc.

    Returns:
        Dictionary with references to created components {'R1': comp, 'R2': comp}
    """
    # Grid spacing constant
    GRID = 2.54  # 100mil = 2.54mm

    # Snap all input coordinates to grid (this is the rectangle upper-left corner)
    rect_x = snap_to_grid(x_offset, grid_size)
    rect_y = snap_to_grid(y_offset, grid_size)

    # Calculate component center position relative to rectangle upper-left
    # R1 is positioned 3 GRID units right and 5 GRID units down from rectangle corner
    x = snap_to_grid(rect_x + GRID * 3, grid_size)
    y = snap_to_grid(rect_y + GRID * 5, grid_size)

    # All derived coordinates are calculated and snapped to grid
    # This prevents floating-point errors and ensures grid alignment

    # Title position (centered above circuit)
    # Reference position from user's corrected schematic: (59.69, 44.196)
    title_x = snap_to_grid(x + GRID * 2.5, grid_size)  # Centered over circuit
    title_y = snap_to_grid(y - GRID * 4.1, grid_size)  # Above circuit

    # Component positions (snapped to grid)
    # R1 centered at (x, y)
    r1_x = snap_to_grid(x, grid_size)
    r1_y = snap_to_grid(y, grid_size)

    # R1 and R2 pin offsets from center (standard resistor is ±3.81mm from center)
    r1_pin1_y = snap_to_grid(r1_y - 3.81, grid_size)
    r1_pin2_y = snap_to_grid(r1_y + 3.81, grid_size)

    # R2 positioned below R1 with proper spacing
    r2_x = snap_to_grid(x, grid_size)
    r2_y = snap_to_grid(y + GRID * 4.5, grid_size)  # 11.43mm spacing to match reference

    r2_pin1_y = snap_to_grid(r2_y - 3.81, grid_size)
    r2_pin2_y = snap_to_grid(r2_y + 3.81, grid_size)

    # Junction point (VOUT node) between the two resistors
    junction_x = snap_to_grid(x, grid_size)
    junction_y = snap_to_grid(y + GRID * 2.5, grid_size)  # Midpoint between resistors

    # Label positions (snapped to grid)
    vcc_x = snap_to_grid(x, grid_size)
    vcc_y = snap_to_grid(r1_pin1_y - GRID, grid_size)

    vout_x = snap_to_grid(x + GRID * 2, grid_size)
    vout_y = snap_to_grid(junction_y, grid_size)

    gnd_x = snap_to_grid(x, grid_size)
    gnd_y = snap_to_grid(r2_pin2_y + GRID, grid_size)

    # Wire endpoints (snapped to grid)
    # Wire 1: VCC label to R1 top pin
    wire1_start_x = vcc_x
    wire1_start_y = vcc_y
    wire1_end_x = r1_x
    wire1_end_y = r1_pin1_y

    # Wire 2: R1 bottom pin to junction (VOUT node)
    wire2_start_x = r1_x
    wire2_start_y = r1_pin2_y
    wire2_end_x = junction_x
    wire2_end_y = junction_y

    # Wire 3: Junction to VOUT label (HORIZONTAL - important!)
    wire3_start_x = junction_x
    wire3_start_y = junction_y
    wire3_end_x = vout_x
    wire3_end_y = vout_y

    # Wire 4: Junction to R2 top pin
    wire4_start_x = junction_x
    wire4_start_y = junction_y
    wire4_end_x = r2_x
    wire4_end_y = r2_pin1_y

    # Wire 5: R2 bottom pin to GND label
    wire5_start_x = r2_x
    wire5_start_y = r2_pin2_y
    wire5_end_x = gnd_x
    wire5_end_y = gnd_y

    # Rectangle bounds (snapped to grid)
    # Rectangle starts at the reference point (upper-left corner)
    rect_start_x = rect_x
    rect_start_y = rect_y
    rect_end_x = snap_to_grid(rect_x + GRID * 11, grid_size)  # 11 GRID units wide
    rect_end_y = snap_to_grid(rect_y + GRID * 14, grid_size)  # 14 GRID units tall

    # Formula text position (snapped to grid)
    # Reference position from user's corrected schematic: (59.436, 75.692)
    formula_x = snap_to_grid(x + GRID * 2.4, grid_size)  # Centered below circuit
    formula_y = snap_to_grid(r2_pin2_y + GRID * 1.3, grid_size)  # Below GND

    # Generate unique reference designators based on instance number
    # instance=1: R1, R2 (standard simple naming)
    # instance=2: R21, R22 (numbered naming for multiple instances)
    # instance=3: R31, R32 (numbered naming for multiple instances)
    if instance == 1:
        ref_r1 = "R1"
        ref_r2 = "R2"
    else:
        ref_r1 = f"R{instance}1"
        ref_r2 = f"R{instance}2"

    # Create title
    # User customized in KiCAD: color=red (255,16,29), bold=yes, thickness=0.4
    # TODO: Add support for text color/bold/thickness in kicad-sch-api
    sch.add_text("VOLTAGE DIVIDER", position=(title_x, title_y), size=2.0)

    # Create components (positions already snapped to grid, references are unique)
    r1 = sch.components.add("Device:R", ref_r1, "10k", position=(r1_x, r1_y))
    r2 = sch.components.add("Device:R", ref_r2, "10k", position=(r2_x, r2_y))

    # Create labels (positions already snapped to grid)
    sch.add_label("VCC", position=(vcc_x, vcc_y))
    sch.add_label("VOUT", position=(vout_x, vout_y))
    sch.add_label("GND", position=(gnd_x, gnd_y))

    # Create junction at VOUT node (critical for proper circuit topology)
    sch.junctions.add(position=(junction_x, junction_y))

    # Create wires (all endpoints snapped to grid)
    # Wire 1: VCC label to R1 top
    sch.add_wire(start=(wire1_start_x, wire1_start_y), end=(wire1_end_x, wire1_end_y))

    # Wire 2: R1 bottom to junction (VOUT node)
    sch.add_wire(start=(wire2_start_x, wire2_start_y), end=(wire2_end_x, wire2_end_y))

    # Wire 3: Junction to VOUT label (HORIZONTAL - critical connection point)
    sch.add_wire(start=(wire3_start_x, wire3_start_y), end=(wire3_end_x, wire3_end_y))

    # Wire 4: Junction to R2 top
    sch.add_wire(start=(wire4_start_x, wire4_start_y), end=(wire4_end_x, wire4_end_y))

    # Wire 5: R2 bottom to GND label
    sch.add_wire(start=(wire5_start_x, wire5_start_y), end=(wire5_end_x, wire5_end_y))

    # Create formula annotation (position already snapped to grid)
    # User customized size to 1.0 in KiCAD (was 1.27)
    sch.add_text("Vout = 2.5V @ Vin=5V", position=(formula_x, formula_y), size=1.0)

    # Create visual grouping rectangle (bounds already snapped to grid)
    sch.add_rectangle(start=(rect_start_x, rect_start_y), end=(rect_end_x, rect_end_y))

    return {ref_r1: r1, ref_r2: r2}


# ============================================================================
# MAIN - DEMONSTRATE PARAMETRIC PLACEMENT
# ============================================================================

if __name__ == "__main__":
    print("🔧 Creating Circuit 1: Voltage Divider (Parametric Version)...")

    # Create schematic
    sch = ksa.create_schematic("Circuit_1_Voltage_Divider")

    # GRID-ALIGNED STARTING POSITION
    # Reference point is now the upper-left corner of the bounding rectangle
    # Rectangle upper-left: (45.72, 41.91)
    GRID_SIZE = 1.27
    START_X = 45.72  # Rectangle upper-left X (36 grid units: 36 * 1.27 = 45.72)
    START_Y = 41.91  # Rectangle upper-left Y (33 grid units: 33 * 1.27 = 41.91)

    print(f"📍 Circuit upper-left corner: ({START_X}, {START_Y}) [grid-aligned]")

    # Create voltage divider at the reference location for validation
    # This position matches the manually created reference schematic
    components = create_voltage_divider(sch, START_X, START_Y)

    print(f"✅ Created voltage divider at ({START_X}, {START_Y})")

    # EXAMPLE: Create additional circuit instances at different locations
    # Each position (x, y) is the upper-left corner of the bounding rectangle
    # create_voltage_divider(sch, START_X + 50, START_Y, instance=2)  # 50mm to the right
    # create_voltage_divider(sch, START_X, START_Y + 50, instance=3)  # 50mm down
    # create_voltage_divider(sch, START_X + 50, START_Y + 50, instance=4)  # 50mm diagonally

    # Save
    output_file = "test_circuit_1_voltage_divider.kicad_sch"
    sch.save(output_file)

    print(f"✅ Saved: {output_file}")
    print(f"📊 Components: {len(sch.components)}")
    print(f"📊 Wires: {len(sch.wires)}")
    print(f"📊 Labels: {len(sch.labels)}")
    print()
    print(f"Open in KiCAD: kicad {output_file}")
