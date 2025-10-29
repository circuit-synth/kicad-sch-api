# Property Rotation Preservation - Implementation Plan V2

**Issue:** [#74](https://github.com/circuit-synth/kicad-sch-api/issues/74)
**Branch:** `fix/preserve-property-rotations`
**Priority:** High

---

## Philosophy Change

**OLD (rejected):** Store raw S-expressions to preserve exact format
**NEW (correct):** Parse complete property data, reconstruct correctly

**Why:**
- kicad-sch-api should be rock-solid at data ↔ S-expression conversion
- Raw S-expression preservation is a hack that avoids fixing the real issue
- We control both repos, so breaking changes are fine
- Proper parsing makes the codebase maintainable long-term

---

## Problem Statement

Properties have rich data (position, rotation, effects, justification) that we're currently ignoring.

### Current State (BROKEN)

**Parsing:**
```python
def _parse_property(self, item: List[Any]) -> Optional[Dict[str, Any]]:
    return {
        "name": item[1],
        "value": item[2],
    }
    # ❌ Ignores: position, rotation, effects, justification, hide flag
```

**Writing:**
```python
ref_prop = self._create_property_with_positioning(
    "Reference", symbol_data["reference"], pos, 0, "left", hide=ref_hide
)
# ❌ Always uses defaults, ignores parsed data
```

---

## Solution: Proper Property Data Structure

### Phase 1: Define Property Data Model

#### Option A: Dataclass (RECOMMENDED)

**File:** `kicad_sch_api/core/types.py` (new)

```python
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class PropertyEffects:
    """Font and formatting effects for a property."""
    font_size: tuple[float, float] = (1.27, 1.27)
    hide: bool = False
    justify: Optional[str] = None  # "left", "right", "center", None


@dataclass
class ComponentProperty:
    """
    A component property (Reference, Value, Footprint, or custom).

    Represents the complete property S-expression:
    (property "Name" "Value"
        (at x y rotation)
        (effects (font (size w h)) (justify dir) (hide yes))
    )
    """
    name: str
    value: str
    position: Optional[tuple[float, float]] = None  # (x, y) - None means use default
    rotation: float = 0.0  # degrees
    effects: PropertyEffects = field(default_factory=PropertyEffects)

    def to_sexp(self) -> List:
        """Convert to S-expression representation."""
        import sexpdata

        sexp = [
            sexpdata.Symbol("property"),
            self.name,
            self.value,
        ]

        # Add position
        if self.position:
            x, y = self.position
            # Format as int if whole number
            x = int(x) if x == int(x) else x
            y = int(y) if y == int(y) else y
            r = int(self.rotation) if self.rotation == int(self.rotation) else self.rotation
            sexp.append([sexpdata.Symbol("at"), x, y, r])

        # Add effects
        effects_sexp = [sexpdata.Symbol("effects")]
        effects_sexp.append([
            sexpdata.Symbol("font"),
            [sexpdata.Symbol("size"), *self.effects.font_size]
        ])

        if self.effects.justify:
            effects_sexp.append([
                sexpdata.Symbol("justify"),
                sexpdata.Symbol(self.effects.justify)
            ])

        if self.effects.hide:
            effects_sexp.append([sexpdata.Symbol("hide"), sexpdata.Symbol("yes")])

        sexp.append(effects_sexp)

        return sexp


@dataclass
class SchematicSymbol:
    """Component symbol in a schematic."""
    uuid: str
    lib_id: str
    position: Point
    rotation: float = 0.0
    unit: int = 1
    in_bom: bool = True
    on_board: bool = True

    # NEW: Store full property objects instead of just values
    reference_property: Optional[ComponentProperty] = None
    value_property: Optional[ComponentProperty] = None
    footprint_property: Optional[ComponentProperty] = None
    custom_properties: dict[str, ComponentProperty] = field(default_factory=dict)

    pins: List[SchematicPin] = field(default_factory=list)

    # Convenience accessors (for backward compatibility)
    @property
    def reference(self) -> str:
        return self.reference_property.value if self.reference_property else ""

    @reference.setter
    def reference(self, value: str):
        if self.reference_property:
            self.reference_property.value = value
        else:
            self.reference_property = ComponentProperty("Reference", value)

    @property
    def value(self) -> str:
        return self.value_property.value if self.value_property else ""

    @value.setter
    def value(self, value: str):
        if self.value_property:
            self.value_property.value = value
        else:
            self.value_property = ComponentProperty("Value", value)

    @property
    def footprint(self) -> Optional[str]:
        return self.footprint_property.value if self.footprint_property else None

    @footprint.setter
    def footprint(self, value: Optional[str]):
        if value is None:
            self.footprint_property = None
        elif self.footprint_property:
            self.footprint_property.value = value
        else:
            self.footprint_property = ComponentProperty("Footprint", value)

    @property
    def properties(self) -> dict[str, str]:
        """For backward compatibility - returns custom property values."""
        return {name: prop.value for name, prop in self.custom_properties.items()}
```

#### Option B: Dict-based (simpler, but less type-safe)

Keep current dict structure but add property data:

```python
symbol_data = {
    # ... existing fields ...
    "reference": "R1",
    "reference_property": {  # NEW
        "position": (x, y),
        "rotation": 45.0,
        "effects": {...}
    },
    # Similar for value_property, footprint_property
}
```

**RECOMMENDED: Option A** - More maintainable, better typing, clearer API

---

### Phase 2: Parse Complete Property Data

**File:** `kicad_sch_api/parsers/elements/symbol_parser.py`

#### Step 2.1: Enhance `_parse_property()`

```python
def _parse_property(self, item: List[Any]) -> Optional[ComponentProperty]:
    """
    Parse a complete property definition.

    Input S-expression:
    (property "Reference" "R1"
        (at 33.02 34.29 45)
        (effects (font (size 1.27 1.27)) (justify left))
    )
    """
    if len(item) < 3:
        return None

    prop = ComponentProperty(
        name=str(item[1]),
        value=str(item[2])
    )

    # Parse position and rotation
    for sub_item in item[3:]:
        if not isinstance(sub_item, list) or len(sub_item) == 0:
            continue

        element_type = str(sub_item[0]) if isinstance(sub_item[0], sexpdata.Symbol) else None

        if element_type == "at" and len(sub_item) >= 3:
            prop.position = (float(sub_item[1]), float(sub_item[2]))
            if len(sub_item) > 3:
                prop.rotation = float(sub_item[3])

        elif element_type == "effects":
            # Parse effects
            for effect_item in sub_item[1:]:
                if not isinstance(effect_item, list):
                    continue

                effect_type = str(effect_item[0]) if isinstance(effect_item[0], sexpdata.Symbol) else None

                if effect_type == "font" and len(effect_item) > 1:
                    for font_item in effect_item[1:]:
                        if isinstance(font_item, list) and len(font_item) > 1:
                            if str(font_item[0]) == "size" and len(font_item) >= 3:
                                prop.effects.font_size = (float(font_item[1]), float(font_item[2]))

                elif effect_type == "justify" and len(effect_item) > 1:
                    prop.effects.justify = str(effect_item[1])

                elif effect_type == "hide":
                    prop.effects.hide = True

    return prop
```

#### Step 2.2: Update `_parse_symbol()` to store ComponentProperty objects

```python
def _parse_symbol(self, item: List[Any]) -> Optional[Dict[str, Any]]:
    symbol_data = {
        "lib_id": None,
        "position": Point(0, 0),
        "rotation": 0,
        "uuid": None,

        # NEW: Store ComponentProperty objects
        "reference_property": None,
        "value_property": None,
        "footprint_property": None,
        "custom_properties": {},

        "pins": [],
        "in_bom": True,
        "on_board": True,
    }

    for sub_item in item[1:]:
        # ... existing parsing ...

        elif element_type == "property":
            prop = self._parse_property(sub_item)  # Returns ComponentProperty
            if prop:
                if prop.name == "Reference":
                    symbol_data["reference_property"] = prop
                elif prop.name == "Value":
                    symbol_data["value_property"] = prop
                elif prop.name == "Footprint":
                    symbol_data["footprint_property"] = prop
                else:
                    # Custom property
                    symbol_data["custom_properties"][prop.name] = prop

    return symbol_data
```

---

### Phase 3: Write Properties Correctly

**File:** `kicad_sch_api/parsers/elements/symbol_parser.py`

#### Step 3.1: Update `_symbol_to_sexp()` to use property objects

```python
def _symbol_to_sexp(self, symbol_data: Dict[str, Any], schematic_uuid: str = None) -> List[Any]:
    sexp = [sexpdata.Symbol("symbol")]

    # ... existing lib_id, position, rotation, uuid ...

    # Add properties using stored ComponentProperty objects

    # Reference
    ref_prop = symbol_data.get("reference_property")
    if ref_prop:
        sexp.append(ref_prop.to_sexp())
    elif symbol_data.get("reference"):  # Fallback for programmatically created
        # Create with defaults
        ref_prop = ComponentProperty(
            "Reference",
            symbol_data["reference"],
            effects=PropertyEffects(hide=("power:" in symbol_data.get("lib_id", "")))
        )
        sexp.append(ref_prop.to_sexp())

    # Value
    val_prop = symbol_data.get("value_property")
    if val_prop:
        sexp.append(val_prop.to_sexp())
    elif symbol_data.get("value"):  # Fallback
        val_prop = ComponentProperty("Value", symbol_data["value"])
        sexp.append(val_prop.to_sexp())

    # Footprint
    fp_prop = symbol_data.get("footprint_property")
    if fp_prop:
        sexp.append(fp_prop.to_sexp())
    elif symbol_data.get("footprint") is not None:  # Fallback
        fp_prop = ComponentProperty(
            "Footprint",
            symbol_data["footprint"],
            effects=PropertyEffects(hide=True)
        )
        sexp.append(fp_prop.to_sexp())

    # Custom properties
    for prop_name, prop in symbol_data.get("custom_properties", {}).items():
        sexp.append(prop.to_sexp())

    # ... rest of symbol (pins, instances, etc) ...

    return sexp
```

#### Step 3.2: Remove `_create_property_with_positioning()` (if no longer needed)

This function becomes obsolete if we're using `ComponentProperty.to_sexp()`.

---

### Phase 4: Update SchematicSymbol Dataclass

**File:** `kicad_sch_api/core/types.py`

Update the SchematicSymbol dataclass to use the new property structure (see Phase 1 Option A).

**BREAKING CHANGE:** This changes internal structure but maintains backward compatibility through property accessors.

---

### Phase 5: Update Components Collection

**File:** `kicad_sch_api/collections/components.py`

Ensure any code that accesses `component.reference`, `component.value`, etc. works through the property accessors.

---

### Phase 6: Testing

#### Test 6.1: Round-trip Property Data

```python
def test_property_data_roundtrip():
    """Test that property data survives load/save cycle."""
    from kicad_sch_api import Schematic

    # Create schematic with component at specific rotation
    test_sch = '''
    (kicad_sch ...
      (symbol
        (lib_id "Device:R")
        (at 100 100 90)
        (property "Reference" "R1"
          (at 102 99 45)
          (effects (font (size 1.27 1.27)) (justify left))
        )
        (property "Value" "10k"
          (at 102 101 135)
          (effects (font (size 1.27 1.27)) (justify right))
        )
      )
    )
    '''

    # Write test file
    Path("test.kicad_sch").write_text(test_sch)

    # Load
    sch = Schematic.load("test.kicad_sch")
    comp = sch.components[0]

    # Verify parsed data
    assert comp.reference == "R1"
    assert comp.reference_property.position == (102, 99)
    assert comp.reference_property.rotation == 45.0
    assert comp.reference_property.effects.justify == "left"

    assert comp.value == "10k"
    assert comp.value_property.rotation == 135.0
    assert comp.value_property.effects.justify == "right"

    # Save
    sch.save("test.kicad_sch")

    # Reload and verify
    sch2 = Schematic.load("test.kicad_sch")
    comp2 = sch2.components[0]

    assert comp2.reference_property.rotation == 45.0  # ← CRITICAL
    assert comp2.value_property.rotation == 135.0  # ← CRITICAL
```

#### Test 6.2: Value Updates Work

```python
def test_property_value_update():
    """Test that updating values preserves formatting."""
    # ... load schematic ...

    # Update value
    comp.value = "47k"

    # Save and reload
    sch.save("test.kicad_sch")
    sch2 = Schematic.load("test.kicad_sch")

    # Value changed, rotation preserved
    assert sch2.components[0].value == "47k"
    assert sch2.components[0].value_property.rotation == 135.0
```

#### Test 6.3: Programmatic Component Creation

```python
def test_new_component_creation():
    """Test creating components programmatically."""
    sch = Schematic.create("test")

    # Add component without property formatting
    comp = sch.add_component("Device:R", reference="R1", value="10k")

    # Should have default property objects
    assert comp.reference_property is not None
    assert comp.reference_property.rotation == 0.0  # Default
```

---

### Phase 7: Migration Path

#### Update Existing Tests

Find all tests that access properties and ensure they work with new structure.

```bash
# Find property access patterns
grep -r "\.reference\|\.value\|\.footprint" tests/
```

Most should work through backward-compatible accessors, but verify.

#### Update circuit-synth

Once this is merged:
1. Update circuit-synth's kicad-sch-api submodule
2. Update any code that directly accesses property data
3. Test bidirectional test suite

---

## Implementation Order

1. ✅ **Define ComponentProperty and PropertyEffects** (types.py)
2. ✅ **Update _parse_property()** to parse complete data
3. ✅ **Update _parse_symbol()** to store ComponentProperty objects
4. ✅ **Add ComponentProperty.to_sexp()** method
5. ✅ **Update _symbol_to_sexp()** to use property objects
6. ✅ **Update SchematicSymbol dataclass** with property accessors
7. ✅ **Write tests** for roundtrip, updates, and creation
8. ✅ **Run existing tests**, fix any breaks
9. ✅ **Manual verification** in KiCad

---

## Breaking Changes

**For external users (if any):**
- `SchematicSymbol` internal structure changes
- But public API (`.reference`, `.value`, `.footprint`) remains compatible

**For us (circuit-synth):**
- May need to update any code that accesses `component._data` directly
- Submodule pointer update required

---

## Success Criteria

✅ Property rotations preserved through load/save
✅ Property positions preserved
✅ Property effects (font, justify, hide) preserved
✅ Property values can be updated via API
✅ New components get sensible defaults
✅ All existing tests pass (or are updated)
✅ Type hints complete and accurate

---

## Long-term Benefits

1. **Proper architecture**: Data model matches S-expression structure
2. **Type safety**: PropertyEffects, ComponentProperty are typed
3. **Maintainability**: Clear separation of concerns
4. **Extensibility**: Easy to add new property attributes
5. **Debugging**: Easier to inspect parsed data

---

**Status:** Ready for implementation (correct approach)
**Estimated effort:** 4-6 hours (more changes, but cleaner)
**Risk:** Medium (breaking changes, but we control usage)
