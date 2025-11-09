# PRD: Complete Component Property Preservation

## Overview

Implement complete property preservation for component symbols during round-trip operations (load → save → load). The current implementation preserves Reference, Value, and Footprint properties but needs systematic handling of ALL properties including custom user-defined properties (MPN, Manufacturer, Tolerance, etc.) with visibility state tracking.

## Success Criteria

- [x] All component properties are imported from KiCAD schematics
- [x] All property visibility states (hidden/visible) are preserved
- [x] Custom properties survive round-trip unchanged
- [x] Simple API for getting/setting property visibility
- [x] Helper methods for adding properties with visibility control
- [x] Byte-perfect or semantically equivalent round-trip output
- [x] All tests pass
- [x] Format preservation validated against reference schematic

## Functional Requirements

### REQ-1: Import All Properties from KiCAD Schematic

When loading a `.kicad_sch` file, extract ALL component properties:
- Standard properties: Reference, Value, Footprint, Datasheet, Description
- KiCAD metadata properties: ki_keywords, ki_description, ki_fp_filters
- Custom user-defined properties: MPN, Manufacturer, Tolerance, Supplier, etc.
- Store property values in `component.properties` dict

### REQ-2: Extract Property Visibility State

Parse the `(hide yes)` flag from each property's S-expression:
- Properties with `(effects ... (hide yes))` → add to `hidden_properties` set
- Properties without hide flag → not in `hidden_properties` set
- Populate `component.hidden_properties` set during load

### REQ-3: Preserve Property S-Expressions

Maintain existing S-expression preservation system:
- Store original S-expression as `__sexp_{PropertyName}` in properties dict
- Preserve all metadata: position, rotation, font, color, justify, effects
- Use preserved S-expression for round-trip output

### REQ-4: Get Property Visibility State

Provide simple API to check if property is hidden:
```python
is_hidden = "MPN" in component.hidden_properties
is_visible = "MPN" not in component.hidden_properties
```

### REQ-5: Set Property Visibility State

Allow users to show/hide existing properties:
```python
component.hidden_properties.add("MPN")  # Hide
component.hidden_properties.discard("MPN")  # Show
component.hidden_properties.remove("MPN")  # Show (raises if not present)
```

### REQ-6: Add Properties with Visibility Control

Provide helper methods for adding new properties:
```python
# Single property
component.add_property("Supplier", "Digikey", hidden=True)

# Multiple properties
component.add_properties({
    "Supplier": "Digikey",
    "Cost": "$0.10"
}, hidden=True)
```

### REQ-7: Emit Properties with Correct Visibility

When saving to `.kicad_sch`, emit properties with correct hide flag:
- Properties in `hidden_properties` → include `(hide yes)` in effects
- Properties NOT in `hidden_properties` → no hide flag (visible)
- Use preserved S-expression when available
- Generate new S-expression for newly added properties

### REQ-8: Preserve Property Ordering

Maintain property order from original file:
- Standard properties first: Reference, Value, Footprint, Datasheet
- Custom properties in original order
- Newly added properties appended at end

## KiCAD Format Specifications

### Property S-Expression Structure

```lisp
(property "PropertyName" "value"
  (at x y rotation)
  (effects
    (font (size 1.27 1.27))
    (justify left)
    (hide yes)  ; Optional - presence indicates hidden
  )
)
```

### Standard Properties

- **Reference**: Component designator (R1, C1, U1) - usually visible
- **Value**: Component value (10k, 100nF, TL072) - usually visible
- **Footprint**: PCB footprint identifier - usually hidden
- **Datasheet**: Datasheet URL or "~" for none - usually hidden

### Custom Properties

Any user-defined property name:
- MPN (Manufacturer Part Number)
- Manufacturer
- Tolerance
- Power
- Voltage
- Supplier
- Supplier_PN
- Cost
- Notes
- Any other custom name

### Visibility Flag

- **Hidden**: `(hide yes)` appears in effects section
- **Visible**: No hide flag present in effects (or `(hide no)` in some KiCAD versions)

### Version Compatibility

- KiCAD 7.0+: Uses `(hide yes)` syntax
- KiCAD 8.0+: Same syntax
- Format preservation must work for both versions

## Technical Constraints

### Backward Compatibility

- Existing `component.properties` dict access must continue working
- Existing S-expression preservation system (`__sexp_*`) must remain intact
- No breaking changes to public API
- Components without `hidden_properties` should default to empty set

### Format Preservation

- Byte-perfect output when possible
- Preserve all property metadata: position, rotation, font, justify, color
- Preserve property order from original file
- Only modify visibility flag when explicitly changed by user

### Performance

- Property lookup must remain O(1) via dict access
- Visibility check must be O(1) via set membership test
- No performance degradation for schematics with many properties

## Reference Schematic Requirements

Create reference schematic demonstrating property preservation:

### Reference 1: Component with Custom Properties

Single resistor with multiple custom properties:
- Standard properties: Reference="R1", Value="10k", Footprint="Resistor_SMD:R_0603_1608Metric", Datasheet="~"
- Custom properties: MPN="RC0603FR-0710KL", Manufacturer="Yageo", Tolerance="1%"
- Visibility: Reference and Value visible, all others hidden
- Position: (100, 100) with rotation=0

**Expected S-expression snippet:**
```lisp
(symbol
  (lib_id "Device:R")
  (at 100 100 0)
  (property "Reference" "R1" (at ...) (effects ...))
  (property "Value" "10k" (at ...) (effects ...))
  (property "Footprint" "Resistor_SMD:R_0603_1608Metric" (at ...) (effects ... (hide yes)))
  (property "Datasheet" "~" (at ...) (effects ... (hide yes)))
  (property "MPN" "RC0603FR-0710KL" (at ...) (effects ... (hide yes)))
  (property "Manufacturer" "Yageo" (at ...) (effects ... (hide yes)))
  (property "Tolerance" "1%" (at ...) (effects ...))
)
```

### Reference 2: Multiple Components with Different Properties

- R1: Has MPN, Manufacturer
- C1: Has Voltage, Tolerance
- U1: Has Datasheet, Notes

This validates that different components can have different custom properties.

## Edge Cases

### EC-1: Empty Property Values

Properties with empty string values must be preserved:
```python
component.properties["Datasheet"] = ""  # Not "~", but ""
# Should emit: (property "Datasheet" "" ...)
```

### EC-2: Special Characters in Values

Properties with quotes, newlines, unicode:
```python
component.properties["Notes"] = 'Use "high quality" parts'
# Should escape quotes: (property "Notes" "Use \"high quality\" parts" ...)
```

### EC-3: Missing Visibility State

When loading old schematics without explicit hide flags:
- Assume standard behavior: Reference/Value visible, others hidden
- Or preserve absence of hide flag

### EC-4: Conflicting Visibility State

If S-expression has `(hide yes)` but property not in `hidden_properties`:
- User explicitly made visible → remove `(hide yes)` when saving
- Priority: `hidden_properties` set is source of truth

### EC-5: Property Name Collisions

Reserved internal names:
- Properties starting with `__sexp_` are internal (already handled)
- No user property should start with `__`

### EC-6: Adding Property That Already Exists

```python
component.add_property("MPN", "NewValue", hidden=False)
# Should update value and visibility, not create duplicate
```

### EC-7: Removing Properties

```python
del component.properties["MPN"]
component.hidden_properties.discard("MPN")  # Clean up visibility tracking
# Or: automatic cleanup when property deleted
```

## Impact Analysis

### Parser Changes

File: `kicad_sch_api/parsers/elements/symbol_parser.py`

**Current state:**
- Lines 64-83: Parses properties, stores S-expression as `__sexp_{PropertyName}`
- Lines 72-77: Extracts Reference, Value, Footprint
- Lines 78-83: Stores other properties in `properties` dict

**Required changes:**
- Extract `(hide yes)` flag from property S-expression
- Populate `hidden_properties` set during parsing
- Example:
```python
# In _parse_property method
def _parse_property(self, item):
    # ... existing parsing ...

    # NEW: Extract hide flag from effects
    effects = find_clause(item, 'effects')
    is_hidden = False
    if effects:
        hide_clause = find_clause(effects, 'hide')
        if hide_clause and len(hide_clause) > 1:
            is_hidden = parse_bool_property(hide_clause[1])

    return {
        "name": prop_name,
        "value": prop_value,
        "hidden": is_hidden  # NEW
    }
```

### Type Changes

File: `kicad_sch_api/core/types.py`

**Current state:**
- Line 216: `properties: Dict[str, str] = field(default_factory=dict)`

**Required changes:**
- Add `hidden_properties` field to `SchematicSymbol` dataclass
- Add `add_property()` helper method
- Add `add_properties()` helper method

```python
@dataclass
class SchematicSymbol:
    # ... existing fields ...
    properties: Dict[str, str] = field(default_factory=dict)
    hidden_properties: Set[str] = field(default_factory=set)  # NEW

    def add_property(self, name: str, value: str, hidden: bool = False) -> None:
        """Add or update a property with visibility control."""
        self.properties[name] = value
        if hidden:
            self.hidden_properties.add(name)
        else:
            self.hidden_properties.discard(name)

    def add_properties(self, props: Dict[str, str], hidden: bool = False) -> None:
        """Add or update multiple properties with same visibility."""
        self.properties.update(props)
        if hidden:
            self.hidden_properties.update(props.keys())
        else:
            for name in props.keys():
                self.hidden_properties.discard(name)
```

### Formatter Changes

File: `kicad_sch_api/parsers/elements/symbol_parser.py`

**Current state:**
- Lines 319-340: Emits custom properties using preserved S-expression
- Lines 325-333: Uses preserved format if available, creates new otherwise

**Required changes:**
- Check `hidden_properties` set when emitting properties
- Add/remove `(hide yes)` flag based on set membership
- Example:
```python
for prop_name, prop_value in symbol_data.get("properties", {}).items():
    if prop_name.startswith("__sexp_"):
        continue

    preserved_prop = symbol_data.get("properties", {}).get(f"__sexp_{prop_name}")
    is_hidden = prop_name in symbol_data.get("hidden_properties", set())  # NEW

    if preserved_prop:
        # Use preserved format but update hide flag
        prop = update_hide_flag(preserved_prop, is_hidden)  # NEW helper
    else:
        # Create new property with correct hide flag
        prop = self._create_property_with_positioning(
            prop_name, prop_value, pos, offset, "left", hide=is_hidden  # NEW
        )
    sexp.append(prop)
```

### MCP Tools Impact

No changes required - MCP tools use the same API and will automatically benefit from complete property preservation.

## Out of Scope

### Not Included in This PR

- Property position calculation/adjustment (handled by existing config system)
- Property rotation independent of component rotation
- Property font customization API (use `get_property_effects()` for advanced cases)
- Property validation (type checking, allowed values)
- BOM generation tools
- Property templates or defaults
- Bulk property operations across multiple components

### Future Enhancements

- Property inheritance from library symbols
- Property validation framework
- Property search/filter across schematic
- Property diff/comparison tools

## Acceptance Criteria

### Unit Tests (tests/unit/)

- [x] Test loading schematic with custom properties
- [x] Test `hidden_properties` set populated correctly
- [x] Test `add_property()` with hidden=True/False
- [x] Test `add_properties()` bulk operation
- [x] Test visibility state survives round-trip
- [x] Test property value modification preserves visibility
- [x] Test edge cases: empty values, special characters, missing properties

### Reference Tests (tests/reference_tests/)

- [x] Create reference schematic with custom properties
- [x] Test load → save → byte-perfect match (or semantic equivalence)
- [x] Test programmatically replicating reference schematic
- [x] Test all properties preserved with correct visibility

### Integration Tests

- [x] Test large schematic with many components and properties
- [x] Test mixed visibility states across multiple properties
- [x] Test backward compatibility with schematics without custom properties

### Format Preservation Validation

- [x] Load reference schematic
- [x] Save to temp file
- [x] Diff against original - verify properties section matches
- [x] Verify property count matches
- [x] Verify hide flags match

### Manual Validation (Interactive)

- [x] Open generated schematic in KiCAD
- [x] Verify custom properties appear in component properties dialog
- [x] Verify hidden properties have visibility icon (eye crossed out)
- [x] Verify visible properties show on schematic
- [x] Verify properties can be edited in KiCAD GUI

## Priority

**HIGH** - Essential for professional workflows requiring BOM generation, procurement metadata, and complete round-trip fidelity. This is a format preservation bug affecting real-world schematic compatibility.

## Related Issues

- #140 - This issue
- #139 - Pin UUIDs not preserved (similar format preservation issue)
- Round-trip testing framework (future work)

## Labels

`enhancement`, `high-priority`, `round-trip`, `format-preservation`, `component-properties`
