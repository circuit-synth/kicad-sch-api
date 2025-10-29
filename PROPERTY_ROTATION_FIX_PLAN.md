# Property Rotation Preservation - Implementation Plan

**Issue:** [#74](https://github.com/circuit-synth/kicad-sch-api/issues/74)
**Branch:** `fix/preserve-property-rotations`
**Priority:** High (breaks exact format preservation guarantee)

---

## Problem Statement

kicad-sch-api resets all component property rotations to 0° when loading and saving schematics, losing the original formatting set by KiCad. This violates the "exact format preservation" principle.

### Current Behavior

```python
# Before: Component at 90°, properties at 45° and 135°
sch = Schematic.load("test.kicad_sch")
sch.save("test.kicad_sch")
# After: Component at 90°, properties at 0° and 0°  ❌
```

---

## Root Cause Analysis

### Data Flow

```
LOADING:
1. File (S-expr) → Parser.parse()
2. Parser → SymbolParser._parse_symbol() → symbol_data dict
3. symbol_data dict → [CONVERSION POINT] → SchematicSymbol dataclass
4. SchematicSymbol stored in Schematic.components

SAVING:
1. SchematicSymbol dataclass → SymbolParser._symbol_to_sexp() → S-expression list
2. S-expression list → Formatter.format() → String
3. String → File
```

### Where Data is Lost

**Problem 1: Parsing drops property formatting**

File: `kicad_sch_api/parsers/elements/symbol_parser.py:95-103`

```python
def _parse_property(self, item: List[Any]) -> Optional[Dict[str, Any]]:
    """Parse a property definition."""
    if len(item) < 3:
        return None

    return {
        "name": item[1] if len(item) > 1 else None,
        "value": item[2] if len(item) > 2 else None,
    }
```

**Only extracts name and value, discards:**
- Position: `(at x y rotation)` ❌
- Effects: `(effects ...)` ❌
- Justification, hide flags, etc. ❌

**Problem 2: Writing recreates properties from scratch**

File: `kicad_sch_api/parsers/elements/symbol_parser.py:146-149`

```python
if symbol_data.get("reference"):
    ref_hide = is_power_symbol
    ref_prop = self._create_property_with_positioning(
        "Reference", symbol_data["reference"], pos, 0, "left", hide=ref_hide
    )
    sexp.append(ref_prop)
```

**Always creates new properties with default positioning, never reuses originals.**

---

## Solution Architecture

### Design Principles

1. **Exact Format Preservation**: Keep original S-expressions intact
2. **API Compatibility**: Don't break public API (SchematicSymbol dataclass)
3. **Value Mutation**: Allow property values to be updated via API
4. **Backward Compatible**: New components get sensible defaults

### Approach: Store Raw S-Expressions

Store the complete property S-expression alongside the parsed value, then reuse it when writing.

---

## Implementation Plan

### Phase 1: Store Property S-Expressions (Parsing)

**File:** `kicad_sch_api/parsers/elements/symbol_parser.py`

#### Step 1.1: Modify `_parse_symbol()` storage

Currently stores properties in `symbol_data["properties"]` dict.

**Change:** Store both value AND raw S-expression:

```python
# In _parse_symbol() around line 61-76:
elif element_type == "property":
    prop_data = self._parse_property(sub_item)
    if prop_data:
        prop_name = prop_data.get("name")

        # Store original S-expression for exact format preservation
        # Use special key prefix to avoid conflicts
        sexp_key = f"__sexp_{prop_name}"
        symbol_data["properties"][sexp_key] = sub_item  # ← NEW

        if prop_name == "Reference":
            symbol_data["reference"] = prop_data.get("value")
        elif prop_name == "Value":
            symbol_data["value"] = prop_data.get("value")
        elif prop_name == "Footprint":
            symbol_data["footprint"] = prop_data.get("value")
        else:
            # Custom properties
            prop_value = prop_data.get("value")
            if prop_value:
                prop_value = str(prop_value).replace('\\"', '"')
            symbol_data["properties"][prop_name] = prop_value
```

**Key Decision:** Use `__sexp_*` prefix for internal keys
- Stored in existing `properties` dict (no dataclass changes needed)
- Double underscore prefix signals "internal use only"
- Won't conflict with user properties (KiCad property names can't start with `_`)
- Survives dict → dataclass conversion

#### Step 1.2: Verify data flows to SchematicSymbol

The `properties` dict in `symbol_data` becomes `SchematicSymbol.properties`.

**Test:** After loading, check if `__sexp_Reference` exists:
```python
sch = Schematic.load("test.kicad_sch")
comp = sch.components[0]
assert "__sexp_Reference" in comp.properties  # Should pass
```

---

### Phase 2: Reuse S-Expressions (Writing)

**File:** `kicad_sch_api/parsers/elements/symbol_parser.py`

#### Step 2.1: Update `_symbol_to_sexp()` for Reference property

Currently (line 143-149):
```python
if symbol_data.get("reference"):
    ref_hide = is_power_symbol
    ref_prop = self._create_property_with_positioning(
        "Reference", symbol_data["reference"], pos, 0, "left", hide=ref_hide
    )
    sexp.append(ref_prop)
```

**Change to:**
```python
if symbol_data.get("reference"):
    # Check if we have preserved S-expression
    preserved_sexp = symbol_data.get("properties", {}).get("__sexp_Reference")

    if preserved_sexp:
        # Reuse original format (preserves rotation, position, effects)
        # But update the value in case it changed via API
        updated_sexp = list(preserved_sexp)  # Copy to avoid mutation
        if len(updated_sexp) >= 3:
            updated_sexp[2] = symbol_data["reference"]  # Update value
        sexp.append(updated_sexp)
    else:
        # No preserved format - create new (for newly added components)
        ref_hide = is_power_symbol
        ref_prop = self._create_property_with_positioning(
            "Reference", symbol_data["reference"], pos, 0, "left", hide=ref_hide
        )
        sexp.append(ref_prop)
```

#### Step 2.2: Apply same pattern to Value property

Around line 151-161, apply identical pattern.

#### Step 2.3: Apply same pattern to Footprint property

Around line 163-168, apply identical pattern.

#### Step 2.4: Filter out `__sexp_*` keys in custom properties loop

Around line 170-175:
```python
for prop_name, prop_value in symbol_data.get("properties", {}).items():
    # Skip internal S-expression preservation keys
    if prop_name.startswith("__sexp_"):  # ← NEW
        continue

    escaped_value = str(prop_value).replace('"', '\\"')
    prop = self._create_property_with_positioning(
        prop_name, escaped_value, pos, 3, "left", hide=True
    )
    sexp.append(prop)
```

---

### Phase 3: Testing

#### Test 3.1: Property Rotation Preservation

**File:** `tests/test_property_rotation_preservation.py` (new)

```python
def test_property_rotation_preserved_through_load_save():
    """Test that property rotations are preserved exactly."""
    import re
    from kicad_sch_api import Schematic
    from pathlib import Path

    # Create test schematic with rotated properties
    test_file = Path("test_rotation.kicad_sch")
    test_file.write_text(SCHEMATIC_WITH_ROTATIONS)

    # Extract original rotations
    content_before = test_file.read_text()
    ref_rot_before = extract_rotation(content_before, "Reference")
    val_rot_before = extract_rotation(content_before, "Value")

    # Load and save
    sch = Schematic.load(str(test_file))
    sch.save(str(test_file))

    # Extract rotations after save
    content_after = test_file.read_text()
    ref_rot_after = extract_rotation(content_after, "Reference")
    val_rot_after = extract_rotation(content_after, "Value")

    # Verify preservation
    assert ref_rot_before == ref_rot_after, f"Reference rotation changed: {ref_rot_before} → {ref_rot_after}"
    assert val_rot_before == val_rot_after, f"Value rotation changed: {val_rot_before} → {val_rot_after}"

    # Cleanup
    test_file.unlink()

def extract_rotation(content: str, prop_name: str) -> float:
    """Extract rotation value from property S-expression."""
    pattern = rf'\(property "{prop_name}"[^)]+\(at [\d.]+ [\d.]+ ([\d.]+)\)'
    match = re.search(pattern, content)
    return float(match.group(1)) if match else 0.0

SCHEMATIC_WITH_ROTATIONS = '''
(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0")
  (uuid "test-uuid")
  (paper "A4")
  (lib_symbols
    (symbol "Device:R" ...)
  )
  (symbol
    (lib_id "Device:R")
    (at 100 100 90)
    (uuid "comp-uuid")
    (property "Reference" "R1"
      (at 102 99 45)
      (effects (font (size 1.27 1.27)) (justify left))
    )
    (property "Value" "10k"
      (at 102 101 135)
      (effects (font (size 1.27 1.27)) (justify left))
    )
    (property "Footprint" ""
      (at 98.222 100 90)
      (effects (font (size 1.27 1.27)) (hide yes))
    )
  )
)
'''
```

#### Test 3.2: Value Updates Still Work

```python
def test_property_value_can_be_updated():
    """Test that property values can still be updated via API."""
    test_file = Path("test_update.kicad_sch")
    test_file.write_text(SCHEMATIC_WITH_ROTATIONS)

    # Load
    sch = Schematic.load(str(test_file))

    # Update value via API
    sch.components[0].value = "47k"

    # Save
    sch.save(str(test_file))

    # Verify: value changed, rotation preserved
    content = test_file.read_text()
    assert '"47k"' in content, "Value not updated"
    assert '(at 102 101 135)' in content, "Rotation not preserved"

    test_file.unlink()
```

#### Test 3.3: New Components Get Defaults

```python
def test_new_components_get_default_positioning():
    """Test that newly added components get sensible defaults."""
    sch = Schematic.create("test")

    # Add new component (no preserved S-expression)
    comp = sch.add_component("Device:R", reference="R1", value="10k", position=(100, 100))

    # Save
    test_file = Path("test_new.kicad_sch")
    sch.save(str(test_file))

    # Verify: properties created with default rotations
    content = test_file.read_text()
    assert 'property "Reference"' in content
    assert 'property "Value"' in content
    # Default rotation should be 0

    test_file.unlink()
```

---

### Phase 4: Documentation

#### Update CHANGELOG.md

```markdown
## [Unreleased]

### Fixed
- **CRITICAL:** Property rotations now preserved through load/save cycles (#74)
  - Previously, all property rotations were reset to 0° on save
  - This violated the "exact format preservation" principle
  - Now stores original property S-expressions and reuses them
  - Allows property values to be updated while preserving formatting
```

#### Update README if needed

If exact format preservation is mentioned, add:
- "Property formatting (position, rotation, effects) is preserved"

---

## Testing Checklist

Before merging:

- [ ] Test 3.1 passes: Property rotations preserved
- [ ] Test 3.2 passes: Values can still be updated
- [ ] Test 3.3 passes: New components get defaults
- [ ] All existing tests still pass
- [ ] Manual verification: Open schematic in KiCad, looks correct
- [ ] No performance regression (benchmarking if needed)

---

## Known Limitations

### Custom Properties

Currently, custom properties (non-Reference/Value/Footprint) are always recreated with defaults. This is acceptable because:
1. Custom properties are less commonly positioned/rotated
2. Extending the fix to custom properties follows the same pattern
3. Can be added in a follow-up if needed

### Future Enhancement

If we want to preserve ALL property formatting (including custom):

```python
# Instead of special-casing Reference/Value/Footprint:
# Store ALL properties' S-expressions
for prop_name, prop_sexp in preserved_properties.items():
    if prop_name.startswith("__sexp_"):
        # Use preserved S-expression
        sexp.append(prop_sexp)
```

---

## Rollout Plan

1. **Implement** (this branch)
2. **Test** thoroughly
3. **Merge** to main
4. **Release** as patch version (0.4.5)
5. **Notify** circuit-synth maintainers to update submodule

---

## Alternatives Considered

### Alternative 1: Modify SchematicSymbol dataclass

**Rejected** because:
- Breaking change to public API
- More complex implementation
- Harder to maintain

### Alternative 2: Store in separate hidden attribute

**Rejected** because:
- Requires dataclass modification anyway
- More complex data flow
- Current approach is simpler

### Alternative 3: Parse and reconstruct rotation correctly

**Rejected** because:
- Would need to track component rotation at property creation time
- Complex logic to calculate relative vs absolute rotations
- Doesn't preserve other formatting (effects, justification, etc.)
- Violates "exact format preservation" principle

---

## Success Criteria

✅ Property rotations preserved through load/save
✅ Property values can still be updated via API
✅ New components get sensible defaults
✅ No breaking changes to public API
✅ All existing tests pass
✅ Performance not significantly impacted

---

**Status:** Ready for implementation
**Estimated effort:** 2-3 hours (implementation + testing)
**Risk:** Low (non-breaking, well-scoped change)
