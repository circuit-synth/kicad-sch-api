# Advanced Hierarchy Management

**Implementation Date:** 2025-11-05
**Issue:** #37 - Advanced hierarchy and sheet management (2.7)
**Issue:** #100 - Hierarchical sheet component references
**Status:** ✅ Complete

## Overview

This document covers two aspects of hierarchical schematic management:

1. **Creating Hierarchical Schematics** - How to build hierarchical designs with proper component references
2. **Analyzing Hierarchical Schematics** - How to analyze existing hierarchical designs

---

## Part 1: Creating Hierarchical Schematics

### Component Reference Problem (Issue #100)

When creating hierarchical schematics, components in child sheets must have correct hierarchical instance paths for KiCad to properly assign reference designators. Without proper paths, KiCad shows "?" instead of "C1", "R1", etc.

### Solution: `set_hierarchy_context()`

Use the `set_hierarchy_context()` method to configure child schematics with proper hierarchical paths.

### Quick Start Example

```python
import kicad_sch_api as ksa

# 1. Create parent schematic
main = ksa.create_schematic("MyProject")
parent_uuid = main.uuid

# 2. Add sheet to parent
power_sheet_uuid = main.sheets.add_sheet(
    name="Power Supply",
    filename="power.kicad_sch",
    position=(50, 50),
    size=(100, 100),
    project_name="MyProject"  # MUST match parent project name
)

# 3. Add sheet pins
main.sheets.add_sheet_pin(power_sheet_uuid, "VIN", "input", "left", 5)
main.sheets.add_sheet_pin(power_sheet_uuid, "+3.3V", "output", "right", 5)

# 4. Create child schematic with hierarchy context
power = ksa.create_schematic("MyProject")  # SAME project name
power.set_hierarchy_context(parent_uuid, power_sheet_uuid)  # KEY STEP!

# 5. Add components - they automatically get correct hierarchical paths
vreg = power.components.add(
    'Regulator_Linear:AMS1117-3.3',
    'U1',
    'AMS1117-3.3',
    position=(127, 101.6)
)
# Component instance path: /parent_uuid/power_sheet_uuid (CORRECT!)

# 6. Save both schematics
main.save("main.kicad_sch")
power.save("power.kicad_sch")
```

### Complete Hierarchical Design Pattern

```python
import kicad_sch_api as ksa
from pathlib import Path

# Project configuration
PROJECT_NAME = "STM32_Board"
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

# ===== STEP 1: Create Main Schematic =====
main = ksa.create_schematic(PROJECT_NAME)
parent_uuid = main.uuid  # Save for child schematics

# ===== STEP 2: Add Hierarchical Sheets =====

# Power supply sheet
power_sheet_uuid = main.sheets.add_sheet(
    name="Power Supply",
    filename="power.kicad_sch",
    position=(50, 50),
    size=(100, 80),
    project_name=PROJECT_NAME
)
main.sheets.add_sheet_pin(power_sheet_uuid, "VIN", "input", "left", 5)
main.sheets.add_sheet_pin(power_sheet_uuid, "+3.3V", "output", "right", 5)
main.sheets.add_sheet_pin(power_sheet_uuid, "GND", "passive", "bottom", 10)

# MCU sheet
mcu_sheet_uuid = main.sheets.add_sheet(
    name="Microcontroller",
    filename="mcu.kicad_sch",
    position=(175, 50),
    size=(100, 80),
    project_name=PROJECT_NAME
)
main.sheets.add_sheet_pin(mcu_sheet_uuid, "+3.3V", "input", "left", 5)
main.sheets.add_sheet_pin(mcu_sheet_uuid, "GND", "passive", "bottom", 10)

# Add labels for connections
main.add_label("+3.3V", position=(155, 55))
main.add_label("GND", position=(100, 140))

# Save main schematic
main.save(str(output_dir / f"{PROJECT_NAME}.kicad_sch"))

# ===== STEP 3: Create Child Schematics with Hierarchy Context =====

# Power supply child schematic
power = ksa.create_schematic(PROJECT_NAME)
power.set_hierarchy_context(parent_uuid, power_sheet_uuid)  # Set context!

vreg = power.components.add(
    'Regulator_Linear:AMS1117-3.3',
    'U1',
    'AMS1117-3.3',
    position=(127, 101.6)
)
vreg.footprint = 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'

c_in = power.components.add('Device:C', 'C1', '10µF', position=(101.6, 101.6))
c_out = power.components.add('Device:C', 'C2', '10µF', position=(152.4, 101.6))

power.add_label("VIN", position=(76.2, 101.6))
power.add_label("+3.3V", position=(177.8, 101.6))
power.add_label("GND", position=(127, 127))

power.save(str(output_dir / "power.kicad_sch"))

# MCU child schematic
mcu_sch = ksa.create_schematic(PROJECT_NAME)
mcu_sch.set_hierarchy_context(parent_uuid, mcu_sheet_uuid)  # Set context!

mcu = mcu_sch.components.add(
    'MCU_ST_STM32G4:STM32G431R_6-8-B_Tx',
    'U2',
    'STM32G431RBT6',
    position=(127, 101.6)
)
mcu.footprint = 'Package_QFP:LQFP-64_10x10mm_P0.5mm'

# Add decoupling caps
for i, x_pos in enumerate([101.6, 152.4], start=3):
    cap = mcu_sch.components.add('Device:C', f'C{i}', '100nF', position=(x_pos, 76.2))
    cap.footprint = 'Capacitor_SMD:C_0603_1608Metric'

mcu_sch.add_label("+3.3V", position=(76.2, 63.5))
mcu_sch.add_label("GND", position=(127, 152.4))

mcu_sch.save(str(output_dir / "mcu.kicad_sch"))

print(f"✓ Hierarchical schematic created in {output_dir}/")
print(f"  - {PROJECT_NAME}.kicad_sch (main)")
print(f"  - power.kicad_sch (child)")
print(f"  - mcu.kicad_sch (child)")
```

### Critical Requirements

1. **Same Project Name**: All schematics (parent and children) MUST use the same project name
   ```python
   main = ksa.create_schematic("MyProject")
   child = ksa.create_schematic("MyProject")  # SAME name!
   ```

2. **Call `set_hierarchy_context()` BEFORE Adding Components**:
   ```python
   child = ksa.create_schematic("MyProject")
   child.set_hierarchy_context(parent_uuid, sheet_uuid)  # Do this FIRST
   child.components.add(...)  # Then add components
   ```

3. **Save Parent UUID Early**:
   ```python
   main = ksa.create_schematic("MyProject")
   parent_uuid = main.uuid  # Save this immediately
   ```

4. **Pass `project_name` to `add_sheet()`**:
   ```python
   sheet_uuid = main.sheets.add_sheet(
       name="Child",
       filename="child.kicad_sch",
       position=(50, 50),
       size=(100, 80),
       project_name="MyProject"  # Required!
   )
   ```

### What Happens Internally

When you call `set_hierarchy_context()`:

1. The schematic stores the parent UUID and sheet UUID
2. The hierarchical path is computed: `/{parent_uuid}/{sheet_uuid}`
3. When components are added, this path is automatically set in their instance data
4. KiCad uses this path to properly annotate components

**Without `set_hierarchy_context()`:**
- Component path: `/child_uuid` ❌ WRONG
- KiCad shows: "C?" instead of "C1"

**With `set_hierarchy_context()`:**
- Component path: `/parent_uuid/sheet_uuid` ✅ CORRECT
- KiCad shows: "C1", "C2", "R1" (proper references)

### Real-World Example

See `examples/stm32g431_simple.py` for a complete working example with:
- Main schematic with 4 hierarchical sheets
- Power supply sheet (voltage regulator)
- MCU sheet (STM32 microcontroller)
- USB sheet (USB-C connector)
- UI sheet (buttons, LEDs, debug header)

Run it:
```bash
python examples/stm32g431_simple.py
```

---

## Part 2: Analyzing Hierarchical Schematics

The `HierarchyManager` provides comprehensive tools for analyzing existing hierarchical KiCAD schematic designs.

## Features Implemented

### 1. **Sheet Reuse Tracking** ✅
Track sheets used multiple times in a design (same schematic file instantiated in different locations).

```python
tree = sch.hierarchy.build_hierarchy_tree(sch)
reused = sch.hierarchy.find_reused_sheets()

for filename, instances in reused.items():
    print(f"{filename} used {len(instances)} times")
```

**Key Methods:**
- `build_hierarchy_tree()` - Build complete hierarchy tree
- `find_reused_sheets()` - Find sheets instantiated multiple times

### 2. **Cross-Sheet Signal Tracking** ✅
Trace signals through hierarchical boundaries.

```python
paths = sch.hierarchy.trace_signal_path("VCC")

for path in paths:
    print(f"Signal: {path.signal_name}")
    print(f"Path: {path.start_path} → {path.end_path}")
    print(f"Sheet crossings: {path.sheet_crossings}")
```

**Key Methods:**
- `trace_signal_path(signal_name, start_path)` - Trace signal through hierarchy
- Returns `SignalPath` objects with routing information

### 3. **Sheet Pin Validation** ✅
Validate sheet pins match hierarchical labels in child schematics.

```python
tree = sch.hierarchy.build_hierarchy_tree(sch, schematic_path)
connections = sch.hierarchy.validate_sheet_pins()

errors = sch.hierarchy.get_validation_errors()
for error in errors:
    print(f"Pin {error['pin_name']}: {error['error']}")
```

**Validation Checks:**
- Sheet pins have matching hierarchical labels
- Pin types are compatible (input/output/bidirectional)
- Pin names match exactly
- No duplicate pins

**Key Methods:**
- `validate_sheet_pins()` - Validate all sheet pin connections
- `get_validation_errors()` - Get detailed validation errors

### 4. **Hierarchy Flattening** ✅
Flatten hierarchical design into single-level representation.

```python
flattened = sch.hierarchy.flatten_hierarchy(prefix_references=True)

print(f"Components: {len(flattened['components'])}")
print(f"Wires: {len(flattened['wires'])}")

# Hierarchy map shows original locations
for ref, path in flattened['hierarchy_map'].items():
    print(f"{ref} was in {path}")
```

**Options:**
- `prefix_references=True` - Prefix component references with sheet path
- `prefix_references=False` - Keep original references

**Key Methods:**
- `flatten_hierarchy(prefix_references)` - Flatten to single level

### 5. **Hierarchy Visualization** ✅
Generate text-based hierarchy tree visualization.

```python
viz = sch.hierarchy.visualize_hierarchy(include_stats=True)
print(viz)

# Output:
# ├── Root (5 components)
# │   ├── PowerSupply [power.kicad_sch] (3 components)
# │   ├── MCU [mcu.kicad_sch] (12 components)
```

**Key Methods:**
- `visualize_hierarchy(include_stats)` - Generate tree visualization
- `get_hierarchy_statistics()` - Get comprehensive statistics

### 6. **Hierarchy Statistics** ✅
Get comprehensive statistics about hierarchical design.

```python
stats = sch.hierarchy.get_hierarchy_statistics()

print(f"Total sheets: {stats['total_sheets']}")
print(f"Max depth: {stats['max_hierarchy_depth']}")
print(f"Reused sheets: {stats['reused_sheets_count']}")
print(f"Components: {stats['total_components']}")
print(f"Wires: {stats['total_wires']}")
print(f"Valid connections: {stats['valid_connections']}")
```

## Architecture

### Core Classes

#### `HierarchyManager`
Main manager class providing all hierarchy operations.

**Key Properties:**
- `_hierarchy_tree` - Root node of hierarchy tree
- `_sheet_instances` - Tracks all sheet instances
- `_loaded_schematics` - Cache of loaded schematics
- `_pin_connections` - Validated sheet pin connections

#### `HierarchyNode`
Represents a node in the hierarchy tree.

**Key Properties:**
- `path` - Hierarchical path (e.g., "/root_uuid/child_uuid/")
- `name` - Sheet name
- `schematic` - Loaded schematic object
- `parent` - Parent node
- `children` - List of child nodes
- `is_root` - Whether this is the root node

**Methods:**
- `get_depth()` - Get depth in hierarchy (root = 0)
- `get_full_path()` - Get full path from root to this node
- `add_child(node)` - Add child node

#### `SheetInstance`
Represents a single instance of a hierarchical sheet.

**Properties:**
- `sheet_uuid` - UUID of sheet symbol
- `sheet_name` - Name of the sheet
- `filename` - Referenced schematic filename
- `path` - Hierarchical path
- `parent_path` - Parent's path
- `schematic` - Loaded schematic object
- `sheet_pins` - List of sheet pins
- `position` - Position on parent schematic

#### `SheetPinConnection`
Represents validated connection between sheet pin and hierarchical label.

**Properties:**
- `sheet_path` - Path to sheet instance
- `sheet_pin_name` - Sheet pin name
- `sheet_pin_type` - Pin type (input/output/bidirectional)
- `hierarchical_label_name` - Matching label name
- `validated` - Whether connection is valid
- `validation_errors` - List of validation errors

#### `SignalPath`
Represents a signal's path through hierarchy.

**Properties:**
- `signal_name` - Name of signal
- `start_path` - Starting hierarchical path
- `end_path` - Ending hierarchical path
- `connections` - List of connection points
- `sheet_crossings` - Number of sheet boundaries crossed

## API Reference

### Building Hierarchy

```python
# Build hierarchy tree from root schematic
tree = sch.hierarchy.build_hierarchy_tree(sch, schematic_path)
```

### Sheet Reuse

```python
# Find sheets used multiple times
reused = sch.hierarchy.find_reused_sheets()
# Returns: Dict[filename, List[SheetInstance]]
```

### Validation

```python
# Validate sheet pins
connections = sch.hierarchy.validate_sheet_pins()
# Returns: List[SheetPinConnection]

# Get validation errors
errors = sch.hierarchy.get_validation_errors()
# Returns: List[Dict[str, Any]]
```

### Signal Tracing

```python
# Trace signal through hierarchy
paths = sch.hierarchy.trace_signal_path("SIGNAL_NAME", start_path="/")
# Returns: List[SignalPath]
```

### Flattening

```python
# Flatten hierarchy
flattened = sch.hierarchy.flatten_hierarchy(prefix_references=True)
# Returns: Dict with 'components', 'wires', 'labels', 'hierarchy_map'
```

### Statistics

```python
# Get statistics
stats = sch.hierarchy.get_hierarchy_statistics()
# Returns: Dict with comprehensive statistics
```

### Visualization

```python
# Visualize hierarchy
viz = sch.hierarchy.visualize_hierarchy(include_stats=True)
# Returns: String representation of tree
```

## Usage Patterns

### Pattern 1: Validate Hierarchical Design

```python
# Load root schematic
sch = ksa.Schematic.load("project.kicad_sch")

# Build hierarchy tree
tree = sch.hierarchy.build_hierarchy_tree(sch, Path("project.kicad_sch"))

# Validate all sheet pins
connections = sch.hierarchy.validate_sheet_pins()

# Check for errors
errors = sch.hierarchy.get_validation_errors()
if errors:
    for error in errors:
        print(f"ERROR: {error['sheet_path']} - {error['pin_name']}: {error['error']}")
```

### Pattern 2: Analyze Reusable Modules

```python
# Build hierarchy
tree = sch.hierarchy.build_hierarchy_tree(sch, sch_path)

# Find reused sheets
reused = sch.hierarchy.find_reused_sheets()

for filename, instances in reused.items():
    print(f"\nModule: {filename}")
    print(f"Used {len(instances)} times:")
    for inst in instances:
        print(f"  - {inst.sheet_name} at {inst.path}")
```

### Pattern 3: Flatten for Analysis

```python
# Build and flatten
tree = sch.hierarchy.build_hierarchy_tree(sch, sch_path)
flattened = sch.hierarchy.flatten_hierarchy(prefix_references=True)

# Analyze flattened design
print(f"Total components: {len(flattened['components'])}")
print(f"Total connections: {len(flattened['wires'])}")

# Map back to original locations
for comp in flattened['components']:
    print(f"{comp['reference']}: {comp['lib_id']} from {comp['hierarchy_path']}")
```

### Pattern 4: Generate Hierarchy Report

```python
# Build hierarchy
tree = sch.hierarchy.build_hierarchy_tree(sch, sch_path)

# Get statistics
stats = sch.hierarchy.get_hierarchy_statistics()

# Generate report
print("=" * 60)
print("HIERARCHY REPORT")
print("=" * 60)
print(f"Total Sheets: {stats['total_sheets']}")
print(f"Max Depth: {stats['max_hierarchy_depth']}")
print(f"Reused Sheets: {stats['reused_sheets_count']}")
print(f"Total Components: {stats['total_components']}")
print(f"Total Wires: {stats['total_wires']}")
print(f"\nHierarchy Tree:")
print(sch.hierarchy.visualize_hierarchy(include_stats=True))
```

## Testing

### Test Coverage

**19 comprehensive unit tests covering:**
- ✅ Hierarchy tree building (3 tests)
- ✅ Sheet reuse detection (2 tests)
- ✅ Sheet pin validation (3 tests)
- ✅ Hierarchy flattening (2 tests)
- ✅ Hierarchy statistics (2 tests)
- ✅ Hierarchy visualization (2 tests)
- ✅ Signal tracing (2 tests)
- ✅ Edge cases (3 tests)

**All tests passing:** `pytest tests/unit/test_hierarchy_manager.py -v`

## Examples

Complete examples available in: `examples/hierarchy_example.py`

Run examples:
```bash
python examples/hierarchy_example.py
```

## Implementation Notes

### Design Decisions

1. **Tree-Based Structure**: Hierarchy represented as tree of `HierarchyNode` objects for efficient traversal and depth calculation.

2. **Lazy Loading**: Child schematics loaded on-demand during tree building, reducing memory usage for large projects.

3. **Validation Caching**: Sheet pin validation results cached in `_pin_connections` for repeated access without re-validation.

4. **Path-Based Tracking**: Hierarchical paths use KiCAD's UUID-based format (`/root_uuid/child_uuid/`) for precise tracking.

5. **Flexible Flattening**: Flattening creates data representation only (not real schematic), preserving original hierarchy information in `hierarchy_map`.

### Performance Considerations

- **Tree building**: O(n) where n is total number of sheets
- **Sheet reuse detection**: O(n) lookup in `_sheet_instances` dictionary
- **Validation**: O(m × p) where m is sheets, p is pins per sheet
- **Flattening**: O(n × c) where n is sheets, c is components per sheet
- **Signal tracing**: O(n × l) where n is sheets, l is labels per sheet

## Integration

### With ConnectivityAnalyzer

HierarchyManager complements `ConnectivityAnalyzer` by providing:
- Sheet structure and navigation
- Pin validation before connectivity analysis
- Flattened view for simplified connectivity tracing

### With SheetManager

HierarchyManager extends `SheetManager` with:
- Multi-level hierarchy tracking
- Reuse detection
- Cross-sheet analysis
- SheetManager: Basic sheet operations
- HierarchyManager: Advanced hierarchy analysis

## Limitations

1. **File System Dependency**: Requires actual schematic files to exist for loading child schematics.

2. **Memory Usage**: Loading large hierarchies loads all schematics into memory.

3. **Circular References**: Does not detect circular sheet references (A includes B includes A).

4. **Read-Only**: Hierarchy analysis is read-only; modifications must be made through `SheetManager`.

## Future Enhancements

Potential improvements (not in scope of #37):

1. **Circular Reference Detection**: Detect and report circular sheet dependencies
2. **Hierarchy Editing**: Modify hierarchy structure programmatically
3. **Diff/Merge**: Compare and merge hierarchical designs
4. **Export Formats**: Export hierarchy to other formats (JSON, DOT, etc.)
5. **Incremental Loading**: Load hierarchy incrementally for very large designs
6. **Cache Management**: Persistent caching of hierarchy analysis results

## See Also

- **SheetManager**: `kicad_sch_api/core/managers/sheet.py` - Basic sheet operations
- **ConnectivityAnalyzer**: `kicad_sch_api/core/connectivity.py` - Network connectivity
- **Examples**: `examples/hierarchy_example.py` - Usage examples
- **Tests**: `tests/unit/test_hierarchy_manager.py` - Test coverage

## Changelog

**v0.4.6** (2025-11-05)
- ✅ Implemented `HierarchyManager` class
- ✅ Added 19 comprehensive unit tests
- ✅ Integrated with `Schematic` class via `sch.hierarchy` property
- ✅ Created usage examples and documentation
- ✅ All tests passing

---

**Status:** Issue #37 - ✅ Complete

For questions or issues, please refer to the GitHub repository.
