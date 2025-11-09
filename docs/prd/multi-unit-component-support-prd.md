# PRD: Multi-Unit Component Support (Issue #107)

## Overview

Add support for multi-unit components (dual/quad op-amps, logic gates, matched transistors) with automatic unit addition and manual position control. Currently, only the first unit is added when creating multi-unit components, making them unusable for designs requiring multiple gates/amplifiers.

## Problem Statement

When adding multi-unit components like the TL072 dual op-amp:
```python
sch.components.add("Amplifier_Operational:TL072", "U1", "TL072")
```

**Current behavior:**
- Only unit 1 (first op-amp) is added to schematic
- Units 2 and 3 (second op-amp, power pins) are missing
- Component cannot be used for dual op-amp circuits

**Expected behavior:**
- Easy way to add all units with automatic placement
- Option for manual unit-by-unit addition with explicit positions
- LLMs can discover how many units a component has
- All units share same reference ("U1") with different unit numbers

## Success Criteria

- [ ] Multi-unit components can be added with all units in a single call
- [ ] Individual units can be added manually with explicit unit numbers
- [ ] Symbol library can be queried for unit count and names
- [ ] Automatic layout provides sensible default positions
- [ ] Manual position override supported for each unit
- [ ] MCP server exposes multi-unit functionality
- [ ] Documentation includes multi-unit workflow examples
- [ ] All tests pass including new multi-unit tests
- [ ] Format preservation validated against KiCAD reference schematics
- [ ] Backward compatible with existing `unit` parameter

## Functional Requirements

### REQ-1: Automatic Multi-Unit Addition

Add `add_all_units` parameter to `ComponentCollection.add()`:

```python
# Automatic: Add all units with default layout
u1 = sch.components.add(
    "Amplifier_Operational:TL072",
    reference="U1",
    value="TL072",
    position=(100, 100),
    add_all_units=True,  # NEW PARAMETER
    unit_spacing=25.4    # Optional: spacing between units in mm (default: 25.4mm = 1 inch)
)
# Returns: MultiUnitComponentGroup with all 3 units
# Result: U1 unit=1 at (100, 100), U1 unit=2 at (125.4, 100), U1 unit=3 at (150.8, 100)
```

**Behavior:**
- Query symbol library for unit count
- Add each unit with same reference, different unit number
- Auto-place units horizontally with configurable spacing
- Return `MultiUnitComponentGroup` object for position overrides
- Default `add_all_units=False` for backward compatibility

### REQ-2: Manual Unit Addition

Keep existing explicit `unit` parameter approach:

```python
# Manual: Add each unit individually with explicit positions
sch.components.add("Amplifier_Operational:TL072", "U1", "TL072",
                   position=(100, 100), unit=1)  # First op-amp
sch.components.add("Amplifier_Operational:TL072", "U1", "TL072",
                   position=(150, 100), unit=2)  # Second op-amp
sch.components.add("Amplifier_Operational:TL072", "U1", "TL072",
                   position=(125, 150), unit=3)  # Power pins
```

**Behavior:**
- Same reference for all units (e.g., "U1")
- Different unit numbers (1, 2, 3, ...)
- Explicit position control per unit
- Existing parameter, no changes needed

### REQ-3: Position Override for Auto-Placed Units

`MultiUnitComponentGroup` allows position overrides after auto-placement:

```python
# Auto-add all units
u1 = sch.components.add("Amplifier_Operational:TL072", "U1", "TL072",
                        position=(100, 100), add_all_units=True)

# Override individual unit positions
u1.place_unit(2, (175, 100))  # Move unit 2
u1.place_unit(3, (137.5, 150))  # Move unit 3 (power) below

# Access individual units
unit_1 = u1.get_unit(1)  # Returns Component wrapper
unit_2 = u1.get_unit(2)

# Get all unit positions
positions = u1.get_all_positions()  # {1: Point(100, 100), 2: Point(175, 100), ...}
```

### REQ-4: Symbol Library Introspection

Add `get_symbol_info()` method to query symbol metadata:

```python
# Query symbol for unit information
info = sch.library.get_symbol_info("Amplifier_Operational:TL072")

# Returns SymbolInfo object with:
print(f"Units: {info.unit_count}")           # 3
print(f"Unit names: {info.unit_names}")       # {1: "A", 2: "B", 3: "C"}
print(f"Description: {info.description}")     # "Dual Low-Noise JFET-Input..."
print(f"Reference prefix: {info.reference_prefix}")  # "U"
print(f"Pins per unit: {info.pins}")         # List of pins for each unit

# LLM usage pattern:
symbol_info = sch.library.get_symbol_info("Amplifier_Operational:TL072")
for unit in range(1, symbol_info.unit_count + 1):
    sch.components.add("Amplifier_Operational:TL072", "U1", "TL072",
                       position=(100 + unit * 25.4, 100), unit=unit)
```

**SymbolInfo dataclass:**
```python
@dataclass
class SymbolInfo:
    lib_id: str
    name: str
    library: str
    reference_prefix: str
    description: str
    keywords: str
    datasheet: str
    unit_count: int                    # Number of units (1 for single-unit, 3 for TL072)
    unit_names: Dict[int, str]         # {1: "A", 2: "B", 3: "C"}
    pins: List[SchematicPin]           # All pins across all units
    power_symbol: bool
```

### REQ-5: MCP Server Tool Updates

Update `add_component` MCP tool:

```json
{
  "tool": "add_component",
  "arguments": {
    "lib_id": "Amplifier_Operational:TL072",
    "reference": "U1",
    "value": "TL072",
    "position": [100, 100],
    "unit": 1,                    // Existing: explicit unit number
    "add_all_units": false,       // NEW: auto-add all units
    "unit_spacing": 25.4          // NEW: spacing for auto-layout (mm)
  }
}
```

Add new `get_symbol_info` MCP tool:

```json
{
  "tool": "get_symbol_info",
  "arguments": {
    "lib_id": "Amplifier_Operational:TL072"
  },
  "returns": {
    "lib_id": "Amplifier_Operational:TL072",
    "unit_count": 3,
    "unit_names": {"1": "A", "2": "B", "3": "C"},
    "reference_prefix": "U",
    "description": "Dual Low-Noise JFET-Input Operational Amplifier"
  }
}
```

## KiCAD Format Specifications

### Multi-Unit Component S-Expression Structure

Each unit is a separate `(symbol ...)` entry with **same reference, different unit number**:

```scheme
;; Unit 1 (First op-amp)
(symbol (lib_id "Amplifier_Operational:TL072")
  (at 100 100 0)
  (unit 1)  ;; Unit number
  (uuid "uuid-1")
  (property "Reference" "U1" ...)
  (property "Value" "TL072" ...)
  (instances
    (project "MyProject"
      (path "/root"
        (reference "U1")    ;; Same reference for all units
        (unit 1)))))        ;; Unit number

;; Unit 2 (Second op-amp)
(symbol (lib_id "Amplifier_Operational:TL072")
  (at 125.4 100 0)
  (unit 2)  ;; Different unit number
  (uuid "uuid-2")  ;; Different UUID
  (property "Reference" "U1" ...)  ;; SAME reference
  (property "Value" "TL072" ...)
  (instances
    (project "MyProject"
      (path "/root"
        (reference "U1")    ;; Same reference
        (unit 2)))))        ;; Different unit

;; Unit 3 (Power pins)
(symbol (lib_id "Amplifier_Operational:TL072")
  (at 150.8 100 0)
  (unit 3)
  (uuid "uuid-3")
  (property "Reference" "U1" ...)  ;; SAME reference
  (property "Value" "TL072" ...)
  (instances
    (project "MyProject"
      (path "/root"
        (reference "U1")
        (unit 3)))))
```

**Critical Format Requirements:**
- Each unit is a separate `(symbol ...)` S-expression
- All units have the **same reference** (e.g., "U1")
- Each unit has a **different unit number** (1, 2, 3, ...)
- Each unit has a **unique UUID**
- Each unit has its own position (`at` field)
- Instances section contains same reference with unit number

### Version Compatibility

- KiCAD 7.0+: Supports multi-unit components
- KiCAD 8.0+: Same format, fully compatible

## Technical Constraints

### TC-1: Backward Compatibility

- Existing `unit` parameter in `add()` remains unchanged (default: `unit=1`)
- Existing code continues to work without modification
- New `add_all_units` parameter defaults to `False`

### TC-2: Reference Validation

- When adding unit N of reference "U1", validate that:
  - If other units of "U1" exist, they must have the same `lib_id`
  - Unit numbers must be unique per reference
  - Unit number must be valid for the symbol (1 ≤ unit ≤ unit_count)

### TC-3: Format Preservation

- Each unit preserves its own S-expression structure
- UUIDs are unique per unit (not shared)
- Instances section correctly reflects reference and unit number
- Round-trip load/save preserves all unit data

### TC-4: ICManager Analysis

**Current ICManager Issues:**
1. Uses incorrect unit naming (U1A, U1B vs. U1 unit=1, U1 unit=2)
2. Hard-coded for 74xx logic ICs (units 1-5)
3. Complex auto-layout logic that's not flexible

**Recommendation: Create New MultiUnitComponentGroup**

Replace `ICManager` with simpler `MultiUnitComponentGroup`:

```python
class MultiUnitComponentGroup:
    """Manages multiple units of a single multi-unit component."""

    def __init__(self, reference: str, lib_id: str, components: List[Component]):
        self.reference = reference
        self.lib_id = lib_id
        self._units: Dict[int, Component] = {c._data.unit: c for c in components}

    def get_unit(self, unit: int) -> Optional[Component]:
        """Get component for specific unit number."""
        return self._units.get(unit)

    def place_unit(self, unit: int, position: Union[Point, Tuple[float, float]]):
        """Move a specific unit to new position."""
        if unit in self._units:
            self._units[unit].position = position

    def get_all_positions(self) -> Dict[int, Point]:
        """Get positions of all units."""
        return {unit: comp.position for unit, comp in self._units.items()}

    def get_all_units(self) -> List[Component]:
        """Get all unit components."""
        return list(self._units.values())

    def __len__(self) -> int:
        return len(self._units)

    def __iter__(self):
        return iter(self._units.values())
```

**Benefits over ICManager:**
- Simpler design focused on position management
- No assumptions about unit naming or IC type
- Works with any multi-unit component (op-amps, gates, transistors)
- Clean API for position overrides

**Migration Strategy:**
- Deprecate `add_ic()` method in ComponentCollection
- Keep ICManager for backward compatibility but mark as deprecated
- Document migration path in CHANGELOG

## Reference Schematic Requirements

### Reference 1: TL072 Dual Op-Amp (All Units)

**Purpose:** Validate all 3 units of TL072 can be added and positioned correctly

**Contents:**
- U1 unit 1 at (100, 100) - First op-amp
- U1 unit 2 at (150, 100) - Second op-amp
- U1 unit 3 at (125, 150) - Power pins

**Validation:**
- All 3 units have reference "U1"
- Unit numbers are 1, 2, 3
- Each unit has unique UUID
- Positions are grid-aligned
- Instances section correct for each unit

### Reference 2: 74HC00 Quad NAND Gate

**Purpose:** Validate 5-unit component (4 gates + power)

**Contents:**
- U2 unit 1-4 (NAND gates) in vertical column
- U2 unit 5 (power pins) offset to the right

**Expected format:** Same reference "U2", units 1-5

### Reference 3: Mixed Single and Multi-Unit

**Purpose:** Validate single-unit and multi-unit components coexist

**Contents:**
- R1 (single-unit resistor) - unit 1
- U1 (TL072, 3 units) - units 1, 2, 3
- C1 (single-unit capacitor) - unit 1

**Validation:** No conflicts, correct unit numbering

## Edge Cases

### EC-1: Adding Duplicate Unit

**Scenario:** User tries to add U1 unit 2 when U1 unit 2 already exists

**Expected:** Raise `ValidationError` with clear message:
```
ValidationError: Unit 2 of reference 'U1' already exists in schematic
```

### EC-2: Invalid Unit Number

**Scenario:** User adds unit 99 of TL072 (which only has 3 units)

**Expected:** Raise `ValidationError`:
```
ValidationError: Unit 99 invalid for symbol 'Amplifier_Operational:TL072'
(valid units: 1-3)
```

### EC-3: Mismatched lib_id for Same Reference

**Scenario:**
```python
sch.components.add("Device:R", "U1", "10k", unit=1)  # Wrong lib_id
sch.components.add("Amplifier_Operational:TL072", "U1", "TL072", unit=2)
```

**Expected:** Raise `ValidationError`:
```
ValidationError: Reference 'U1' already exists with different lib_id
'Device:R' (attempting to add 'Amplifier_Operational:TL072')
```

### EC-4: Empty Unit Names

**Scenario:** Symbol library has units but no unit names

**Expected:** Generate default names:
```python
{1: "1", 2: "2", 3: "3"}  # Fallback to unit numbers as strings
```

### EC-5: add_all_units=True for Single-Unit Component

**Scenario:**
```python
sch.components.add("Device:R", "R1", "10k", add_all_units=True)
```

**Expected:** Add only unit 1 (no error, behaves like normal resistor)

## Impact Analysis

### Parser Changes

**File:** `kicad_sch_api/parsers/elements/symbol_parser.py`

**Changes:** None required - parser already handles `unit` field correctly

**Validation:** Verify unit field is parsed and preserved in round-trip

### Formatter Changes

**File:** `kicad_sch_api/parsers/elements/symbol_parser.py`

**Changes:** None required - formatter already emits `(unit N)` correctly

**Validation:** Verify multi-unit components format correctly

### Type Changes

**File:** `kicad_sch_api/core/types.py`

**New dataclass:** `SymbolInfo` (for library introspection)

```python
@dataclass
class SymbolInfo:
    """Symbol metadata from library cache."""
    lib_id: str
    name: str
    library: str
    reference_prefix: str
    description: str
    keywords: str
    datasheet: str
    unit_count: int
    unit_names: Dict[int, str]
    pins: List[SchematicPin]
    power_symbol: bool
```

**New class:** `MultiUnitComponentGroup` (for managing multi-unit components)

### Collection Changes

**File:** `kicad_sch_api/collections/components.py`

**ComponentCollection.add() signature:**
```python
def add(
    self,
    lib_id: str,
    reference: Optional[str] = None,
    value: str = "",
    position: Optional[Union[Point, Tuple[float, float]]] = None,
    footprint: Optional[str] = None,
    unit: int = 1,  # EXISTING
    add_all_units: bool = False,  # NEW
    unit_spacing: float = 25.4,   # NEW (default: 1 inch in mm)
    rotation: float = 0.0,
    component_uuid: Optional[str] = None,
    grid_units: Optional[bool] = None,
    grid_size: Optional[float] = None,
    **properties,
) -> Union[Component, MultiUnitComponentGroup]:  # NEW: conditional return type
```

**New method:** `ComponentCollection._add_multi_unit()`

**New validation:** Check for duplicate units, invalid unit numbers, mismatched lib_id

### Library Cache Changes

**File:** `kicad_sch_api/library/cache.py`

**New method:** `SymbolLibraryCache.get_symbol_info(lib_id: str) -> SymbolInfo`

**Purpose:** Public API to query symbol metadata including unit information

**Implementation:** Wrapper around existing `get_symbol()` that returns SymbolInfo dataclass

### MCP Server Changes

**File:** `mcp_server/tools/component_tools.py`

**Updated tool:** `add_component` - add `unit`, `add_all_units`, `unit_spacing` parameters

**New tool:** `get_symbol_info` - query symbol unit information

## Out of Scope

- Custom unit naming (e.g., "OpAmp1", "OpAmp2") - use KiCAD's numeric units
- Advanced auto-layout algorithms (grid, functional grouping) - simple horizontal is sufficient
- Unit-aware connectivity analysis - handled by existing connectivity features
- Visual rendering of multi-unit components - KiCAD handles this
- Unit exchange/swapping - advanced feature for future consideration
- De Morgan equivalent units - KiCAD library feature, not API concern

## Acceptance Criteria

- [ ] `add()` with `add_all_units=True` adds all units with auto-placement
- [ ] `add()` with explicit `unit` parameter adds individual units (existing functionality)
- [ ] `MultiUnitComponentGroup` supports position overrides via `place_unit()`
- [ ] `get_symbol_info()` returns unit count and names
- [ ] Reference validation prevents duplicate units and mismatched lib_id
- [ ] Unit number validation ensures units are valid for symbol
- [ ] MCP server exposes `add_all_units` and `get_symbol_info`
- [ ] Documentation includes TL072, 74HC00, and SSM2212 examples
- [ ] Reference schematics validate format preservation
- [ ] All unit tests pass (existing + new)
- [ ] Reference tests verify exact KiCAD format matching
- [ ] Integration tests verify multi-unit connectivity
- [ ] ICManager deprecation documented with migration path
- [ ] Backward compatibility maintained (existing code works unchanged)

## Common Multi-Unit Components

For testing and documentation:

| Component | Units | Description | Unit Names |
|-----------|-------|-------------|------------|
| TL072 | 3 | Dual op-amp (2 amps + power) | A, B, C |
| LM358 | 3 | Dual op-amp (2 amps + power) | A, B, C |
| TL074 | 5 | Quad op-amp (4 amps + power) | A, B, C, D, E |
| 74HC00 | 5 | Quad 2-input NAND (4 gates + power) | A, B, C, D, E |
| 74HC08 | 5 | Quad 2-input AND (4 gates + power) | A, B, C, D, E |
| CD4011 | 5 | Quad 2-input NAND (4 gates + power) | A, B, C, D, E |
| SSM2212 | 2 | Dual matched transistor | A, B |

## Timeline Estimate

- **PRD Review**: 30 minutes
- **Reference Schematic Creation**: 1-2 hours (3 reference schematics)
- **Test Generation**: 2-3 hours (unit + reference + integration tests)
- **Implementation**: 4-6 hours
  - `MultiUnitComponentGroup` class: 1 hour
  - `add()` method updates: 1 hour
  - `get_symbol_info()` implementation: 1 hour
  - Validation logic: 1 hour
  - MCP server updates: 1 hour
  - Documentation: 1 hour
- **Manual Validation**: 1 hour
- **Cleanup & PR**: 1 hour

**Total**: 9-13 hours

## References

- Issue #107: https://github.com/circuit-synth/kicad-sch-api/issues/107
- KiCAD Symbol Library Format: https://dev-docs.kicad.org/en/file-formats/sexpr-intro/
- Existing `ICManager`: `kicad_sch_api/core/ic_manager.py`
- Existing `unit` support: `kicad_sch_api/core/types.py` line 221
