---
name: create-schematic
description: Create a KiCAD schematic from a description
---

# Create Schematic Command

Generate a complete KiCAD schematic file from a natural language description using kicad-sch-api.

## Usage

```bash
/create-schematic <description>
```

## Examples

```bash
# Simple circuit
/create-schematic "voltage divider with two 10k resistors"

# Power supply
/create-schematic "3.3V voltage regulator circuit with AMS1117 and bypass capacitors"

# LED circuit
/create-schematic "LED circuit with 330 ohm resistor and 5V power supply"

# More complex
/create-schematic "ESP32-C3 dev board with USB-C, voltage regulator, and reset button"
```

## What This Does

This command:
1. Analyzes your circuit description
2. Selects appropriate components from KiCAD libraries
3. Creates schematic with proper component placement
4. Adds pin-to-pin wiring connections
5. Sets component properties (values, footprints, etc.)
6. Saves to a .kicad_sch file in current directory
7. Provides summary of components used

## Implementation

When you provide a circuit description, I will:

### 1. Parse Requirements
- Identify required components (resistors, capacitors, ICs, etc.)
- Determine component values from description
- Identify connections and topology

### 2. Select Components
```python
# Select appropriate KiCAD library components
# Device:R for resistors
# Device:C for capacitors
# Device:LED for LEDs
# Regulator_Linear:AMS1117-3.3 for voltage regulators
# RF_Module:ESP32-C3-MINI-1 for ESP32
# etc.
```

### 3. Generate Schematic
```python
import kicad_sch_api as ksa

# Create schematic with descriptive title
sch = ksa.create_schematic("Circuit Name from Description")

# Add components with proper spacing
# Position components logically (left to right: input -> processing -> output)
# Add appropriate footprints for each component

# Wire components together
# Use pin-to-pin wiring for automatic routing
# Add power symbols and ground connections

# Add labels for important nets
# Set component properties (tolerance, power rating, etc.)

# Save to file
sch.save("circuit_name.kicad_sch")
```

### 4. Best Practices Applied

**Component Placement:**
- Input on left, output on right
- Power supplies at top
- Ground at bottom
- Logical signal flow

**Component Selection:**
- Standard KiCAD footprints (0603, 0805 for passives)
- Common ICs with proper package types
- Connectors with correct pinouts

**Properties:**
- Footprints assigned to all components
- Values set appropriately
- Power ratings on resistors
- Voltage ratings on capacitors
- Part numbers for ICs

**Wiring:**
- Clean orthogonal routing
- Proper net labels
- Power symbols where appropriate

## Output

After running, you'll get:
1. **Schematic file**: `circuit_name.kicad_sch` in current directory
2. **Component summary**: List of all components added
3. **Next steps**: How to open in KiCAD and proceed

## Example Session

```
User: /create-schematic "LED with 330 ohm current limiting resistor for 5V"

Claude: I'll create an LED circuit with current limiting resistor for you.

[Creates schematic with]
- LED (Device:LED)
- Resistor 330Ω (Device:R)
- Power connector
- Ground connection
- Proper footprints and wiring

✅ Schematic saved: led_circuit.kicad_sch

Components used:
- D1: LED (LED_SMD:LED_0603_1608Metric)
- R1: 330Ω resistor (Resistor_SMD:R_0603_1608Metric)
- J1: Power connector (Connector:Conn_01x02)

Next steps:
1. Open in KiCAD: kicad led_circuit.kicad_sch
2. Review and adjust component placement
3. Add PCB layout
```

## Tips

**Be Specific**: The more details you provide, the better the result.
- "3.3V regulator" → Will use common LDO like AMS1117
- "Buck converter 5V to 3.3V" → Will use switching regulator topology
- "ESP32 dev board" → Will include USB, voltage regulator, buttons, etc.

**Common Components Recognized:**
- Resistors, capacitors, inductors, LEDs
- Voltage regulators (linear and switching)
- Microcontrollers (ESP32, STM32, ATmega, etc.)
- Op-amps, comparators
- USB connectors, headers
- Buttons, switches

**Circuit Patterns:**
- Voltage dividers
- RC filters (low-pass, high-pass)
- LED drivers
- Power supplies
- Decoupling networks
- Pull-up/pull-down resistors

## Hierarchical Schematics

For complex designs with multiple subsystems, I can create hierarchical schematics:

```bash
/create-schematic "STM32 development board with separate sheets for power, MCU, USB, and peripherals"
```

**This will create:**
- Main schematic with hierarchical sheet symbols
- Separate schematic files for each subsystem
- Proper hierarchical connections using sheet pins

**Important**: When creating hierarchical schematics, the code automatically uses `set_hierarchy_context()` to ensure component references display correctly in KiCad.

See `examples/stm32g431_simple.py` for a complete hierarchical design example.

## Limitations

- Cannot design analog circuits requiring specific tuning
- Cannot optimize for specific performance requirements automatically
- Generated schematics may need manual refinement
- Complex ICs may need manual pin assignment review

## See Also

- Check `examples/complete_board_example.py` for complex board template
- See `llm.txt` for complete API documentation
- Read `examples/README.md` for learning progression