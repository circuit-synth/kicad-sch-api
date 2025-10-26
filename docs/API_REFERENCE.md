# API Reference

Complete reference for k

icad-sch-api. For practical examples, see [RECIPES.md](RECIPES.md).

## Table of Contents

1. [Creating Schematics](#creating-schematics)
2. [Component Operations](#component-operations)
3. [Wire Operations](#wire-operations)
4. [Label Operations](#label-operations)
5. [Collections API](#collections-api)
6. [Configuration](#configuration)
7. [File Operations](#file-operations)

---

## Creating Schematics

### `create_schematic(name: str) → Schematic`

Create a new blank schematic.

```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("My Circuit")
```

**Parameters:**
- `name` (str): Schematic name (appears in title block)

**Returns:** Schematic object

---

### `load_schematic(filepath: str) → Schematic`

Load an existing KiCAD schematic file.

```python
sch = ksa.load_schematic("existing.kicad_sch")
```

**Parameters:**
- `filepath` (str): Path to .kicad_sch file

**Returns:** Schematic object

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `ValueError`: If file is not valid KiCAD format

---

## Component Operations

### `Schematic.components`

ComponentCollection object providing access to all components.

### `components.add(lib_id, reference, value, position, **kwargs) → Component`

Add a component to the schematic.

```python
resistor = sch.components.add(
    lib_id="Device:R",
    reference="R1",
    value="10k",
    position=(100, 100),
    footprint="Resistor_SMD:R_0805_2012Metric"
)
```

**Parameters:**
- `lib_id` (str): Library and component name (e.g., "Device:R")
- `reference` (str, optional): Component reference (e.g., "R1"). Auto-generated if None.
- `value` (str): Component value (e.g., "10k", "100nF")
- `position` (tuple or Point, optional): (x, y) position in mm. Auto-placed if None.
- `footprint` (str, optional): PCB footprint
- `unit` (int, optional): Unit number for multi-unit components. Default: 1
- `component_uuid` (str, optional): Specific UUID. Auto-generated if None.
- `**properties`: Additional properties as keyword arguments

**Returns:** Component object

**Raises:**
- `ValidationError`: If lib_id invalid or reference already exists

**Example:**
```python
# Minimal
r = sch.components.add("Device:R", "R1", "10k", (100, 100))

# With all options
r = sch.components.add(
    lib_id="Device:R",
    reference="R1",
    value="10k",
    position=(100, 100),
    footprint="Resistor_SMD:R_0805_2012Metric",
    unit=1,
    Tolerance="1%",
    Power="0.125W",
    MPN="RC0805FR-0710KL"
)
```

---

### `components.get(reference: str) → Optional[Component]`

Get component by reference.

```python
resistor = sch.components.get("R1")
if resistor:
    print(f"R1 value: {resistor.value}")
```

**Parameters:**
- `reference` (str): Component reference

**Returns:** Component object or None if not found

---

### `components.remove(reference: str) → bool`

Remove component by reference.

```python
removed = sch.components.remove("R1")
print(f"Removed: {removed}")  # True if removed, False if not found
```

**Parameters:**
- `reference` (str): Component reference

**Returns:** True if removed, False if not found

---

### `components.filter(**criteria) → List[Component]`

Filter components by criteria.

```python
# By library
resistors = sch.components.filter(lib_id="Device:R")

# By value
ten_k_resistors = sch.components.filter(value="10k")

# By footprint
smd_parts = sch.components.filter(footprint="*SMD*")

# Multiple criteria
ten_k_smd_resistors = sch.components.filter(
    lib_id="Device:R",
    value="10k",
    footprint="*SMD*"
)
```

**Parameters:**
- `lib_id` (str, optional): Library ID to match
- `value` (str, optional): Value to match (exact)
- `value_pattern` (str, optional): Value pattern (substring)
- `reference_pattern` (str, optional): Reference regex pattern
- `footprint` (str, optional): Footprint to match
- `in_area` (tuple, optional): (x1, y1, x2, y2) bounding box
- `has_property` (str, optional): Must have this property

**Returns:** List of matching components

---

### `components.bulk_update(criteria: Dict, updates: Dict) → int`

Update multiple components at once.

```python
# Update all resistors
count = sch.components.bulk_update(
    criteria={'lib_id': 'Device:R'},
    updates={'properties': {'Tolerance': '1%', 'Power': '0.125W'}}
)
print(f"Updated {count} resistors")
```

**Parameters:**
- `criteria` (dict): Selection criteria
- `updates` (dict): Updates to apply

**Returns:** Number of components updated

---

### Component Object

Represents a single component.

#### Properties

```python
comp = sch.components.get("R1")

# Read/write properties
comp.reference      # str: "R1"
comp.value         # str: "10k"
comp.footprint     # Optional[str]: "Resistor_SMD:R_0805_2012Metric"
comp.position      # Point: Point(x=100, y=100)
comp.rotation      # float: Rotation in degrees
comp.lib_id        # str: "Device:R"
comp.uuid          # str: UUID
comp.properties    # Dict[str, str]: All properties

# Read-only properties
comp.library       # str: "Device"
comp.symbol_name   # str: "R"
comp.pins          # List[SchematicPin]: Pin information
```

#### Methods

```python
# Property management
comp.set_property("MPN", "RC0805FR-0710KL")
comp.get_property("MPN", default="")
comp.has_property("MPN")  # Returns bool
comp.remove_property("MPN")

# Pin operations
pin = comp.get_pin("1")  # Get pin by number
pin_pos = comp.get_pin_position("1")  # Get absolute position

# Validation
issues = comp.validate()  # List[ValidationIssue]

# Conversion
comp_dict = comp.to_dict()  # Convert to dictionary
```

---

## Wire Operations

### `Schematic.wires`

WireCollection object providing access to all wires.

### `wires.add(start=None, end=None, points=None, **kwargs) → str`

Add a wire.

```python
# Simple 2-point wire
wire_uuid = sch.wires.add(start=(100, 100), end=(150, 100))

# Multi-point wire (L-shaped)
wire_uuid = sch.wires.add(
    points=[
        (100, 100),
        (100, 120),
        (150, 120)
    ]
)
```

**Parameters:**
- `start` (tuple or Point, optional): Start point for 2-point wire
- `end` (tuple or Point, optional): End point for 2-point wire
- `points` (List[tuple or Point], optional): List of points for multi-point wire
- `wire_type` (WireType, optional): Wire type. Default: WireType.WIRE
- `stroke_width` (float, optional): Line width. Default: 0.0
- `uuid` (str, optional): Specific UUID

**Returns:** Wire UUID (string)

**Raises:**
- `ValueError`: If neither start/end nor points provided

---

### `add_wire_between_pins(from_ref, from_pin, to_ref, to_pin) → Optional[str]`

Connect two component pins automatically.

```python
# Connect R1 pin 2 to R2 pin 1
wire_uuid = sch.add_wire_between_pins("R1", "2", "R2", "1")
```

**Parameters:**
- `from_ref` (str): Source component reference
- `from_pin` (str): Source pin number
- `to_ref` (str): Destination component reference
- `to_pin` (str): Destination pin number

**Returns:** Wire UUID or None if components/pins not found

---

### `add_wire_to_pin(point, component_ref, pin) → Optional[str]`

Connect a point to a component pin.

```python
# Connect external point to R1 pin 1
sch.add_wire_to_pin((50, 100), "R1", "1")

# Using Point object
from kicad_sch_api.core.types import Point
sch.add_wire_to_pin(Point(50, 100), "R1", "1")
```

**Parameters:**
- `point` (tuple or Point): External point coordinates
- `component_ref` (str): Component reference
- `pin` (str): Pin number

**Returns:** Wire UUID or None if component/pin not found

---

### `wires.get(uuid: str) → Optional[Wire]`

Get wire by UUID.

```python
wire = sch.wires.get(wire_uuid)
```

---

### `wires.remove(uuid: str) → bool`

Remove wire by UUID.

```python
removed = sch.wires.remove(wire_uuid)
```

---

### `wires.get_by_point(point, tolerance=None) → List[Wire]`

Find wires near a point.

```python
wires = sch.wires.get_by_point((100, 100), tolerance=1.0)
```

---

## Label Operations

### `Schematic.labels`

LabelCollection object providing access to all labels.

### `add_label(text, position, **kwargs) → str`

Add a label (net name).

```python
label_uuid = sch.add_label("VCC", position=(100, 50))

# With options
label_uuid = sch.add_label(
    text="SDA",
    position=(150, 100),
    rotation=0.0,
    size=1.27
)
```

**Parameters:**
- `text` (str): Label text
- `position` (tuple or Point): Position
- `rotation` (float, optional): Rotation in degrees. Default: 0.0
- `size` (float, optional): Text size. Default: 1.27
- `label_uuid` (str, optional): Specific UUID

**Returns:** Label UUID

---

### `labels.find_by_text(text, exact=True) → List[LabelElement]`

Find labels by text.

```python
# Exact match
vcc_labels = sch.labels.find_by_text("VCC", exact=True)

# Substring match
power_labels = sch.labels.find_by_text("VCC", exact=False)
```

---

### `labels.remove(uuid: str) → bool`

Remove label by UUID.

```python
removed = sch.labels.remove(label_uuid)
```

---

## Collections API

All collections (components, wires, labels, etc.) inherit from BaseCollection.

### Common Methods

```python
# Length
count = len(sch.components)

# Iteration
for comp in sch.components:
    print(comp.reference)

# Indexing by UUID
comp = sch.components[uuid]

# Indexing by position
first_comp = sch.components[0]

# Contains check
if "R1" in sch.components:  # Checks reference for ComponentCollection
    print("R1 exists")

# Get by UUID
comp = sch.components.get(uuid)

# Find with predicate
matching = sch.components.find(lambda c: c.value == "10k")

# Remove
removed = sch.components.remove(uuid)

# Clear all
sch.components.clear()

# Statistics
stats = sch.components.get_statistics()
```

### Modification Tracking

```python
# Check if modified
if sch.components.is_modified():
    print("Components have been modified")

# Reset flag (usually after save)
sch.components.reset_modified_flag()
```

---

## Configuration

Global configuration accessible via `ksa.config`.

### Property Positioning

```python
# Adjust label positions
ksa.config.properties.reference_y = -2.0  # Reference label offset
ksa.config.properties.value_y = 2.0       # Value label offset
ksa.config.properties.footprint_y = 4.0   # Footprint label offset
```

### Tolerances

```python
# Position matching tolerance
ksa.config.tolerance.position_tolerance = 0.01  # mm

# Wire segment minimum length
ksa.config.tolerance.wire_segment_min = 0.005  # mm
```

### Defaults

```python
# Default values for new elements
ksa.config.defaults.project_name = "My Project"
ksa.config.defaults.stroke_width = 0.1
ksa.config.defaults.text_size = 1.27
```

### Grid and Spacing

```python
# Grid settings
ksa.config.grid.size = 2.54  # KiCAD grid size (0.1 inch)
ksa.config.grid.unit_spacing = 10.0  # Multi-unit IC spacing
ksa.config.grid.component_spacing = 5.0  # Component spacing
```

### Sheet Settings

```python
# Hierarchical sheet settings
ksa.config.sheet.name_offset_y = -1.0
ksa.config.sheet.file_offset_y = 1.0
```

---

## File Operations

### `Schematic.save(filepath: str = None)`

Save schematic to file.

```python
# Save to original path (if loaded)
sch.save()

# Save to new path
sch.save("new_circuit.kicad_sch")
```

**Parameters:**
- `filepath` (str, optional): Save path. Uses original if None.

**Raises:**
- `ValueError`: If filepath is None and schematic wasn't loaded from file

---

## Hierarchical Sheets

### `add_hierarchical_sheet(name, filename, position, size, **kwargs)`

Add a hierarchical sheet.

```python
sheet_uuid = sch.add_hierarchical_sheet(
    name="Power Supply",
    filename="power.kicad_sch",
    position=(100, 100),
    size=(80, 60)
)
```

**Parameters:**
- `name` (str): Sheet name/title
- `filename` (str): Referenced schematic filename
- `position` (tuple or Point): Top-left corner position
- `size` (tuple or Point): (width, height)
- `project_name` (str, optional): Project name
- `page_number` (str, optional): Page number
- `uuid` (str, optional): Specific UUID

**Returns:** Sheet UUID

---

### `add_hierarchical_label(text, label_type, position, **kwargs)`

Add a hierarchical label (sheet connector).

```python
label_uuid = sch.add_hierarchical_label(
    text="VIN",
    label_type="input",
    position=(50, 25)
)
```

**Parameters:**
- `text` (str): Label text
- `label_type` (str): Type: "input", "output", "bidirectional", "tri_state", "passive"
- `position` (tuple or Point): Position
- `shape` (str, optional): Shape style
- `uuid` (str, optional): Specific UUID

**Returns:** Label UUID

---

## Junctions

### `junctions.add(position, **kwargs) → str`

Add a junction (connection point).

```python
junction_uuid = sch.junctions.add(position=(100, 100))
```

---

## No-Connect Symbols

### `no_connects.add(position, **kwargs) → NoConnectElement`

Add a no-connect symbol.

```python
nc = sch.no_connects.add(position=(100, 100))
```

---

## Text Elements

### `texts.add(text, position, **kwargs) → TextElement`

Add text annotation.

```python
text = sch.texts.add(
    text="Important Note",
    position=(100, 100),
    size=2.0,
    rotation=0.0
)
```

---

## Validation

### `Schematic.validate() → List[ValidationIssue]`

Validate entire schematic.

```python
issues = sch.validate()
for issue in issues:
    print(f"{issue.severity}: {issue.message}")
```

---

## Utilities

### Point Class

```python
from kicad_sch_api.core.types import Point

p1 = Point(100, 100)
p2 = Point(150, 150)

# Distance
dist = p1.distance_to(p2)

# Addition
p3 = p1 + p2  # Component-wise addition

# Access
x = p1.x
y = p1.y
```

---

## Type Hints

Library provides full type hints:

```python
from kicad_sch_api import Schematic, Component
from kicad_sch_api.core.types import Point
from typing import Optional, List

def process_schematic(sch: Schematic) -> List[str]:
    """Process schematic and return component references."""
    references: List[str] = []

    comp: Component
    for comp in sch.components:
        references.append(comp.reference)

    return references
```

---

## Error Handling

```python
from kicad_sch_api.utils.validation import ValidationError

try:
    sch.components.add("InvalidLib:Part", "R1", "10k", (100, 100))
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    sch = ksa.load_schematic("missing.kicad_sch")
except FileNotFoundError:
    print("File not found")
except ValueError as e:
    print(f"Invalid file format: {e}")
```

---

## Complete Example

```python
import kicad_sch_api as ksa

# Create schematic
sch = ksa.create_schematic("Complete Example")

# Add components
r1 = sch.components.add("Device:R", "R1", "10k", (100, 100))
r2 = sch.components.add("Device:R", "R2", "5k", (100, 120))
c1 = sch.components.add("Device:C", "C1", "100nF", (150, 110))

# Set properties
r1.set_property("Tolerance", "1%")
r1.set_property("Power", "0.125W")

# Connect components
sch.add_wire_between_pins("R1", "2", "R2", "1")
sch.add_wire_between_pins("R2", "2", "C1", "1")

# Add labels
sch.add_label("VIN", (100, 90))
sch.add_label("VOUT", (125, 110))
sch.add_label("GND", (150, 130))

# Add junction at connection point
sch.junctions.add((125, 110))

# Validate
issues = sch.validate()
if issues:
    for issue in issues:
        print(f"Warning: {issue.message}")

# Save
sch.save("complete_example.kicad_sch")
print("Schematic created successfully!")
```

---

For more examples, see:
- [GETTING_STARTED.md](GETTING_STARTED.md) - Beginner guide
- [RECIPES.md](RECIPES.md) - Common patterns and solutions
- `examples/` directory - Complete working examples
