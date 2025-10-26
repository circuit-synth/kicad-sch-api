# ICManager - Multi-Unit IC Component Management

## Overview

`ICManager` is a specialized component manager for handling multi-unit integrated circuits (ICs) like op-amps, logic gates, and other complex components with multiple functional units.

**Status**: ✅ **ACTIVE AND INTEGRATED**

## Purpose

ICManager handles the complexity of multi-unit ICs by:
- Automatically detecting and placing component units
- Managing unit-specific positioning and properties
- Generating properly-named component references (U1A, U1B, U1C, etc.)
- Providing intelligent layout algorithms for unit placement

## Key Features

### 1. Automatic Unit Detection
- Scans symbol library to detect available units
- Extracts unit information from KiCAD symbol definitions
- Works with standard KiCAD multi-unit symbol format

### 2. Intelligent Unit Placement
- **Vertical Layout**: Stacks units vertically with configurable spacing
- **Power Unit Handling**: Separates power units (typically unit 5) with offset
- **Professional Spacing**: Uses grid-based alignment for clean layouts

### 3. Unit Reference Generation
- Automatically generates unit references (A, B, C, D, etc.)
- Handles power units separately (e.g., U1A-U1D for logic, U1E for power)
- Customizable reference prefixes

### 4. Position Override
- Override default positions for specific units
- Useful for custom layouts or special requirements
- Updates component positions in real-time

## Usage

### Basic Usage - Auto-Layout

```python
import kicad_sch_api as ksa

sch = ksa.create_schematic("Multi-Unit IC Example")

# Add a 7400 quad NAND gate IC with auto-layout
# Automatically creates U1A, U1B, U1C, U1D (gates) and U1E (power)
ic_manager = sch.components.add_ic(
    lib_id="74xx:7400",
    reference_prefix="U1",
    position=(100, 100),
    value="7400"
)

# Inspect unit positions
positions = ic_manager.get_all_units()
print(f"Unit positions: {positions}")
# Output: {1: Point(100, 100), 2: Point(100, 112.7), 3: Point(100, 125.4), ...}
```

### Custom Unit Positioning

```python
# Override position of specific unit
ic_manager.place_unit(1, position=(150, 80))  # Move Gate A to different location

# Get position of specific unit
gate_a_pos = ic_manager.get_unit_position(1)
print(f"Gate A is at: {gate_a_pos}")

# Get all unit references
references = ic_manager.get_unit_references()
print(f"Unit references: {references}")
# Output: {1: 'U1A', 2: 'U1B', 3: 'U1C', 4: 'U1D', 5: 'U1E'}
```

## Common IC Types

### Logic ICs (74xx series)
- **Units**: Typically 1-4 (logic gates) + 5 (power)
- **Spacing**: Tight vertical spacing (grid.unit_spacing = 12.7 mm)
- **Example**: 7400 (Quad NAND), 7404 (Hex NOT), 7408 (Quad AND)

```python
# Add a 7404 hex NOT gate
u1 = sch.components.add_ic("74xx:7404", "U1", position=(100, 100))
# Creates: U1A, U1B, U1C, U1D, U1E, U1F (6 gates) + power unit
```

### Operational Amplifiers (Dual Op-Amp)
- **Units**: Typically 1-2 (op-amp channels) + 3 (power)
- **Example**: LM358 (Dual General-Purpose Op-Amp)

```python
# Add a dual op-amp
u2 = sch.components.add_ic("Amplifier_Operational:LM358", "U2", position=(200, 100))
# Creates: U2A (op-amp 1), U2B (op-amp 2), U2C (power)
```

## Configuration

ICManager uses configuration from `core/config.py`:

```python
from kicad_sch_api.core.config import config

# Customize unit spacing
config.grid.unit_spacing = 12.7  # Default: 12.7 mm (0.5 inch)

# Customize power unit offset
config.grid.power_offset = (25.4, 0.0)  # Default: (25.4 mm, 0)
```

## Integration with Component Manager

ICManager is integrated into `ComponentCollection.add_ic()` method:

```python
class ComponentCollection:
    def add_ic(
        self,
        lib_id: str,
        reference_prefix: str,
        position: Optional[Union[Point, Tuple[float, float]]] = None,
        value: str = "",
        footprint: Optional[str] = None,
        layout_style: str = "vertical",
        **properties,
    ) -> ICManager:
        """Add multi-unit IC with automatic unit placement."""
        # ... implementation uses ICManager internally
```

## How It Works

### 1. Initialization
```
add_ic() called → ICManager.__init__()
  └─ _detect_available_units() - Read from symbol library
  └─ _auto_layout_units() - Calculate unit positions
```

### 2. Component Generation
```
generate_components() called
  ├─ For each unit:
  │  ├─ Calculate position (base + spacing)
  │  ├─ Generate unit reference (U1A, U1B, etc.)
  │  └─ Create SchematicSymbol with unit number
  └─ Add all units to ComponentCollection
```

### 3. Position Management
```
place_unit(unit, position) called
  ├─ Update internal position dictionary
  ├─ If component exists, update its position
  └─ Mark collection as modified
```

## Known Limitations

### 1. Hardcoded Unit Assumptions
- Currently assumes units 1-4 for logic, 5 for power
- Works well for standard 74xx ICs and dual op-amps
- May need customization for unusual IC configurations

### 2. Layout Styles
- Only vertical layout is currently implemented
- `layout_style` parameter is reserved for future enhancements
- Grid and functional layouts not yet implemented

### 3. Unit Detection
- Unit detection from symbol library is partially implemented
- Currently falls back to default unit assumptions
- May fail for non-standard symbol definitions

## Future Enhancements

1. **Grid Layout Support**: Arrange units in 2D grid (e.g., 2x4 for 8-gate IC)
2. **Functional Layout**: Group units by function (logic + power clusters)
3. **Smart Symbol Parsing**: Better detection of unit definitions from KiCAD library
4. **Unit Custom Names**: Support ICs with custom unit labels (e.g., "LEFT_HALF", "RIGHT_HALF")
5. **Layout Preview**: Visualize unit layout before commitment

## Testing

ICManager is tested through:
- Component integration tests (ComponentCollection)
- Reference generation tests
- Position override tests

Current test coverage: 20% (see TEST_COVERAGE_GAPS.md)

To improve coverage, consider adding tests for:
- Multi-unit IC generation
- Layout algorithms
- Symbol library unit detection
- Position override functionality

## Related Files

- **Implementation**: `kicad_sch_api/core/ic_manager.py`
- **Integration**: `kicad_sch_api/core/components.py` (add_ic method)
- **Configuration**: `kicad_sch_api/core/config.py` (GridSettings)
- **Types**: `kicad_sch_api/core/types.py` (SchematicSymbol, Point)

## See Also

- [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md)
- [TEST_COVERAGE_GAPS.md](TEST_COVERAGE_GAPS.md)
- [README.md](README.md#advanced-features)
