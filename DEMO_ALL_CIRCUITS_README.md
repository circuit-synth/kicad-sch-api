# Complete Parametric Circuits Demo

## Overview

This demo showcases **three professional parametric circuits** combined into one comprehensive schematic, demonstrating the full capabilities of the `kicad-sch-api` library.

## Generated Files

- **`demo_all_circuits.py`** - Python script that generates the schematic
- **`demo_all_circuits.kicad_sch`** - Generated KiCAD schematic (29KB)
- Individual circuit modules:
  - `test_circuit_1_voltage_divider.py`
  - `test_circuit_2_power_supply.py`
  - `test_circuit_3_rc_filter.py`

## Circuits Included

### 1. Voltage Divider (Left)
- **Location**: (20, 20)mm
- **Components**: R1 (10kΩ), R2 (10kΩ)
- **Function**: Creates 2.5V output from 5V input
- **Formula**: Vout = Vin × R2/(R1+R2) = 2.5V
- **Use Case**: Reference voltage generation, signal attenuation

### 2. 5V Power Supply (Center)
- **Location**: (80, 20)mm
- **Components**:
  - U1 (LM7805 voltage regulator)
  - C1 (10µF input filter capacitor)
  - C2 (10µF output decoupling capacitor)
- **Input**: 7-35V DC
- **Output**: 5V @ 1.5A max
- **Dropout**: ~2V minimum
- **Use Case**: Converting unregulated DC to stable 5V supply

### 3. RC Low-Pass Filter (Right)
- **Location**: (140, 20)mm
- **Components**: R3 (1kΩ), C3 (100nF)
- **Cutoff Frequency**: fc = 1.59 kHz
- **Formula**: fc = 1/(2πRC)
- **Use Case**: Audio signal filtering, noise reduction

## Schematic Statistics

- **Total Components**: 13
  - Resistors: 3
  - Capacitors: 3
  - Voltage Regulators: 1
  - Power Symbols: 6 (VCC, VBUS, +5V, GND)
- **Wires**: 19
- **Labels**: 5 (VCC, VOUT, IN, OUT, GND)
- **Junctions**: 4
- **Rectangles**: 3 (visual grouping boxes)

## Key Features Demonstrated

### ✅ Parametric Circuit Design
Each circuit is a **reusable function** with position parameters:
```python
create_voltage_divider(sch, x_offset=20, y_offset=20, instance=1)
create_power_supply(sch, x_offset=80, y_offset=20, instance=1)
create_rc_filter(sch, x_offset=140, y_offset=20, instance=1)
```

### ✅ Grid-Aligned Placement
All components snap to KiCAD's **1.27mm (50 mil) grid**:
```python
def snap_to_grid(value: float, grid_size: float = 1.27) -> float:
    return round(value / grid_size) * grid_size
```

### ✅ Automatic Wire Routing
Uses `list_component_pins()` for accurate pin positions:
```python
r1_pins = sch.list_component_pins('R1')
r1_pin1 = r1_pins[0][1]  # Get (x, y) position
sch.add_wire(start=(vcc_x, vcc_y), end=r1_pin1)
```

### ✅ Power Symbol Management
Proper power rail naming:
- Input power: `VBUS` (unregulated)
- Regulated output: `+5V`
- Ground: `GND`
- Logic supply: `VCC`

### ✅ Visual Organization
- Grouping rectangles around each circuit
- Text annotations and formulas
- Consistent spacing and alignment

### ✅ Unique Reference Designators
Instance parameter allows multiple copies:
- Instance 1: R1, R2, U1, C1, C2, R3, C3
- Instance 2: R21, R22, U2, C21, C22, R23, C23
- etc.

## Layout Strategy

### Horizontal Layout (Row-Based)
```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ VOLTAGE DIVIDER │  │ 5V POWER SUPPLY │  │ RC LOW-PASS     │
│                 │  │                 │  │ FILTER          │
│   VCC           │  │  VBUS    +5V    │  │  IN        OUT  │
│    │            │  │   │       │     │  │   │         │   │
│   R1            │  │  C1  U1  C2     │  │   R3───┬───OUT  │
│    │            │  │       │         │  │        │        │
│   ├──VOUT       │  │      GND        │  │       C3        │
│    │            │  │                 │  │        │        │
│   R2            │  │                 │  │       GND       │
│    │            │  │                 │  │                 │
│   GND           │  │                 │  │  fc = 1.59 kHz  │
└─────────────────┘  └─────────────────┘  └─────────────────┘
  20mm spacing        60mm spacing         60mm spacing
```

### Circuit Spacing
- **Horizontal**: 60mm between circuit centers
- **Starting position**: (20, 20)mm from page origin
- **Total width**: ~200mm (fits on A4 landscape)

## Usage

### Generate Schematic
```bash
uv run python demo_all_circuits.py
```

### Open in KiCAD
```bash
open demo_all_circuits.kicad_sch
```

### Export to PDF
```bash
kicad-cli sch export pdf demo_all_circuits.kicad_sch
```

### Export Netlist
```bash
kicad-cli sch export netlist demo_all_circuits.kicad_sch
```

### Export BOM
```bash
kicad-cli sch export bom demo_all_circuits.kicad_sch
```

## Extending the Demo

### Add More Circuits

Add circuits to new rows:
```python
# Row 2: Add more circuits below
circuit4_x = START_X
circuit4_y = START_Y + CIRCUIT_GRID  # 60mm below row 1
create_led_circuit(sch, circuit4_x, circuit4_y, instance=1)
```

### Create Multiple Instances

Place duplicate circuits with unique references:
```python
# Create two voltage dividers
create_voltage_divider(sch, 20, 20, instance=1)   # R1, R2
create_voltage_divider(sch, 20, 80, instance=2)   # R21, R22
```

### Customize Values

Modify circuit parameters:
```python
# In create_rc_filter(), change:
r = sch.components.add("Device:R", r_ref, "10k", ...)  # 10kΩ instead of 1kΩ
c = sch.components.add("Device:C", c_ref, "10nF", ...)  # 10nF instead of 100nF
# Result: fc = 1.59 kHz × 10 = 15.9 kHz
```

## Technical Notes

### Y-Axis Inversion
KiCAD uses **inverted Y-axis** (Y increases downward):
- Lower Y values = visually HIGHER on screen (top)
- Higher Y values = visually LOWER on screen (bottom)

### Power Symbol Values
**CRITICAL**: Power symbols must use voltage string as value:
```python
# CORRECT ✅
sch.components.add("power:+5V", "#PWR01", value="+5V")

# WRONG ❌ (shows blank)
sch.components.add("power:+5V", "#PWR01", value="#PWR01")
```

### Junction Placement
Junctions required at T-connections (3+ wires meeting):
```python
sch.junctions.add(position=(junction_x, junction_y))
```

## Performance Metrics

- **Script execution time**: < 1 second
- **Schematic file size**: 29KB
- **Generation process**: Fully automated
- **Manual intervention**: None required
- **Reproducibility**: 100% (identical output every run)

## Real-World Applications

### Design Reuse
These parametric functions can be used in actual projects:
- Copy voltage divider function for ADC reference voltages
- Copy power supply function for multi-rail designs
- Copy RC filter for signal conditioning

### Rapid Prototyping
Generate variations quickly:
```python
# Test different cutoff frequencies
for fc_target in [1000, 5000, 10000]:  # Hz
    C = 100e-9  # 100nF
    R = 1 / (2 * math.pi * fc_target * C)
    create_rc_filter_custom(sch, x, y, R_value=R, C_value=C)
```

### Design Validation
Generated schematics can be:
- Imported into KiCAD for layout
- Simulated with SPICE
- Exported to Gerber files
- Manufactured directly

## Lessons Learned

1. **Grid alignment is critical** - All positions must be multiples of 1.27mm
2. **Pin position queries are essential** - Use `list_component_pins()` for wiring
3. **Parametric design enables reuse** - Functions can be called multiple times
4. **Power symbols need special handling** - Use voltage strings as values
5. **Visual organization matters** - Rectangles and spacing improve readability

## Next Steps

### Additional Circuits to Add
- Op-amp amplifier (non-inverting, inverting)
- Comparator with hysteresis
- LED indicator with current limiting
- Pull-up/pull-down resistors
- Crystal oscillator
- Button debounce circuit
- Level shifter
- Motor driver H-bridge

### Advanced Features
- Hierarchical sheets for complex designs
- Multi-page schematics
- Custom symbol libraries
- Automated testing with pytest
- CI/CD integration for schematic generation

## References

- **KiCAD Documentation**: https://docs.kicad.org/
- **kicad-sch-api GitHub**: https://github.com/circuit-synth/kicad-sch-api
- **Feature Branch**: `feature/issue-126-cli-setup`

---

**Generated**: November 7, 2025
**Script**: `demo_all_circuits.py`
**Output**: `demo_all_circuits.kicad_sch`
