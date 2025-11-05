# Advanced Hierarchy Management

**Implementation Date:** 2025-11-05
**Issue:** #37 - Advanced hierarchy and sheet management (2.7)
**Status:** ✅ Complete

## Overview

The `HierarchyManager` provides comprehensive tools for managing complex hierarchical KiCAD schematic designs, addressing limitations in basic hierarchy support.

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
