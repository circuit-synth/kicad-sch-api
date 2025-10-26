# Common Recipes and Patterns

This guide shows solutions to common tasks with kicad-sch-api.

## Table of Contents

1. [Basic Circuit Patterns](#basic-circuit-patterns)
2. [Component Management](#component-management)
3. [Wiring and Connectivity](#wiring-and-connectivity)
4. [Circuit Analysis](#circuit-analysis)
5. [Batch Operations](#batch-operations)
6. [Advanced Patterns](#advanced-patterns)

---

## Basic Circuit Patterns

### Recipe 1: Voltage Divider

```python
import kicad_sch_api as ksa

def create_voltage_divider(sch, name, r1_val, r2_val, position, v_in_label="VIN", v_out_label="VOUT"):
    """Create a voltage divider at the specified position.

    Args:
        sch: Schematic object
        name: Unique identifier for this divider
        r1_val: Top resistor value (string, e.g., "10k")
        r2_val: Bottom resistor value
        position: (x, y) tuple for placement
        v_in_label: Input voltage label
        v_out_label: Output voltage label

    Returns:
        Tuple of (r1_component, r2_component)
    """
    x, y = position

    # Add resistors
    r1 = sch.components.add(
        "Device:R",
        f"R_{name}_1",
        r1_val,
        (x, y)
    )

    r2 = sch.components.add(
        "Device:R",
        f"R_{name}_2",
        r2_val,
        (x, y + 20)  # 20mm below first resistor
    )

    # Connect resistors
    sch.add_wire_between_pins(f"R_{name}_1", "2", f"R_{name}_2", "1")

    # Add connection points and labels
    sch.add_wire_to_pin((x, y - 10), f"R_{name}_1", "1")
    sch.add_label(v_in_label, (x, y - 10))

    sch.add_wire_to_pin((x + 10, y + 10), f"R_{name}_1", "2")
    sch.add_label(v_out_label, (x + 10, y + 10))

    sch.add_wire_to_pin((x, y + 30), f"R_{name}_2", "2")
    sch.add_label("GND", (x, y + 30))

    return r1, r2

# Use it
sch = ksa.create_schematic("Voltage Dividers")
create_voltage_divider(sch, "3V3", "10k", "5k", (100, 100))
create_voltage_divider(sch, "1V8", "22k", "10k", (150, 100))
sch.save("dividers.kicad_sch")
```

### Recipe 2: RC Low-Pass Filter

```python
def create_rc_filter(sch, name, r_val, c_val, position):
    """Create an RC low-pass filter.

    Cutoff frequency: f_c = 1 / (2 * π * R * C)
    """
    x, y = position

    # Resistor
    r = sch.components.add("Device:R", f"R_{name}", r_val, (x, y))

    # Capacitor
    c = sch.components.add("Device:C", f"C_{name}", c_val, (x + 20, y + 10))

    # Connect R output to C input
    sch.add_wire_between_pins(f"R_{name}", "2", f"C_{name}", "1")

    # Input
    sch.add_wire_to_pin((x - 10, y), f"R_{name}", "1")
    sch.add_label("INPUT", (x - 10, y))

    # Output (between R and C)
    sch.add_label("OUTPUT", (x + 10, y))

    # Ground the capacitor
    sch.add_wire_to_pin((x + 20, y + 20), f"C_{name}", "2")
    sch.add_label("GND", (x + 20, y + 25))

    return r, c

# Calculate values for specific cutoff frequency
import math

def rc_values_for_frequency(target_freq_hz):
    """Calculate R and C values for target frequency."""
    # Use standard E12 values
    c_val = 100e-9  # 100nF
    r_val = 1 / (2 * math.pi * target_freq_hz * c_val)
    # Round to nearest E12 value
    return f"{int(r_val)}", f"{int(c_val * 1e9)}nF"

# Create filter for 1kHz cutoff
sch = ksa.create_schematic("RC Filter")
r_val, c_val = rc_values_for_frequency(1000)
create_rc_filter(sch, "1kHz", r_val, c_val, (100, 100))
sch.save("rc_filter_1khz.kicad_sch")
```

### Recipe 3: LED with Current-Limiting Resistor

```python
def create_led_circuit(sch, name, led_color, supply_voltage, led_forward_voltage, current_ma, position):
    """Create LED circuit with calculated current-limiting resistor.

    Args:
        supply_voltage: Supply voltage (e.g., 5.0 for 5V)
        led_forward_voltage: LED forward voltage (e.g., 2.0 for red LED)
        current_ma: Desired current in milliamps (e.g., 20)
    """
    x, y = position

    # Calculate resistor value: R = (V_supply - V_led) / I
    v_drop = supply_voltage - led_forward_voltage
    r_ohms = v_drop / (current_ma / 1000.0)

    # Round to nearest standard value
    r_val = f"{int(r_ohms)}"

    # Add components
    r = sch.components.add("Device:R", f"R_{name}", r_val, (x, y))
    led = sch.components.add("Device:LED", f"D_{name}", led_color, (x, y + 20))

    # Connect
    sch.add_wire_between_pins(f"R_{name}", "2", f"D_{name}", "1")

    # Power connection
    sch.add_wire_to_pin((x, y - 10), f"R_{name}", "1")
    sch.add_label(f"V{int(supply_voltage)}V", (x, y - 10))

    # Ground
    sch.add_wire_to_pin((x, y + 30), f"D_{name}", "2")
    sch.add_label("GND", (x, y + 30))

    print(f"LED {name}: {r_val}Ω resistor for {current_ma}mA at {supply_voltage}V")

    return r, led

# Create multiple LED circuits
sch = ksa.create_schematic("LED Indicators")
create_led_circuit(sch, "RED", "RED", 5.0, 2.0, 20, (100, 100))
create_led_circuit(sch, "GREEN", "GREEN", 5.0, 2.2, 20, (150, 100))
create_led_circuit(sch, "BLUE", "BLUE", 5.0, 3.2, 20, (200, 100))
sch.save("led_indicators.kicad_sch")
```

---

## Component Management

### Recipe 4: Find and Update Components

```python
# Load existing schematic
sch = ksa.load_schematic("design.kicad_sch")

# Find all resistors
resistors = sch.components.filter(lib_id="Device:R")
print(f"Found {len(resistors)} resistors")

# Update specific resistors
for r in resistors:
    if r.reference.startswith("R_PULLUP"):
        r.value = "10k"  # Standardize pullups to 10k
        r.set_property("Tolerance", "5%")

# Find components by value
high_value_resistors = [
    r for r in resistors
    if "k" in r.value and float(r.value.replace("k", "")) > 100
]

# Find components in specific area
components_in_area = sch.components.in_area(
    x1=100, y1=100,
    x2=200, y2=200
)

# Find components near a point
components_near_ic = sch.components.near_point(
    point=(150, 150),
    radius=30  # 30mm radius
)
```

### Recipe 5: Bulk Property Updates

```python
# Add manufacturer part numbers to all resistors
resistor_mpns = {
    "10k": "RC0603FR-0710KL",
    "100k": "RC0603FR-07100KL",
    # ...
}

resistors = sch.components.filter(lib_id="Device:R")
for r in resistors:
    if r.value in resistor_mpns:
        r.set_property("MPN", resistor_mpns[r.value])
        r.set_property("Manufacturer", "Yageo")

# Bulk update all capacitors
sch.components.bulk_update(
    criteria={'lib_id': 'Device:C'},
    updates={
        'properties': {
            'Voltage': '50V',
            'Tolerance': '10%'
        }
    }
)

# Update all SMD footprints to 0805
for comp in sch.components:
    if "0603" in (comp.footprint or ""):
        comp.footprint = comp.footprint.replace("0603", "0805")
```

### Recipe 6: Component Validation

```python
def validate_design(sch):
    """Check design for common issues."""
    issues = []

    # Check for missing footprints
    for comp in sch.components:
        if not comp.footprint:
            issues.append(f"{comp.reference}: Missing footprint")

    # Check for missing MPNs (for production)
    for comp in sch.components:
        if not comp.has_property("MPN"):
            issues.append(f"{comp.reference}: Missing MPN property")

    # Check resistor power ratings
    for r in sch.components.filter(lib_id="Device:R"):
        if not r.has_property("Power"):
            issues.append(f"{r.reference}: Missing power rating")

    # Check for duplicate references (shouldn't happen, but check anyway)
    refs = [c.reference for c in sch.components]
    duplicates = [ref for ref in refs if refs.count(ref) > 1]
    if duplicates:
        issues.append(f"Duplicate references: {set(duplicates)}")

    return issues

# Validate and report
issues = validate_design(sch)
if issues:
    print("Design issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Design validation passed!")
```

---

## Wiring and Connectivity

### Recipe 7: Auto-Route Between Components

```python
# Connect multiple components in a chain
components = ["R1", "C1", "R2", "C2", "R3"]

for i in range(len(components) - 1):
    current = components[i]
    next_comp = components[i + 1]

    # Connect output of current to input of next
    sch.add_wire_between_pins(current, "2", next_comp, "1")

# Create a bus connection
resistors = ["R1", "R2", "R3", "R4"]
for r in resistors:
    # Connect all resistor pin 1's to VCC
    sch.add_wire_to_pin((50, 50), r, "1")
    sch.add_label("VCC", (50, 50))

    # Connect all resistor pin 2's to different signal lines
    pin_pos = sch.get_component_pin_position(r, "2")
    if pin_pos:
        sch.add_label(f"SIG_{r}", (pin_pos.x + 10, pin_pos.y))
```

### Recipe 8: Create Multi-Point Wires

```python
# Create L-shaped wire (Manhattan routing)
sch.wires.add(
    points=[
        (100, 100),  # Start
        (100, 120),  # Down 20mm
        (150, 120),  # Right 50mm
        (150, 140)   # Down 20mm to end
    ]
)

# Create connection with junction
junction = sch.junctions.add(position=(125, 120))

# Wires connecting to junction
sch.wires.add(start=(100, 100), end=(125, 120))  # To junction
sch.wires.add(start=(125, 120), end=(150, 120))  # From junction
sch.wires.add(start=(125, 120), end=(125, 150))  # Branch from junction
```

### Recipe 9: Label Management

```python
# Add labels for nets
sch.add_label("VCC", position=(100, 50))
sch.add_label("GND", position=(100, 150))
sch.add_label("SDA", position=(150, 100))
sch.add_label("SCL", position=(150, 120))

# Find all labels with specific text
vcc_labels = sch.labels.find_by_text("VCC")
print(f"Found {len(vcc_labels)} VCC labels")

# Rename a net (update all labels)
old_net = "VIN"
new_net = "V_INPUT"
for label in sch.labels.find_by_text(old_net):
    label.text = new_net
```

---

## Circuit Analysis

### Recipe 10: Generate Bill of Materials

```python
def generate_bom(sch):
    """Generate bill of materials from schematic."""
    bom = {}

    for comp in sch.components:
        # Create BOM key (lib_id + value + footprint)
        key = (comp.lib_id, comp.value, comp.footprint or "N/A")

        if key not in bom:
            bom[key] = {
                'lib_id': comp.lib_id,
                'value': comp.value,
                'footprint': comp.footprint,
                'quantity': 0,
                'references': [],
                'mpn': comp.get_property("MPN", "")
            }

        bom[key]['quantity'] += 1
        bom[key]['references'].append(comp.reference)

    return list(bom.values())

# Generate and print BOM
sch = ksa.load_schematic("product.kicad_sch")
bom = generate_bom(sch)

print("Bill of Materials:")
print(f"{'Qty':<5} {'References':<20} {'Value':<10} {'Part Number'}")
print("-" * 70)
for item in sorted(bom, key=lambda x: x['lib_id']):
    refs = ", ".join(sorted(item['references']))
    print(f"{item['quantity']:<5} {refs:<20} {item['value']:<10} {item['mpn']}")
```

### Recipe 11: Find Unconnected Pins

```python
def find_unconnected_pins(sch):
    """Find component pins that aren't connected to anything."""
    unconnected = []

    for comp in sch.components:
        for pin in comp.pins:
            pin_pos = sch.get_component_pin_position(comp.reference, pin.number)
            if not pin_pos:
                continue

            # Check if any wire connects to this pin
            connected = False
            for wire in sch.wires:
                for point in wire.points:
                    if point.distance_to(pin_pos) < 0.1:  # 0.1mm tolerance
                        connected = True
                        break

            if not connected:
                unconnected.append((comp.reference, pin.number, pin.name))

    return unconnected

# Check for unconnected pins
unconnected = find_unconnected_pins(sch)
if unconnected:
    print("Warning: Unconnected pins found:")
    for ref, pin_num, pin_name in unconnected:
        print(f"  {ref} pin {pin_num} ({pin_name})")
```

### Recipe 12: Component Statistics

```python
def get_component_statistics(sch):
    """Get statistics about components in schematic."""
    stats = {
        'total_components': len(sch.components),
        'by_type': {},
        'by_library': {},
        'total_value': 0
    }

    for comp in sch.components:
        # Count by type
        comp_type = comp.lib_id.split(":")[-1]
        stats['by_type'][comp_type] = stats['by_type'].get(comp_type, 0) + 1

        # Count by library
        lib = comp.lib_id.split(":")[0]
        stats['by_library'][lib] = stats['by_library'].get(lib, 0) + 1

    return stats

# Print statistics
stats = get_component_statistics(sch)
print(f"Total components: {stats['total_components']}")
print("\nBy type:")
for comp_type, count in sorted(stats['by_type'].items()):
    print(f"  {comp_type}: {count}")
print("\nBy library:")
for lib, count in sorted(stats['by_library'].items()):
    print(f"  {lib}: {count}")
```

---

## Batch Operations

### Recipe 13: Generate Test Circuits

```python
def generate_pin_test_circuit(ic_part, pin_number):
    """Generate test circuit for a specific IC pin."""
    sch = ksa.create_schematic(f"Test_{ic_part}_Pin{pin_number}")

    # Add IC
    ic = sch.components.add(
        f"IC:{ic_part}",
        "U1",
        ic_part,
        (100, 100)
    )

    # Add test resistor to the pin
    test_r = sch.components.add(
        "Device:R",
        f"R_TEST_{pin_number}",
        "10k",
        (150, 100 + pin_number * 10)
    )

    # Connect
    sch.add_wire_between_pins("U1", str(pin_number), f"R_TEST_{pin_number}", "1")

    # Add measurement point
    sch.add_label(f"TEST_PIN_{pin_number}", (160, 100 + pin_number * 10))

    return sch

# Generate test circuits for all 64 pins
ic_part = "STM32F103"
for pin in range(1, 65):
    sch = generate_pin_test_circuit(ic_part, pin)
    sch.save(f"test_{ic_part}_pin{pin:02d}.kicad_sch")
```

### Recipe 14: Parameter Sweep

```python
def generate_filter_sweep():
    """Generate filters with different cutoff frequencies."""
    frequencies = [100, 500, 1000, 5000, 10000]  # Hz

    for freq in frequencies:
        sch = ksa.create_schematic(f"Filter_{freq}Hz")

        # Calculate R and C for this frequency
        C = 100e-9  # Fixed 100nF
        R = 1 / (2 * 3.14159 * freq * C)

        create_rc_filter(sch, f"{freq}Hz", f"{int(R)}", "100nF", (100, 100))

        sch.save(f"filter_{freq}hz.kicad_sch")
        print(f"Generated filter for {freq}Hz")

generate_filter_sweep()
```

### Recipe 15: Design Variants

```python
def create_design_variant(base_sch_path, variant_name, modifications):
    """Create a design variant with specific modifications."""
    # Load base design
    sch = ksa.load_schematic(base_sch_path)

    # Apply modifications
    for mod in modifications:
        if mod['type'] == 'change_value':
            comp = sch.components.get(mod['reference'])
            if comp:
                comp.value = mod['new_value']

        elif mod['type'] == 'add_component':
            sch.components.add(
                mod['lib_id'],
                mod['reference'],
                mod['value'],
                mod['position']
            )

        elif mod['type'] == 'remove_component':
            sch.components.remove(mod['reference'])

    # Save variant
    sch.save(f"{variant_name}.kicad_sch")

# Create variants
modifications_v2 = [
    {'type': 'change_value', 'reference': 'R1', 'new_value': '22k'},
    {'type': 'add_component', 'lib_id': 'Device:C', 'reference': 'C10',
     'value': '10uF', 'position': (150, 150)}
]

create_design_variant("base_design.kicad_sch", "design_v2", modifications_v2)
```

---

## Advanced Patterns

### Recipe 16: Template System

```python
class CircuitTemplate:
    """Base class for circuit templates."""

    def generate(self, sch, position, **params):
        """Generate circuit at position with parameters."""
        raise NotImplementedError

class VoltageRegulatorTemplate(CircuitTemplate):
    """Linear voltage regulator template."""

    def generate(self, sch, position, v_in, v_out, current_ma):
        x, y = position

        # Add regulator IC
        reg = sch.components.add(
            "Regulator_Linear:LM317_TO220",
            f"U_REG_{v_out}V",
            "LM317",
            (x, y)
        )

        # Calculate resistor values
        r1_val = "240"  # Standard value
        r2_val = str(int((v_out - 1.25) * 240 / 1.25))

        # Add resistors
        r1 = sch.components.add("Device:R", f"R1_{v_out}V", r1_val, (x + 20, y))
        r2 = sch.components.add("Device:R", f"R2_{v_out}V", r2_val, (x + 20, y + 10))

        # Add capacitors
        c_in = sch.components.add("Device:C", f"C_IN_{v_out}V", "100nF", (x - 10, y))
        c_out = sch.components.add("Device:C", f"C_OUT_{v_out}V", "10uF", (x + 30, y))

        # Wire it up...
        return reg

# Use templates
templates = {
    'regulator': VoltageRegulatorTemplate(),
}

sch = ksa.create_schematic("Power Supply")
templates['regulator'].generate(sch, (100, 100), v_in=12, v_out=5, current_ma=500)
sch.save("power_supply.kicad_sch")
```

### Recipe 17: Configuration-Driven Generation

```python
import json

def generate_from_config(config_path):
    """Generate schematic from JSON configuration."""
    with open(config_path) as f:
        config = json.load(f)

    sch = ksa.create_schematic(config['name'])

    # Process components
    for comp_cfg in config['components']:
        sch.components.add(
            comp_cfg['lib_id'],
            comp_cfg['reference'],
            comp_cfg['value'],
            tuple(comp_cfg['position'])
        )

        # Set properties
        comp = sch.components.get(comp_cfg['reference'])
        for key, value in comp_cfg.get('properties', {}).items():
            comp.set_property(key, value)

    # Process connections
    for conn in config['connections']:
        if conn['type'] == 'pin_to_pin':
            sch.add_wire_between_pins(
                conn['from_component'],
                conn['from_pin'],
                conn['to_component'],
                conn['to_pin']
            )

    sch.save(config['output_file'])

# Example config.json:
# {
#   "name": "LED Circuit",
#   "components": [
#     {
#       "lib_id": "Device:R",
#       "reference": "R1",
#       "value": "330",
#       "position": [100, 100]
#     }
#   ],
#   "connections": [
#     {
#       "type": "pin_to_pin",
#       "from_component": "R1",
#       "from_pin": "2",
#       "to_component": "D1",
#       "to_pin": "1"
#     }
#   ]
# }

generate_from_config("circuit_config.json")
```

---

## More Examples

Check the `examples/` directory for complete, working examples:
- `basic_usage.py` - Simple circuits
- `advanced_usage.py` - Complex operations
- `pin_to_pin_wiring_demo.py` - Wiring examples

## Contributing Recipes

Have a useful recipe? Please contribute!

1. Fork the repository
2. Add your recipe to this file
3. Include a working example
4. Submit a pull request

---

**Happy circuit generation!** 🚀
